#!/usr/bin/env python3
"""Fetch CURRENT NSW MPs and MLCs from Parliament of NSW downloadable lists.

Standard library only. Writes data/nsw_official.json and prints a report.

Primary files (filenames may change; script discovers from the downloadables
page when reachable, else uses known NOV 2026 paths):
  LA XLSX / LC CSV under
  https://www.parliament.nsw.gov.au/_media/documents/members-and-electorates/downloadable-lists/

Profile URLs need a numeric memberId from the all-members list page
  …/members-and-electorates/members-and-ministers/all-members
  pattern: …/members-details?memberId={id}

Cloudflare often blocks unattended fetches. Pass --from-dir with saved LA/LC
files and --id-map with a TSV (memberId, name, house, electorate, profile_url)
from a browser-cleared session when needed.

Facts only — no addresses, emails, phones, portraits, or bios.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import guards

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "nsw_official.json"

USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
SOURCE = "Parliament of New South Wales"
SOURCE_URL = "https://www.parliament.nsw.gov.au/members-and-electorates/members-and-ministers/downloadable-lists"
MEDIA_BASE = (
    "https://www.parliament.nsw.gov.au/_media/documents/"
    "members-and-electorates/downloadable-lists/"
)
# Filenames observed 2026-11-24; may roll with new releases.
DEFAULT_LA = "la-members-July-2026.xlsx"
DEFAULT_LC = "lc-members-nov-26.csv"
PROFILE_TMPL = (
    "https://www.parliament.nsw.gov.au/members-and-electorates/"
    "members-and-ministers/members-details?memberId={member_id}"
)
EXPECTED = {"Assembly": 93, "Council": 42}
REQUEST_DELAY_SEC = 1.0

NS_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NS_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
NS_ODR = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def http_get(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
    )
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = guards.read_checked(resp, url)
                ctype = (resp.headers.get("content-type") or "").lower()
                if b"Just a moment" in body[:800] or "text/html" in ctype and b"cf-" in body[:2000].lower():
                    raise RuntimeError(
                        f"Cloudflare challenge HTML for {url}. "
                        "Re-run with --from-dir after a browser-cleared download."
                    )
                return body
        except (urllib.error.URLError, TimeoutError, RuntimeError) as err:
            last_err = err
            print(f"  attempt {attempt}/3 failed: {err}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after 3 attempts: {last_err}")


def read_xlsx_sheet(data: bytes) -> list[list[str]]:
    """Read the first worksheet of an XLSX (stdlib zip+xml)."""
    with zipfile.ZipFile(BytesIO(data)) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(guards.read_zip_member(zf, "xl/sharedStrings.xml"))
            for si in root.findall(f"{NS_MAIN}si"):
                texts = [t.text or "" for t in si.iter(f"{NS_MAIN}t")]
                shared.append("".join(texts))

        sheet_path = "xl/worksheets/sheet1.xml"
        if sheet_path not in zf.namelist():
            # resolve first worksheet via workbook
            wb = ET.fromstring(guards.read_zip_member(zf, "xl/workbook.xml"))
            sheets = wb.find(f"{NS_MAIN}sheets")
            if sheets is None or not list(sheets):
                raise ValueError("XLSX has no sheets")
            rid = list(sheets)[0].attrib.get(f"{NS_ODR}id")
            rels = ET.fromstring(guards.read_zip_member(zf, "xl/_rels/workbook.xml.rels"))
            target = None
            for rel in rels:
                if rel.attrib.get("Id") == rid:
                    target = rel.attrib.get("Target")
                    break
            if not target:
                raise ValueError("could not resolve worksheet path")
            sheet_path = "xl/" + target.lstrip("/")

        root = ET.fromstring(guards.read_zip_member(zf, sheet_path))
        rows_out: list[list[str]] = []
        for row in root.iter(f"{NS_MAIN}row"):
            cells: dict[int, str] = {}
            for c in row.findall(f"{NS_MAIN}c"):
                ref = c.attrib.get("r", "A1")
                col = 0
                for ch in ref:
                    if ch.isalpha():
                        col = col * 26 + (ord(ch.upper()) - ord("A") + 1)
                    else:
                        break
                col -= 1
                v = c.find(f"{NS_MAIN}v")
                raw = v.text if v is not None and v.text is not None else ""
                if c.attrib.get("t") == "s":
                    try:
                        raw = shared[int(raw)]
                    except (ValueError, IndexError):
                        pass
                cells[col] = raw
            if not cells:
                continue
            width = max(cells) + 1
            rows_out.append([cells.get(i, "") for i in range(width)])
        return rows_out


def rows_to_dicts(grid: list[list[str]]) -> list[dict]:
    if not grid:
        return []
    header = [h.strip() for h in grid[0]]
    out = []
    for row in grid[1:]:
        if not any((c or "").strip() for c in row):
            continue
        rec = {}
        for i, key in enumerate(header):
            if not key:
                continue
            rec[key] = (row[i] if i < len(row) else "") or ""
        out.append(rec)
    return out


def read_csv_bytes(data: bytes) -> list[dict]:
    text = data.decode("utf-8-sig")
    return list(csv.DictReader(text.splitlines()))


def load_id_map(path: Path) -> list[dict]:
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig"), delimiter="\t"))
    if not rows:
        raise ValueError(f"empty id map: {path}")
    needed = {"memberId", "name", "house"}
    if not needed <= set(rows[0].keys()):
        # also accept comma CSV
        rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    if not needed <= set(rows[0].keys()):
        raise ValueError(f"id map needs columns {sorted(needed)}")
    return rows


def previous_id_map() -> dict[tuple[str, str], str]:
    """(folded_name, chamber) -> member_id from last nsw_official.json."""
    if not OUT.exists():
        return {}
    try:
        data = json.loads(OUT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    out: dict[tuple[str, str], str] = {}
    for m in data.get("members") or []:
        mid = (m.get("member_id") or "").strip()
        name = (m.get("name") or "").strip()
        chamber = (m.get("chamber") or "").strip()
        if mid and name and chamber:
            out[(fold(name), chamber)] = mid
    return out


def fold(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").casefold())


def display_name(row: dict) -> str | None:
    given = (row.get("NAME") or "").strip()
    family = (row.get("SURNAME") or "").strip()
    if given and family:
        return f"{given} {family}"
    return given or family or None


def match_member_id(
    name: str,
    chamber: str,
    electorate: str | None,
    id_rows: list[dict],
    prev: dict[tuple[str, str], str],
) -> str | None:
    house = "LA" if chamber == "Assembly" else "LC"
    candidates = [r for r in id_rows if (r.get("house") or "").strip() == house]
    fn = fold(name)
    exact = [r for r in candidates if fold(r.get("name") or "") == fn]
    if chamber == "Assembly" and electorate:
        fe = fold(electorate)
        by_seat = [r for r in exact if fold(r.get("electorate") or "") == fe]
        if len(by_seat) == 1:
            return (by_seat[0].get("memberId") or "").strip() or None
        if not by_seat:
            by_seat = [
                r
                for r in candidates
                if fold(r.get("electorate") or "") == fe and fold(r.get("name") or "") == fn
            ]
            if len(by_seat) == 1:
                return (by_seat[0].get("memberId") or "").strip() or None
    if len(exact) == 1:
        return (exact[0].get("memberId") or "").strip() or None
    return prev.get((fn, chamber))


def parse_row(
    raw: dict,
    chamber: str,
    id_rows: list[dict],
    prev: dict[tuple[str, str], str],
) -> dict:
    name = display_name(raw)
    party = (raw.get("PARTY") or "").strip() or None
    electorate = (raw.get("ELECTORATE") or "").strip() or None
    if chamber == "Council":
        electorate = None
        region = "New South Wales"
    else:
        region = None
    mid = match_member_id(name or "", chamber, electorate, id_rows, prev) if name else None
    return {
        "member_id": mid,
        "name": name,
        "chamber": chamber,
        "party": party,
        "electorate": electorate,
        "region": region,
        "url": PROFILE_TMPL.format(member_id=mid) if mid else None,
    }


def report(members: list[dict]) -> bool:
    print("=== NSW official members fetch report ===")
    print(f"Total records: {len(members)}")
    counts_ok = True
    for chamber, expected in EXPECTED.items():
        count = sum(1 for m in members if m["chamber"] == chamber)
        flag = "OK" if count == expected else f"CHECK (expected {expected})"
        if count != expected:
            counts_ok = False
        print(f"  {chamber}: {count}  [{flag}]")

    party_counts = Counter(m.get("party") or "(missing)" for m in members)
    print("Counts per party:")
    for party, n in sorted(party_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {party}: {n}")

    missing_url = [m for m in members if not m.get("url")]
    print(f"Members missing profile URL / memberId: {len(missing_url)}")
    for m in missing_url[:15]:
        print(f"  {m.get('chamber')} {m.get('name')!r}")

    incomplete = []
    for m in members:
        miss = [k for k in ("name", "chamber", "party") if not m.get(k)]
        if m.get("chamber") == "Assembly" and not m.get("electorate"):
            miss.append("electorate")
        if m.get("chamber") == "Council" and not m.get("region"):
            miss.append("region")
        if miss:
            incomplete.append((m, miss))
    print(f"Members missing required fields: {len(incomplete)}")
    for m, fields in incomplete[:20]:
        print(f"  {m.get('name')!r}: missing {', '.join(fields)}")

    if members:
        print("Sample (first 5):")
        for m in members[:5]:
            seat = m.get("electorate") or m.get("region") or "?"
            print(f"  {m.get('chamber') or '?':8} {m.get('name')} | {m.get('party')} | {seat}")
            print(f"           {m.get('url')}")
    return counts_ok and not incomplete and not missing_url


def load_sources(args: argparse.Namespace) -> tuple[bytes, bytes, list[dict], dict]:
    prev = previous_id_map()
    id_rows: list[dict] = []
    if args.id_map:
        id_rows = load_id_map(Path(args.id_map))
        print(f"Loaded id map: {len(id_rows)} rows from {args.id_map}")
    elif prev:
        print(f"Reusing {len(prev)} memberIds from existing {OUT.relative_to(ROOT)}")

    if args.from_dir:
        d = Path(args.from_dir)
        la_path = next(d.glob("la-members*.xlsx"), None) or next(d.glob("*LA*.xlsx"), None)
        lc_path = next(d.glob("lc-members*.csv"), None) or next(
            d.glob("ContactSpreadsheetLC.csv"), None
        )
        if not la_path or not lc_path:
            raise SystemExit(f"ERROR: could not find LA xlsx / LC csv under {d}")
        print(f"Reading LA from {la_path.name}, LC from {lc_path.name}")
        la_bytes = la_path.read_bytes()
        lc_bytes = lc_path.read_bytes()
        id_guess = d / "members-id-map.tsv"
        if not id_rows and id_guess.exists():
            id_rows = load_id_map(id_guess)
            print(f"Loaded id map: {len(id_rows)} rows from {id_guess}")
        return la_bytes, lc_bytes, id_rows, prev

    print(f"Fetching LA {DEFAULT_LA}…")
    time.sleep(REQUEST_DELAY_SEC)
    la_bytes = http_get(MEDIA_BASE + DEFAULT_LA)
    print(f"Fetching LC {DEFAULT_LC}…")
    time.sleep(REQUEST_DELAY_SEC)
    lc_bytes = http_get(MEDIA_BASE + DEFAULT_LC)
    return la_bytes, lc_bytes, id_rows, prev


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--from-dir",
        help="directory with LA xlsx + LC csv (+ optional members-id-map.tsv)",
    )
    ap.add_argument(
        "--id-map",
        help="TSV/CSV with memberId,name,house,electorate,profile_url",
    )
    args = ap.parse_args()

    try:
        la_bytes, lc_bytes, id_rows, prev = load_sources(args)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if la_bytes[:2] != b"PK":
        print("ERROR: LA file is not an XLSX (zip). Cloudflare HTML?", file=sys.stderr)
        return 1

    la_rows = rows_to_dicts(read_xlsx_sheet(la_bytes))
    lc_rows = read_csv_bytes(lc_bytes)
    print(f"Parsed LA rows={len(la_rows)}, LC rows={len(lc_rows)}")

    members = [parse_row(r, "Assembly", id_rows, prev) for r in la_rows]
    members += [parse_row(r, "Council", id_rows, prev) for r in lc_rows]
    members.sort(
        key=lambda m: (
            0 if m.get("chamber") == "Assembly" else 1,
            (m.get("name") or "").lower(),
        )
    )
    ok = report(members)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "la_file": DEFAULT_LA,
        "lc_file": DEFAULT_LC,
        "expected_counts": EXPECTED,
        "credit": "© State of New South Wales through the Parliament of New South Wales",
        "members": members,
    }
    try:
        guards.assert_profile_urls(members, guards.HOSTS["nsw"])
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")

    if not members:
        print("ERROR: fetch returned zero members.", file=sys.stderr)
        return 1
    if not ok:
        print("WARNING: counts or required fields incomplete.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
