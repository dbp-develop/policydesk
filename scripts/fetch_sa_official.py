#!/usr/bin/env python3
"""Fetch CURRENT South Australia MPs and MLCs (stdlib only).

Writes data/sa_official.json and prints a report.

Primary sources (Parliament of South Australia contact-details API, linked from
www.parliament.sa.gov.au Members pages):
  HA: https://contact-details-api.parliament.sa.gov.au/api/HAMembersDetails
  LC: https://contact-details-api.parliament.sa.gov.au/api/LCMembersDetails

Official profile URLs use the Members Search pattern published in
contact-details client-config.json:
  https://www.parliament.sa.gov.au/Search/Member?type=member&id={pmId}

Facts only — no addresses, emails, phones, dates of birth, qualifications or bios.
Pass --from-json with saved HA/LC JSON when live fetch is blocked.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sa_official.json"

USER_AGENT = (
    "Mozilla/5.0 (compatible; PolicyDeskAU/1.0; +https://policydesk.au) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SOURCE = "Parliament of South Australia"
SOURCE_URL = "https://www.parliament.sa.gov.au/en/Members/Members-Home"
API_BASE = "https://contact-details-api.parliament.sa.gov.au/api"
HA_URL = f"{API_BASE}/HAMembersDetails"
LC_URL = f"{API_BASE}/LCMembersDetails"
MEMBER_DETAIL = (
    "https://www.parliament.sa.gov.au/Search/Member?type=member&id="
)
EXPECTED = {"Assembly": 47, "Council": 22}
REQUEST_DELAY_SEC = 1.0

# Abbreviations as printed on the House of Assembly contact list; full names from
# HAPartyRepresentation / Legislative Council contact list labels.
PARTY_FULL = {
    "ALP": "Australian Labor Party",
    "Australian Labor Party": "Australian Labor Party",
    "Liberal": "Liberal Party",
    "Liberal Party": "Liberal Party",
    "Independent": "Independent",
    "Pauline Hanson's One Nation": "Pauline Hanson's One Nation",
    "Greens SA": "Greens SA",
    "Family First Party": "Family First Party",
    "Family First": "Family First Party",
}


def http_get(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError) as err:
            last_err = err
            print(f"  attempt {attempt}/3 failed: {err}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after 3 attempts: {last_err}")


def display_name(raw: dict) -> str:
    preferred = (raw.get("preferredName") or "").strip()
    first = (raw.get("firstName") or "").strip()
    last = (raw.get("lastName") or "").strip()
    given = preferred or first
    name = f"{given} {last}".strip()
    return " ".join(name.split())


def party_full(label: str) -> str:
    label = (label or "").strip()
    if label not in PARTY_FULL:
        raise ValueError(f"unknown party label {label!r}")
    return PARTY_FULL[label]


def party_short(full: str) -> str:
    reverse = {
        "Australian Labor Party": "ALP",
        "Liberal Party": "LIB",
        "Independent": "IND",
        "Pauline Hanson's One Nation": "ONP",
        "Greens SA": "GRN",
        "Family First Party": "FFP",
    }
    if full not in reverse:
        raise ValueError(f"unmapped full party {full!r}")
    return reverse[full]


def parse_ha(payload: dict) -> list[dict]:
    members: list[dict] = []
    for raw in payload.get("memberContacts") or []:
        pm_id = raw.get("pmId")
        if pm_id is None:
            raise ValueError("HA member missing pmId")
        name = display_name(raw)
        if not name:
            raise ValueError(f"HA pmId {pm_id}: empty name")
        seat = (raw.get("electorateName") or "").strip()
        if not seat:
            raise ValueError(f"HA {name!r}: missing electorate")
        party = party_full(raw.get("politicalPartyName") or "")
        members.append(
            {
                "member_id": str(pm_id),
                "name": name,
                "name_raw": " ".join(
                    p
                    for p in [
                        (raw.get("title") or "").strip(),
                        (raw.get("firstName") or "").strip(),
                        (raw.get("otherName") or "").strip(),
                        (raw.get("lastName") or "").strip(),
                    ]
                    if p
                ),
                "chamber": "Assembly",
                "party": party,
                "party_short": party_short(party),
                "electorate": seat,
                "region": None,
                "url": MEMBER_DETAIL + str(pm_id),
            }
        )
    members.sort(key=lambda m: (m.get("name") or "").lower())
    return members


def parse_lc(payload: dict) -> list[dict]:
    members: list[dict] = []
    for raw in payload.get("memberContacts") or []:
        pm_id = raw.get("pmId")
        if pm_id is None:
            raise ValueError("LC member missing pmId")
        # LC payload has no preferredName; trim whitespace on given names.
        name = display_name(
            {
                "preferredName": None,
                "firstName": raw.get("firstName"),
                "lastName": raw.get("lastName"),
            }
        )
        if not name:
            raise ValueError(f"LC pmId {pm_id}: empty name")
        party = party_full(raw.get("politicalPartyName") or "")
        members.append(
            {
                "member_id": str(pm_id),
                "name": name,
                "name_raw": " ".join(
                    p
                    for p in [
                        (raw.get("title") or "").strip(),
                        (raw.get("firstName") or "").strip(),
                        (raw.get("otherName") or "").strip(),
                        (raw.get("lastName") or "").strip(),
                    ]
                    if p
                ),
                "chamber": "Council",
                "party": party,
                "party_short": party_short(party),
                "electorate": None,
                "region": "South Australia",
                "url": MEMBER_DETAIL + str(pm_id),
            }
        )
    members.sort(key=lambda m: (m.get("name") or "").lower())
    return members


def report(members: list[dict], parliament_number: int | None) -> bool:
    print("=== SA official members fetch report ===")
    if parliament_number is not None:
        print(f"Parliament number: {parliament_number}")
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


def load_json(args: argparse.Namespace, name: str, url: str) -> dict:
    if args.from_json:
        path = Path(args.from_json) / name
        if not path.exists():
            raise FileNotFoundError(f"missing {path}")
        print(f"Reading {path}")
        return json.loads(path.read_text(encoding="utf-8"))
    print(f"Fetching {url}…")
    time.sleep(REQUEST_DELAY_SEC)
    return json.loads(http_get(url).decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--from-json",
        help="directory with HAMembersDetails.json and LCMembersDetails.json",
    )
    args = ap.parse_args()

    try:
        ha_payload = load_json(args, "HAMembersDetails.json", HA_URL)
        lc_payload = load_json(args, "LCMembersDetails.json", LC_URL)
        assembly = parse_ha(ha_payload)
        council = parse_lc(lc_payload)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    members = assembly + council
    members.sort(key=lambda m: ((m.get("name") or "").lower(), m.get("chamber") or ""))
    parliament_number = ha_payload.get("parliamentNumber") or lc_payload.get(
        "parliamentNumber"
    )
    ok = report(members, parliament_number)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "assembly_list_url": HA_URL,
        "council_list_url": LC_URL,
        "member_detail_url_prefix": MEMBER_DETAIL,
        "parliament_number": parliament_number,
        "expected_counts": EXPECTED,
        "credit": "Parliament of South Australia",
        "notes": (
            "Bicameral. House of Assembly: 47 districts. Legislative Council: "
            "22 members elected statewide for the whole of South Australia. "
            "Primary facts from the Parliament contact-details API "
            "(HAMembersDetails / LCMembersDetails), linked from parliament.sa.gov.au "
            "Members pages. Party abbreviations expanded from HAPartyRepresentation "
            "and LC list labels. Addresses, emails, phones, dates of birth, "
            "qualifications and biographies are not stored."
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
