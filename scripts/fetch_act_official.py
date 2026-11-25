#!/usr/bin/env python3
"""Fetch CURRENT ACT Legislative Assembly members (unicameral, stdlib only).

Writes data/act_official.json and prints a report.

Primary source: ACT Legislative Assembly current members table
  https://www.parliament.act.gov.au/members/current
  Profile URLs: …/members/current/{slug}

Cloudflare often returns HTTP 403 / challenge HTML for unattended fetches.
This script uses a Chrome-compatible UA that still identifies PolicyDeskAU.
Pass --from-html with a browser-cleared save of the current-members page when
live fetch is blocked.

Expected: 25 MLAs in 5 multi-member electorates (5 each):
Brindabella, Ginninderra, Kurrajong, Murrumbidgee, Yerrabi.

Facts only — no addresses, emails, phones, portraits, or biographies.
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

import guards

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "act_official.json"

USER_AGENT = (
    "Mozilla/5.0 (compatible; PolicyDeskAU/1.0; +https://policydesk.au) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SOURCE = "ACT Legislative Assembly"
SOURCE_URL = "https://www.parliament.act.gov.au/members/current"
MEMBER_LIST_URL = SOURCE_URL
PROFILE_TMPL = "https://www.parliament.act.gov.au/members/current/{slug}"
EXPECTED = 25
EXPECTED_PER_SEAT = 5
ELECTORATES = {
    "Brindabella",
    "Ginninderra",
    "Kurrajong",
    "Murrumbidgee",
    "Yerrabi",
}
REQUEST_DELAY_SEC = 1.0

# Affiliation column label → full party name + short code (facts mapped from printed label).
PARTY_FULL = {
    "Labor": ("Australian Labor Party", "ALP"),
    "Liberal": ("Liberal Party", "LIB"),
    "Liberals": ("Liberal Party", "LIB"),
    "Green": ("ACT Greens", "GRN"),
    "Greens": ("ACT Greens", "GRN"),
    "Independent": ("Independent", "IND"),
}

HONORIFIC = re.compile(
    r"^(?:The\s+Hon(?:ourable)?\.?|Hon(?:ourable)?\.?|Mr|Ms|Mrs|Miss|Dr|Prof(?:essor)?)\s+",
    re.I,
)
POSTNOM = re.compile(
    r"\s+(?:CSC|AM|AO|OAM|AC|QC|SC|KC|MP|MLA|JP)(?:\s+(?:CSC|AM|AO|OAM|AC|QC|SC|KC|MP|MLA|JP))*\s*$",
    re.I,
)
ROLE_AFTER = re.compile(
    r"\s+(?:Chief Minister|Deputy Chief Minister|Speaker|Deputy Speaker|"
    r"Minister|Opposition Leader|Deputy Opposition Leader|Whip|"
    r"Leader,? ACT Greens|Deputy Leader,? ACT Greens)\b.*$",
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
                body = guards.read_checked(resp, url)
                head = body[:900].lower()
                if (
                    b"just a moment" in head
                    or b"cf-mitigated" in head
                    or b"challenge-platform" in head
                ):
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


def strip_tags(raw: str) -> str:
    text = html_lib.unescape(re.sub(r"<[^>]+>", " ", raw or ""))
    return re.sub(r"\s+", " ", text).strip()


def display_name(raw: str) -> str:
    name = HONORIFIC.sub("", strip_tags(raw))
    name = ROLE_AFTER.sub("", name)
    name = POSTNOM.sub("", name)
    return re.sub(r"\s+", " ", name).strip()


def normalise_affiliation(raw: str) -> str:
    """Map affiliation cell text to a PARTY_FULL key."""
    text = strip_tags(raw).replace("⬤", " ")
    # Known HTML glitch on Emerson row: colour span splits "Independent" as "I</span>ndependent".
    text = re.sub(r"\bI\s+ndependent\b", "Independent", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_members(html: str) -> list[dict]:
    members: list[dict] = []
    seen: set[str] = set()
    for row in re.findall(r"<tr>(.*?)</tr>", html, re.I | re.S):
        m = re.search(
            r'href="https://www\.parliament\.act\.gov\.au/members/current/'
            r'([^"/?#]+)"[^>]*>(.*?)</a>',
            row,
            re.I | re.S,
        )
        if not m:
            continue
        slug = m.group(1)
        if slug in seen:
            continue
        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.I | re.S)
        if len(tds) < 3:
            continue
        name = display_name(m.group(2))
        electorate = strip_tags(tds[1])
        affiliation = normalise_affiliation(tds[2])
        if electorate not in ELECTORATES:
            raise ValueError(f"{slug}: unexpected electorate {electorate!r}")
        if affiliation not in PARTY_FULL:
            raise ValueError(f"{slug}: unknown affiliation {affiliation!r}")
        party, party_short = PARTY_FULL[affiliation]
        seen.add(slug)
        members.append(
            {
                "member_id": slug,
                "name": name,
                "chamber": "Assembly",
                "party": party,
                "party_short": party_short,
                "party_label_raw": affiliation,
                "electorate": electorate,
                "region": None,
                "url": PROFILE_TMPL.format(slug=slug),
            }
        )
    return members


def report(members: list[dict]) -> bool:
    print("=== ACT official members fetch report ===")
    print(f"Total records: {len(members)}")
    ok = len(members) == EXPECTED
    flag = "OK" if ok else f"CHECK (expected {EXPECTED})"
    print(f"  Assembly: {len(members)}  [{flag}]")

    party_counts = Counter(m.get("party") or "(missing)" for m in members)
    print("Counts per party:")
    for party, n in sorted(party_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {party}: {n}")

    seats = Counter(m.get("electorate") for m in members)
    print(f"Electorates: {sorted(seats)}")
    for seat in sorted(ELECTORATES):
        n = seats.get(seat, 0)
        if n != EXPECTED_PER_SEAT:
            ok = False
            print(f"ERROR: {seat} has {n} members (expected {EXPECTED_PER_SEAT})")

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
        help="path to browser-cleared save of /members/current HTML",
    )
    args = ap.parse_args()

    try:
        if args.from_html:
            path = Path(args.from_html)
            print(f"Reading {path}")
            html = path.read_text(encoding="utf-8", errors="replace")
        else:
            print(f"Fetching {MEMBER_LIST_URL}…")
            time.sleep(REQUEST_DELAY_SEC)
            html = http_get(MEMBER_LIST_URL).decode("utf-8", "replace")
        members = parse_members(html)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    members.sort(key=lambda m: ((m.get("name") or "").lower(), m.get("electorate") or ""))
    ok = report(members)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "member_list_url": MEMBER_LIST_URL,
        "expected_count": EXPECTED,
        "credit": "ACT Legislative Assembly",
        "notes": (
            "Unicameral. Legislative Assembly: 25 members in 5 multi-member "
            "electorates (Brindabella, Ginninderra, Kurrajong, Murrumbidgee, "
            "Yerrabi), 5 each. Party from the Affiliation column on "
            "/members/current (Labor/Liberal/Liberals/Green/Independent). "
            "Liberal and Liberals → Liberal Party; Green → ACT Greens. "
            "Addresses, emails, phones and biographies are not stored."
        ),
        "members": members,
    }
    try:
        guards.assert_profile_urls(members, guards.HOSTS["act"])
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
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
