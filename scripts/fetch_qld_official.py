#!/usr/bin/env python3
"""Fetch CURRENT Queensland Legislative Assembly members (unicameral).

Standard library only. Writes data/qld_official.json and prints a report.

Primary source: Parliament of Queensland Member List HTML
  https://www.parliament.qld.gov.au/Members/Current-Members/Member-List
  Profile URLs: …/Member-Details?id={member_id}

Cross-check (facts only, no addresses): Comprehensive Members List PDF
  https://documents.parliament.qld.gov.au/Members/mailingLists/MEMLIST.pdf

PolicyDeskAU/1.0 often receives HTTP 403 from parliament.qld.gov.au (bot
protection). This script uses a plain browser User-Agent for the HTML list.
robots.txt on www.parliament.qld.gov.au returned HTTP 404 on 2026-11-24.

Facts only — no addresses, emails, phones, portraits, or bios.
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
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "qld_official.json"

USER_AGENT = (
    "Mozilla/5.0 (compatible; PolicyDeskAU/1.0; +https://policydesk.au) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SOURCE = "Parliament of Queensland"
SOURCE_URL = "https://www.parliament.qld.gov.au/Members/Current-Members/Member-List"
MEMBER_LIST_URL = SOURCE_URL
PROFILE_TMPL = (
    "https://www.parliament.qld.gov.au/Members/Current-Members/"
    "Member-List/Member-Details?id={member_id}"
)
MEMLIST_PDF = (
    "https://documents.parliament.qld.gov.au/Members/mailingLists/MEMLIST.pdf"
)
EXPECTED = 93
REQUEST_DELAY_SEC = 1.0

PARTY_FULL = {
    "ALP": "Australian Labor Party",
    "LNP": "Liberal National Party",
    "GRN": "Queensland Greens",
    "IND": "Independent",
    "KAP": "Katter's Australian Party",
}

HONORIFIC = re.compile(
    r"^(?:Hon(?:ourable)?|Mr|Ms|Mrs|Miss|Dr|Prof(?:essor)?)\s+",
    re.I,
)
PREFERRED = re.compile(r"^(.+?)\s+\(([^)]+)\)\s+(.+)$")


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
                if b"Just a moment" in body[:800]:
                    raise RuntimeError(
                        f"Cloudflare challenge HTML for {url}. "
                        "Re-run with --from-html after a browser-cleared save."
                    )
                return body
        except (urllib.error.URLError, TimeoutError, RuntimeError) as err:
            last_err = err
            print(f"  attempt {attempt}/3 failed: {err}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after 3 attempts: {last_err}")


def fold(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").casefold())


def display_name(raw: str) -> str:
    """Strip honorifics; use preferred name in parentheses when present."""
    name = HONORIFIC.sub("", (raw or "").strip())
    m = PREFERRED.match(name)
    if m:
        return f"{m.group(2)} {m.group(3)}".strip()
    return name


def parse_member_list(html: str) -> list[dict]:
    ids = sorted(set(re.findall(r"Member-Details\?id=(\d+)", html)))
    if not ids:
        raise ValueError("no Member-Details?id= links found in Member List HTML")

    members: list[dict] = []
    for mid in ids:
        m = re.search(rf"Member-Details\?id={mid}(.{{0,2500}})", html, re.I | re.S)
        if not m:
            continue
        chunk = m.group(0)[:2500]
        nm = re.search(
            rf'Member-Details\?id={mid}"[^>]*>(.*?)</a>', chunk, re.I | re.S
        )
        raw = ""
        if nm:
            raw = html_lib.unescape(re.sub(r"<[^>]+>", " ", nm.group(1)))
            raw = re.sub(r"\s+", " ", raw).strip()
        seat = re.search(
            r"Member for\s+([^<(]+?)\s*\(([A-Z]{2,4})\)", chunk
        )
        if not seat:
            raise ValueError(f"member id={mid} ({raw!r}): missing electorate/party")
        electorate = seat.group(1).strip()
        party_short = seat.group(2).strip()
        if party_short not in PARTY_FULL:
            raise ValueError(
                f"member id={mid} ({raw!r}): unknown party abbrev {party_short!r}"
            )
        name = display_name(raw)
        if not name:
            raise ValueError(f"member id={mid}: empty name")
        members.append(
            {
                "member_id": mid,
                "name": name,
                "name_raw": raw,
                "chamber": "Assembly",
                "party": PARTY_FULL[party_short],
                "party_short": party_short,
                "electorate": electorate,
                "region": None,
                "url": PROFILE_TMPL.format(member_id=mid),
            }
        )
    members.sort(key=lambda m: (m.get("name") or "").lower())
    return members


def parse_memlist_pdf_text(text: str) -> dict[str, dict]:
    """Map folded electorate -> {party_short, surname hint} from MEMLIST layout.

    PDF text is messy (multi-line members). We only use rows that clearly show
    ELECTORATE + PARTY abbreviations on one line for cross-check.
    """
    out: dict[str, dict] = {}
    # Lines like: ASIF, Bisma [Ms]   Sandgate   ALP   ...
    row_re = re.compile(
        r"^([A-Z][A-Z' \-]+),\s+.+\s{2,}([A-Z][A-Za-z' \-]+)\s{2,}(ALP|LNP|GRN|IND|KAP)\b",
        re.M,
    )
    for m in row_re.finditer(text):
        electorate = m.group(2).strip()
        party_short = m.group(3)
        out[fold(electorate)] = {
            "electorate": electorate,
            "party_short": party_short,
            "surname": m.group(1).strip().title(),
        }
    return out


def cross_check(members: list[dict], pdf_map: dict[str, dict]) -> list[str]:
    warnings: list[str] = []
    if not pdf_map:
        warnings.append("MEMLIST PDF parse found 0 electorate rows; skipped cross-check")
        return warnings
    for m in members:
        key = fold(m["electorate"])
        row = pdf_map.get(key)
        if not row:
            warnings.append(
                f"electorate {m['electorate']!r} not found in MEMLIST PDF parse"
            )
            continue
        if row["party_short"] != m["party_short"]:
            warnings.append(
                f"{m['electorate']}: HTML party {m['party_short']} != "
                f"PDF {row['party_short']}"
            )
    html_seats = {fold(m["electorate"]) for m in members}
    pdf_only = sorted(set(pdf_map) - html_seats)
    if pdf_only:
        warnings.append(
            f"MEMLIST PDF seats not on Member List: {[pdf_map[k]['electorate'] for k in pdf_only[:10]]}"
        )
    return warnings


def report(members: list[dict]) -> bool:
    print("=== QLD official members fetch report ===")
    print(f"Total records: {len(members)}")
    ok = len(members) == EXPECTED
    flag = "OK" if ok else f"CHECK (expected {EXPECTED})"
    print(f"  Assembly: {len(members)}  [{flag}]")

    party_counts = Counter(m.get("party") or "(missing)" for m in members)
    print("Counts per party:")
    for party, n in sorted(party_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {party}: {n}")

    seats = [m.get("electorate") for m in members]
    if len(seats) != len(set(seats)):
        ok = False
        print("ERROR: duplicate electorates")
    missing_url = [m for m in members if not m.get("url")]
    print(f"Members missing profile URL: {len(missing_url)}")
    incomplete = []
    for m in members:
        miss = [k for k in ("name", "chamber", "party", "electorate", "url") if not m.get(k)]
        if miss:
            incomplete.append((m, miss))
    print(f"Members missing required fields: {len(incomplete)}")
    for m, fields in incomplete[:20]:
        print(f"  {m.get('name')!r}: missing {', '.join(fields)}")
        ok = False

    if members:
        print("Sample (first 5):")
        for m in members[:5]:
            print(
                f"  {m.get('chamber')} {m.get('name')} | {m.get('party')} | "
                f"{m.get('electorate')}"
            )
            print(f"           {m.get('url')}")
    return ok and not incomplete and not missing_url


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--from-html",
        help="path to saved Member List HTML (when live fetch is blocked)",
    )
    ap.add_argument(
        "--skip-pdf-check",
        action="store_true",
        help="do not download/cross-check MEMLIST.pdf",
    )
    args = ap.parse_args()

    try:
        if args.from_html:
            html = Path(args.from_html).read_text(encoding="utf-8", errors="replace")
            print(f"Reading Member List HTML from {args.from_html}")
        else:
            print(f"Fetching {MEMBER_LIST_URL}…")
            time.sleep(REQUEST_DELAY_SEC)
            html = http_get(MEMBER_LIST_URL).decode("utf-8", "replace")
        members = parse_member_list(html)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    warnings: list[str] = []
    if not args.skip_pdf_check:
        try:
            print(f"Fetching MEMLIST PDF for cross-check…")
            time.sleep(REQUEST_DELAY_SEC)
            pdf = http_get(MEMLIST_PDF)
            # Prefer pdftotext when available; else skip with warning.
            import shutil
            import subprocess
            import tempfile

            if shutil.which("pdftotext"):
                with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
                    tmp.write(pdf)
                    tmp.flush()
                    text = subprocess.check_output(
                        ["pdftotext", "-layout", tmp.name, "-"],
                        text=True,
                        errors="replace",
                    )
                pdf_map = parse_memlist_pdf_text(text)
                print(f"MEMLIST PDF electorate rows parsed: {len(pdf_map)}")
                warnings.extend(cross_check(members, pdf_map))
            else:
                warnings.append("pdftotext not installed; skipped MEMLIST PDF check")
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"MEMLIST PDF cross-check failed: {exc}")

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    ok = report(members)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "member_list_url": MEMBER_LIST_URL,
        "memlist_pdf_url": MEMLIST_PDF,
        "expected_counts": {"Assembly": EXPECTED},
        "credit": "Parliament of Queensland",
        "notes": (
            "Unicameral Legislative Assembly (93 districts). "
            "Display names use preferred name in parentheses from the Member List "
            "when present. Party abbreviations expanded from Parliament list labels. "
            "Addresses/emails/phones from MEMLIST.pdf are not stored."
        ),
        "members": members,
    }
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
