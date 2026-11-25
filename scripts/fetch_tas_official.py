#!/usr/bin/env python3
"""Fetch CURRENT Tasmania MHAs and MLCs (stdlib only).

Writes data/tas_official.json and prints a report.

Primary sources (Parliament of Tasmania member lists + profile pages):
  Assembly: https://www.parliament.tas.gov.au/house-of-assembly/currentmembers
  Council:  https://www.parliament.tas.gov.au/legislative-council/members
  Profiles:
    HA: …/house-of-assembly/currentmembers/{slug}
    LC: …/legislative-council/members/{slug}

Cloudflare often returns HTTP 403 / challenge HTML for unattended fetches.
This script uses a Chrome-compatible UA that still identifies PolicyDeskAU.
Pass --from-dir with saved list + profile HTML when live fetch is blocked.

Expected: House of Assembly 35 (7 members × 5 multi-member divisions);
Legislative Council 15 (one member per division).

Party labels are taken from each profile’s “{party} member for {seat}” line.
Casey Hiscutt’s profile omits a party; the official LC mail-merge workbook
lists IND → Independent (documented fallback, not a guess).
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "tas_official.json"

USER_AGENT = (
    "Mozilla/5.0 (compatible; PolicyDeskAU/1.0; +https://policydesk.au) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SOURCE = "Parliament of Tasmania"
SOURCE_URL = "https://www.parliament.tas.gov.au/"
ASSEMBLY_URL = "https://www.parliament.tas.gov.au/house-of-assembly/currentmembers"
COUNCIL_URL = "https://www.parliament.tas.gov.au/legislative-council/members"
EXPECTED = {"Assembly": 35, "Council": 15}
REQUEST_DELAY_SEC = 1.0

# Profile adjective → full party name + short code (facts mapped from printed label).
PARTY_FULL = {
    "Liberal": ("Liberal Party", "LIB"),
    "Labor": ("Australian Labor Party", "ALP"),
    "Green": ("Tasmanian Greens", "GRN"),
    "Greens": ("Tasmanian Greens", "GRN"),
    "Independent": ("Independent", "IND"),
    "Shooters, Fishers and Farmers Party": (
        "Shooters, Fishers and Farmers Party",
        "SFF",
    ),
    "IND": ("Independent", "IND"),
    "ALP": ("Australian Labor Party", "ALP"),
    "LIB": ("Liberal Party", "LIB"),
}

HONORIFIC = re.compile(
    r"^(?:The\s+Honourable|The\s+Hon\.?|Hon(?:ourable)?\.?)\s+",
    re.I,
)
TRAILING_TITLE = re.compile(r"\s+(?:MP|MLC)\s*$", re.I)
MEMBER_FOR = re.compile(
    r"(?:^|>)\s*([A-Za-z][^<\n]*?)\s+member for\s+(?:<a[^>]*>)?([^<]+?)(?:</a>)?\s*<",
    re.I,
)
MEMBER_FOR_BARE = re.compile(
    r"(?:^|>)\s*member for\s+(?:<a[^>]*>)?([^<]+?)(?:</a>)?\s*<",
    re.I,
)


def http_get(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
    )
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = resp.read()
                head = body[:900].lower()
                if b"just a moment" in head or b"cf-mitigated" in head or b"challenge-platform" in head:
                    raise RuntimeError(
                        f"Cloudflare challenge HTML for {url}. "
                        "Re-run with --from-dir after a browser-cleared save."
                    )
                return body
        except (urllib.error.URLError, TimeoutError, RuntimeError) as err:
            last_err = err
            print(f"  attempt {attempt}/3 failed: {err}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after 3 attempts: {last_err}")


def strip_tags(raw: str) -> str:
    text = html_lib.unescape(re.sub(r"<[^>]+>", " ", raw or ""))
    return re.sub(r"\s+", " ", text).strip()


def display_name(raw: str) -> str:
    name = HONORIFIC.sub("", strip_tags(raw))
    name = TRAILING_TITLE.sub("", name)
    return re.sub(r"\s+", " ", name).strip()


def list_links(html: str, chamber: str) -> list[tuple[str, str]]:
    if chamber == "Assembly":
        pat = re.compile(
            r'<a href="(https://www\.parliament\.tas\.gov\.au/house-of-assembly/'
            r'currentmembers/[^"/]+)"[^>]*>(.*?)</a>',
            re.I | re.S,
        )
    else:
        pat = re.compile(
            r'<a href="(https://www\.parliament\.tas\.gov\.au/legislative-council/'
            r'members/[^"/]+)"[^>]*>(.*?)</a>',
            re.I | re.S,
        )
    by_url: dict[str, str] = {}
    for m in pat.finditer(html):
        url = m.group(1).split("?")[0].rstrip("/")
        name = display_name(m.group(2))
        if not name or name.lower() in {"members", "home", "print"}:
            continue
        # Same profile can appear twice with a longer legal name and a shorter
        # display name (e.g. “Kerry John Vincent” vs “Kerry Vincent”). Prefer
        # the shorter list label when both point at the same URL.
        prev = by_url.get(url)
        if prev is None or len(name) < len(prev):
            by_url[url] = name
    return list(by_url.items())


def parse_profile(html: str, chamber: str, list_name: str, url: str) -> dict:
    party_label = None
    seat = None
    m = MEMBER_FOR.search(html)
    if m:
        party_label = strip_tags(m.group(1))
        seat = strip_tags(m.group(2))
    else:
        m2 = MEMBER_FOR_BARE.search(html)
        if m2:
            seat = strip_tags(m2.group(1))
    if not seat:
        raise ValueError(f"{url}: missing electorate/division on profile")

    party = None
    party_short = None
    party_source = None
    if party_label:
        if party_label not in PARTY_FULL:
            raise ValueError(f"{url}: unknown party label {party_label!r}")
        party, party_short = PARTY_FULL[party_label]
        party_source = "profile"
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    return {
        "member_id": slug,
        "name": list_name,
        "chamber": chamber,
        "party": party,
        "party_short": party_short,
        "party_label_raw": party_label,
        "party_source": party_source,
        "electorate": seat if chamber == "Assembly" else None,
        "region": seat if chamber == "Council" else None,
        "url": url,
    }


def read_xlsx_rows(data: bytes) -> list[dict[str, str]]:
    from io import BytesIO

    with zipfile.ZipFile(BytesIO(data)) as zf:
        root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        strings: list[str] = []
        for si in root.findall("m:si", ns):
            texts = [
                t.text or ""
                for t in si.iter(
                    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
                )
            ]
            strings.append("".join(texts))
        sheet = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))
        rows: list[dict[str, str]] = []
        for row in sheet.findall("m:sheetData/m:row", ns):
            cells: dict[str, str] = {}
            for c in row.findall("m:c", ns):
                ref = c.get("r") or ""
                col = "".join(ch for ch in ref if ch.isalpha())
                v = c.find("m:v", ns)
                if v is None:
                    continue
                val = v.text or ""
                if c.get("t") == "s":
                    val = strings[int(val)]
                cells[col] = val
            if cells:
                rows.append(cells)
        return rows


def apply_lc_mail_merge_party(members: list[dict], xlsx_path: Path) -> None:
    """Fill null Council parties from the official LC mail-merge party column."""
    rows = read_xlsx_rows(xlsx_path.read_bytes())
    if not rows:
        return
    # Header row uses column K = party (title/first/last/…/party).
    by_last: dict[str, str] = {}
    for row in rows[1:]:
        last = (row.get("C") or "").replace(" MLC", "").strip()
        party_code = (row.get("K") or "").strip()
        if last and party_code:
            by_last[last.casefold()] = party_code
    for m in members:
        if m["chamber"] != "Council" or m.get("party"):
            continue
        # Match on last token of display name (e.g. Hiscutt).
        last = m["name"].split()[-1]
        code = by_last.get(last.casefold())
        if not code:
            continue
        if code not in PARTY_FULL:
            raise ValueError(f"LC mail-merge unknown party {code!r} for {m['name']}")
        party, short = PARTY_FULL[code]
        m["party"] = party
        m["party_short"] = short
        m["party_label_raw"] = code
        m["party_source"] = "lc_mail_merge_xlsx"


def load_text(args: argparse.Namespace, name: str, url: str) -> str:
    if args.from_dir:
        path = Path(args.from_dir) / name
        if not path.exists():
            raise FileNotFoundError(f"missing {path}")
        print(f"Reading {path}")
        return path.read_text(encoding="utf-8", errors="replace")
    print(f"Fetching {url}…")
    time.sleep(REQUEST_DELAY_SEC)
    return http_get(url).decode("utf-8", "replace")


def profile_filename(chamber: str, url: str) -> str:
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    prefix = "member-ha-" if chamber == "Assembly" else "member-lc-"
    return f"{prefix}{slug}.html"


def load_profile(args: argparse.Namespace, chamber: str, url: str) -> str:
    if args.from_dir:
        path = Path(args.from_dir) / profile_filename(chamber, url)
        if not path.exists():
            # Some list slugs differ from filename (e.g. jenna-butler vs Jen Butler).
            alt = list(Path(args.from_dir).glob(f"member-{'ha' if chamber == 'Assembly' else 'lc'}-*.html"))
            raise FileNotFoundError(
                f"missing {path} (have {len(alt)} profile HTML files in --from-dir)"
            )
        return path.read_text(encoding="utf-8", errors="replace")
    time.sleep(REQUEST_DELAY_SEC)
    return http_get(url).decode("utf-8", "replace")


def report(members: list[dict]) -> bool:
    print("=== TAS official members fetch report ===")
    print(f"Total records: {len(members)}")
    by_ch = Counter(m.get("chamber") for m in members)
    ok = True
    for chamber, expected in EXPECTED.items():
        n = by_ch.get(chamber, 0)
        flag = "OK" if n == expected else f"CHECK (expected {expected})"
        if n != expected:
            ok = False
        print(f"  {chamber}: {n}  [{flag}]")

    party_counts = Counter(m.get("party") or "(missing)" for m in members)
    print("Counts per party:")
    for party, n in sorted(party_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {party}: {n}")

    la = [m for m in members if m["chamber"] == "Assembly"]
    seats = Counter(m.get("electorate") for m in la)
    print(f"Assembly divisions: {sorted(seats)}")
    for seat, n in sorted(seats.items()):
        if n != 7:
            ok = False
            print(f"ERROR: Assembly {seat} has {n} members (expected 7)")
    lc_regions = sorted({m.get("region") for m in members if m["chamber"] == "Council"})
    print(f"Council divisions ({len(lc_regions)}): {lc_regions}")
    if len(lc_regions) != 15:
        ok = False
        print("ERROR: expected 15 unique Council divisions")

    missing_url = [m for m in members if not m.get("url")]
    print(f"Members missing profile URL: {len(missing_url)}")
    incomplete = []
    for m in members:
        need = ["name", "chamber", "party", "url"]
        if m["chamber"] == "Assembly":
            need.append("electorate")
        else:
            need.append("region")
        miss = [k for k in need if not m.get(k)]
        if miss:
            incomplete.append((m, miss))
    print(f"Members missing required fields: {len(incomplete)}")
    for m, fields in incomplete[:20]:
        print(f"  {m.get('name')!r}: missing {', '.join(fields)}")
        ok = False

    if members:
        print("Sample (first 5):")
        for m in members[:5]:
            seat = m.get("electorate") or m.get("region")
            print(
                f"  {m.get('chamber')} {m.get('name')} | {m.get('party')} | {seat}"
            )
            print(f"           {m.get('url')}")
    return ok and not incomplete and not missing_url


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--from-dir",
        help=(
            "directory with house-currentmembers.html, council-members.html, "
            "member-ha-*.html, member-lc-*.html "
            "(and optional LC-Mail-Merge*.xlsx for null-party fallback)"
        ),
    )
    args = ap.parse_args()

    try:
        assembly_html = load_text(args, "house-currentmembers.html", ASSEMBLY_URL)
        council_html = load_text(args, "council-members.html", COUNCIL_URL)
        assembly_links = list_links(assembly_html, "Assembly")
        council_links = list_links(council_html, "Council")
        if len(assembly_links) != EXPECTED["Assembly"]:
            print(
                f"WARNING: Assembly list links {len(assembly_links)} "
                f"!= {EXPECTED['Assembly']}",
                file=sys.stderr,
            )
        if len(council_links) != EXPECTED["Council"]:
            print(
                f"WARNING: Council list links {len(council_links)} "
                f"!= {EXPECTED['Council']}",
                file=sys.stderr,
            )

        members: list[dict] = []
        for url, name in assembly_links:
            html = load_profile(args, "Assembly", url)
            members.append(parse_profile(html, "Assembly", name, url))
        for url, name in council_links:
            html = load_profile(args, "Council", url)
            members.append(parse_profile(html, "Council", name, url))

        if args.from_dir:
            merges = sorted(Path(args.from_dir).glob("LC-Mail-Merge*.xlsx"))
            if merges:
                print(f"Applying party fallback from {merges[0].name}")
                apply_lc_mail_merge_party(members, merges[0])
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    members.sort(key=lambda m: ((m.get("name") or "").lower(), m.get("chamber") or ""))
    ok = report(members)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "assembly_list_url": ASSEMBLY_URL,
        "council_list_url": COUNCIL_URL,
        "expected_counts": EXPECTED,
        "credit": "Parliament of Tasmania",
        "notes": (
            "Bicameral. House of Assembly: 35 members in 5 multi-member divisions "
            "(Bass, Braddon, Clark, Franklin, Lyons), 7 each. Legislative Council: "
            "15 single-member divisions. Party from each profile’s "
            "“{party} member for {seat}” line; Casey Hiscutt party from the official "
            "LC mail-merge workbook (IND) when the profile omits it. Addresses, "
            "emails, phones and biographies are not stored."
        ),
        "members": members,
    }
    OUT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
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
