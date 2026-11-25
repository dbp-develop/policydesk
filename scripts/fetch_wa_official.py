#!/usr/bin/env python3
"""Fetch CURRENT Western Australia MPs and MLCs (stdlib only).

Writes data/wa_official.json and prints a report.

Primary sources (Parliament of Western Australia Member Lists):
  Assembly: …/parliament/memblist.nsf/WAssemblyMembers
  Council:  …/parliament/memblist.nsf/WebCurrentMembLC
  Profile patterns:
    LA: …/Member+Lookup+LA+Current/{key}?opendocument
    LC: …/WAllMembersFlat2/{key}?opendocument

Azure WAF often returns HTTP 403 for User-Agent PolicyDeskAU/1.0 alone.
This script uses a Chrome-compatible UA that still identifies PolicyDeskAU.
Pass --from-dir with saved HTML when live fetch is blocked.

Party abbreviations are as printed on the Member Lists. Full party names are
expanded from the Parliament of WA “Western Australian State Election 2025”
Analysis of Results party-abbreviation table and the Current Members by
Political Party labels (facts only — no addresses/emails/phones/bios).

After the 2025 election the Legislative Council is a single statewide
electorate (“Western Australia”), not the former six regions.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "wa_official.json"

USER_AGENT = (
    "Mozilla/5.0 (compatible; PolicyDeskAU/1.0; +https://policydesk.au) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SOURCE = "Parliament of Western Australia"
SOURCE_URL = "https://www.parliament.wa.gov.au/parliament/memblist.nsf/WAMembers"
ASSEMBLY_URL = (
    "https://www.parliament.wa.gov.au/parliament/memblist.nsf/WAssemblyMembers"
)
COUNCIL_URL = (
    "https://www.parliament.wa.gov.au/parliament/memblist.nsf/WebCurrentMembLC"
)
BASE = "https://www.parliament.wa.gov.au"
EXPECTED = {"Assembly": 59, "Council": 37}
REQUEST_DELAY_SEC = 1.0

# Abbreviations as printed on the Member Lists. Full names from Parliament of WA
# Election 2025 Analysis of Results (party abbreviations) / Members by party page.
PARTY_FULL = {
    "ALP": "Australian Labor Party",
    "LIB": "Liberal Party",
    "NAT": "The Nationals WA",
    "ONP": "Pauline Hanson's One Nation",
    "GWA": "Greens (WA)",
    "AJP": "Animal Justice Party",
    "AC": "Australian Christians",
    "LCWA": "Legalise Cannabis Western Australia Party",
    "IND": "Independent",
}

HONORIFIC = re.compile(
    r"^(?:Hon(?:ourable)?\.?|Mr|Ms|Mrs|Miss|Dr|Prof(?:essor)?)\s+",
    re.I,
)
PREFERRED = re.compile(r"^(.+?)\s+\(([^)]+)\)\s*$")


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
                if b"azure waf" in head or b"just a moment" in head:
                    raise RuntimeError(
                        f"WAF/challenge HTML for {url}. "
                        "Re-run with --from-dir after a browser-cleared save."
                    )
                return body
        except (urllib.error.URLError, TimeoutError, RuntimeError) as err:
            last_err = err
            print(f"  attempt {attempt}/3 failed: {err}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after 3 attempts: {last_err}")


def abs_url(href: str) -> str:
    href = href.replace("\\", "/")
    if href.startswith("http"):
        return href
    if not href.startswith("/"):
        href = "/" + href
    return BASE + href


def display_from_list_text(raw: str) -> str:
    name = HONORIFIC.sub("", (raw or "").strip())
    return re.sub(r"\s+", " ", name).strip()


def name_from_key(key: str) -> str:
    """Build display name from Domino lookup key (preferred name when present)."""
    key = urllib.parse.unquote(key.replace("+", " ")).strip()
    if "," not in key:
        return HONORIFIC.sub("", key).strip()
    surname, given = [p.strip() for p in key.split(",", 1)]
    given = HONORIFIC.sub("", given).strip()
    m = PREFERRED.match(given)
    if m:
        given = m.group(2).strip()
    # Title-case ALL-CAPS surname tokens while keeping Mc/Mac-ish as in key.
    if surname.isupper():
        surname = surname.title()
    if given.isupper() and len(given) > 1:
        given = given.title()
    return f"{given} {surname}".strip()


def member_key_from_href(href: str) -> str:
    href = href.replace("\\", "/")
    path = urllib.parse.urlparse(abs_url(href)).path
    # …/Member+Lookup+LA+Current/KEY or …/WAllMembersFlat2/KEY
    part = path.rsplit("/", 1)[-1]
    return urllib.parse.unquote(part)


def parse_assembly(html: str) -> list[dict]:
    pat = re.compile(
        r"<A href=(/Parliament\\Memblist\.nsf/Member\+Lookup\+LA\+Current/[^>\s]+?)"
        r"\s*>(.*?)</A>\s*MLA",
        re.I | re.S,
    )
    members: list[dict] = []
    for m in pat.finditer(html):
        href = m.group(1)
        raw = html_lib.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))
        raw = re.sub(r"\s+", " ", raw).strip()
        after = html[m.end() : m.end() + 500]
        seat = re.search(r"Electorate:\s*([^<\n]+)", after)
        party_s = re.search(r"Party:\s*([^<\n]+)", after)
        if not seat or not party_s:
            raise ValueError(f"Assembly member {raw!r}: missing electorate/party")
        party_short = party_s.group(1).strip()
        if party_short not in PARTY_FULL:
            raise ValueError(
                f"Assembly member {raw!r}: unknown party abbrev {party_short!r}"
            )
        key = member_key_from_href(href)
        name = name_from_key(key) or display_from_list_text(raw)
        if not name:
            raise ValueError(f"Assembly key {key!r}: empty name")
        members.append(
            {
                "member_id": key,
                "name": name,
                "name_raw": raw,
                "chamber": "Assembly",
                "party": PARTY_FULL[party_short],
                "party_short": party_short,
                "electorate": seat.group(1).strip(),
                "region": None,
                "url": abs_url(href),
            }
        )
    members.sort(key=lambda m: (m.get("name") or "").lower())
    return members


def parse_council(html: str) -> list[dict]:
    pat = re.compile(
        r'<a href="(/Parliament\\Memblist\.nsf/WAllMembersFlat2/[^"]+?)"\s*>'
        r"(.*?)</a>\s*MLC",
        re.I | re.S,
    )
    members: list[dict] = []
    for m in pat.finditer(html):
        href = m.group(1)
        raw = html_lib.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))
        raw = re.sub(r"\s+", " ", raw).strip()
        after = html[m.end() : m.end() + 600]
        party_s = re.search(r"Party:\s*([^<\n]+)", after)
        region_m = re.search(r">(Western Australia)</a>", after)
        if not party_s:
            raise ValueError(f"Council member {raw!r}: missing party")
        party_short = party_s.group(1).strip()
        if party_short not in PARTY_FULL:
            raise ValueError(
                f"Council member {raw!r}: unknown party abbrev {party_short!r}"
            )
        region = region_m.group(1) if region_m else "Western Australia"
        key = member_key_from_href(href)
        name = name_from_key(key) or display_from_list_text(raw)
        if not name:
            raise ValueError(f"Council key {key!r}: empty name")
        members.append(
            {
                "member_id": key,
                "name": name,
                "name_raw": raw,
                "chamber": "Council",
                "party": PARTY_FULL[party_short],
                "party_short": party_short,
                "electorate": None,
                "region": region,
                "url": abs_url(href),
            }
        )
    members.sort(key=lambda m: (m.get("name") or "").lower())
    return members


def report(members: list[dict]) -> bool:
    print("=== WA official members fetch report ===")
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
    seats = [m.get("electorate") for m in la]
    if len(seats) != len(set(seats)):
        ok = False
        print("ERROR: duplicate Assembly electorates")
    lc_regions = {m.get("region") for m in members if m["chamber"] == "Council"}
    print(f"Council regions present: {sorted(lc_regions)}")

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


def load_html(args: argparse.Namespace, name: str, url: str) -> str:
    if args.from_dir:
        path = Path(args.from_dir) / name
        if not path.exists():
            raise FileNotFoundError(f"missing {path}")
        print(f"Reading {path}")
        return path.read_text(encoding="utf-8", errors="replace")
    print(f"Fetching {url}…")
    time.sleep(REQUEST_DELAY_SEC)
    return http_get(url).decode("utf-8", "replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--from-dir",
        help="directory with WAssemblyMembers.html and WebCurrentMembLC.html",
    )
    args = ap.parse_args()

    try:
        assembly_html = load_html(args, "WAssemblyMembers.html", ASSEMBLY_URL)
        council_html = load_html(args, "WebCurrentMembLC.html", COUNCIL_URL)
        assembly = parse_assembly(assembly_html)
        council = parse_council(council_html)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    members = assembly + council
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
        "credit": "Parliament of Western Australia",
        "notes": (
            "Bicameral. Legislative Assembly: 59 districts. Legislative Council: "
            "37 members elected statewide for the whole of Western Australia "
            "(regions abolished for the 2025 election). Party abbreviations from "
            "the Member Lists; full party names from the Parliament of WA 2025 "
            "election results party-abbreviation table / Members by party labels. "
            "Addresses, emails, phones and biographies are not stored."
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
