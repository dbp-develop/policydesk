#!/usr/bin/env python3
"""Fetch CURRENT Victorian MPs from the Parliament of Victoria search API.

Standard library only. Writes data/vic_official.json and prints a report.

Source: https://www.parliament.vic.gov.au/api/search/members
(same data as the public member search UI). Facts only — no portraits or bios.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "vic_official.json"

USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
BASE = "https://www.parliament.vic.gov.au"
API_PATH = "/api/search/members"
SOURCE_URL = "https://www.parliament.vic.gov.au/members/"

# Parliament house filter values used by the public search UI / API.
HOUSE = {
    "10": "Assembly",
    "20": "Council",
}
EXPECTED = {"Assembly": 88, "Council": 40}
REQUEST_DELAY_SEC = 1.5


def http_get_json(url: str) -> dict:
    """GET JSON with polite User-Agent, timeout, and up to 3 retries."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
            last_err = err
            print(f"  attempt {attempt}/3 failed: {err}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after 3 attempts: {last_err}")


def membership_map(hit: dict) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for item in hit.get("memberships") or []:
        title = (item.get("title") or "").strip()
        details = [d for d in (item.get("details") or []) if d]
        if title:
            out[title] = details
    return out


def first_detail(mem: dict[str, list[str]], title: str) -> str | None:
    details = mem.get(title) or []
    return details[0] if details else None


def normalize_party(party: str | None) -> str | None:
    if party is None:
        return None
    text = party.strip()
    if not text:
        return None
    if text.lower() in {"independent", "independent liberal", "ind"}:
        # Keep parliament's own Independent label; map loose variants carefully.
        if text.lower() == "independent liberal":
            return text  # retain parliament wording if ever present
        return "Independent" if text.lower() in {"independent", "ind"} else text
    return text


def parse_hit(hit: dict) -> dict:
    mem = membership_map(hit)
    house_code = str(hit.get("house") or "")
    chamber = HOUSE.get(house_code)
    if not chamber:
        # Fall back to membership House label.
        house_label = (first_detail(mem, "House") or "").lower()
        if "assembly" in house_label:
            chamber = "Assembly"
        elif "council" in house_label:
            chamber = "Council"
        else:
            chamber = None

    seat = first_detail(mem, "Member for")
    party = normalize_party(first_detail(mem, "Party"))
    rel = hit.get("url") or ""
    profile_url = urllib.parse.urljoin(BASE, rel) if rel else None

    record = {
        "name": (hit.get("title") or "").strip() or None,
        "chamber": chamber,
        "party": party,
        "url": profile_url,
    }
    if chamber == "Assembly":
        record["electorate"] = seat
        record["region"] = None
    elif chamber == "Council":
        record["electorate"] = None
        record["region"] = seat
    else:
        record["electorate"] = seat
        record["region"] = None
    return record


def fetch_chamber(house_code: str) -> list[dict]:
    chamber = HOUSE[house_code]
    params = {
        "page": 1,
        "pageSize": 200,
        "member-house": house_code,
        "member-status": "current",
        "sortType": 2,
    }
    url = f"{BASE}{API_PATH}?{urllib.parse.urlencode(params)}"
    print(f"Fetching current {chamber} members...")
    data = http_get_json(url)
    result = data.get("result") or {}
    total = result.get("totalMatching")
    hits = result.get("hits") or []
    print(f"  API totalMatching={total}, hits returned={len(hits)}")
    return [parse_hit(h) for h in hits]


def missing_fields(member: dict) -> list[str]:
    missing: list[str] = []
    for key in ("name", "chamber", "party", "url"):
        if not member.get(key):
            missing.append(key)
    if member.get("chamber") == "Assembly" and not member.get("electorate"):
        missing.append("electorate")
    if member.get("chamber") == "Council" and not member.get("region"):
        missing.append("region")
    return missing


def report(members: list[dict]) -> bool:
    """Print report. Returns True if chamber counts match expected."""
    print("=== Vic official members fetch report ===")
    print(f"Total records: {len(members)}")

    counts_ok = True
    for chamber, expected in EXPECTED.items():
        count = sum(1 for m in members if m["chamber"] == chamber)
        if count == expected:
            flag = "OK"
        else:
            flag = f"CHECK (expected {expected})"
            counts_ok = False
        print(f"  {chamber}: {count}  [{flag}]")

    party_counts = Counter(m.get("party") or "(missing)" for m in members)
    print("Counts per party:")
    for party, n in sorted(party_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {party}: {n}")

    incomplete = [(m, missing_fields(m)) for m in members if missing_fields(m)]
    print(f"Members missing any field: {len(incomplete)}")
    for m, fields in incomplete[:20]:
        print(f"  {m.get('name')!r}: missing {', '.join(fields)}")

    print("Sample (first 5):")
    for m in members[:5]:
        seat = m.get("electorate") or m.get("region") or "?"
        print(f"  {m.get('chamber') or '?':8} {m.get('name')} | {m.get('party')} | {seat}")
        print(f"           {m.get('url')}")

    return counts_ok


def main() -> int:
    members: list[dict] = []
    for i, house_code in enumerate(("10", "20")):
        if i:
            time.sleep(REQUEST_DELAY_SEC)
        members.extend(fetch_chamber(house_code))

    members.sort(
        key=lambda m: (
            0 if m.get("chamber") == "Assembly" else 1,
            (m.get("name") or "").lower(),
        )
    )

    counts_ok = report(members)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "Parliament of Victoria",
        "source_url": SOURCE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "api_url": f"{BASE}{API_PATH}",
        "expected_counts": EXPECTED,
        "members": members,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")

    if not members:
        print("ERROR: fetch returned zero members.", file=sys.stderr)
        return 1

    if not counts_ok:
        actual = {
            chamber: sum(1 for m in members if m.get("chamber") == chamber)
            for chamber in EXPECTED
        }
        print(
            "WARNING: chamber counts differ from nominal sizes "
            f"(got Assembly={actual['Assembly']}, Council={actual['Council']}; "
            f"expected {EXPECTED['Assembly']}/{EXPECTED['Council']}). "
            "Legitimate vacancies are tracked in data/vacancies.json and checked by "
            "validate_members.py.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
