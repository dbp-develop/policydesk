#!/usr/bin/env python3
"""Fetch CURRENT federal MPs and Senators from the Parliamentary Handbook API.

Standard library only. Writes data/federal_official.json and prints a report.

Source: https://handbookapi.aph.gov.au/api/individuals
  filter InCurrentParliament eq 'True' (string field), paged with $top/$skip.
Profile URLs: https://handbook.aph.gov.au/Parliamentarian/{PHID}
Facts only — no portraits, bios, or office addresses.
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
OUT = ROOT / "data" / "federal_official.json"

USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
API = "https://handbookapi.aph.gov.au/api/individuals"
SOURCE = "Parliament of Australia (Parliamentary Handbook)"
SOURCE_URL = "https://handbook.aph.gov.au/"
PROFILE_TMPL = "https://handbook.aph.gov.au/Parliamentarian/{phid}"
EXPECTED = {"House": 150, "Senate": 76}
PAGE = 100
REQUEST_DELAY_SEC = 1.0

STATE_ABBREV = {
    "New South Wales": "NSW",
    "Victoria": "VIC",
    "Queensland": "QLD",
    "Western Australia": "WA",
    "South Australia": "SA",
    "Tasmania": "TAS",
    "Australian Capital Territory": "ACT",
    "Northern Territory": "NT",
    "NSW": "NSW",
    "Vic": "VIC",
    "VIC": "VIC",
    "Qld": "QLD",
    "QLD": "QLD",
    "WA": "WA",
    "SA": "SA",
    "Tas": "TAS",
    "TAS": "TAS",
    "ACT": "ACT",
    "NT": "NT",
}


def http_get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
            last_err = err
            print(f"  attempt {attempt}/3 failed: {err}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after 3 attempts: {last_err}")


def roles_of(raw: dict) -> list[str]:
    v = raw.get("MPorSenator") or []
    if isinstance(v, str):
        return [v]
    return list(v)


def titlecase_piece(piece: str) -> str:
    if not piece:
        return ""
    if "'" in piece:
        return "'".join(titlecase_piece(b) for b in piece.split("'"))
    upper = piece.upper()
    if upper.startswith("MC") and len(piece) > 2:
        return "Mc" + piece[2:3].upper() + piece[3:].lower()
    return piece[:1].upper() + piece[1:].lower()


def titlecase_family(family: str) -> str:
    """Title-case an UPPERCASE family name, keeping O' / Mc / hyphen patterns."""
    return " ".join(
        "-".join(titlecase_piece(p) for p in chunk.split("-"))
        for chunk in family.split()
    )


def display_name(raw: dict) -> str | None:
    given = (raw.get("GivenName") or "").strip()
    family = (raw.get("FamilyName") or "").strip()
    if not given or not family:
        # Fall back to DisplayName without inventing parts.
        disp = (raw.get("DisplayName") or "").strip()
        return disp or None
    return f"{given} {titlecase_family(family)}"


def classify(raw: dict) -> tuple[str | None, str | None]:
    """Return (chamber, seat) where chamber is House or Senate."""
    el = (raw.get("Electorate") or "").strip()
    sen = (raw.get("SenateState") or "").strip()
    services = raw.get("ElectorateService") or []
    open_div = [
        s
        for s in services
        if (s.get("ServiceEnd") or "").startswith("1900") or not s.get("ServiceEnd")
    ]
    rs = roles_of(raw)
    if open_div or (el and "Member" in rs and not ("Senator" in rs and not el)):
        if open_div:
            return "House", (open_div[0].get("Electorate") or el or "").strip() or None
        if el:
            return "House", el
    if sen or "Senator" in rs:
        return "Senate", sen or (raw.get("State") or "").strip() or None
    if el:
        return "House", el
    return None, None


def state_abbrev(raw: dict, chamber: str, seat: str | None) -> str | None:
    if chamber == "Senate" and seat:
        return STATE_ABBREV.get(seat) or STATE_ABBREV.get((raw.get("StateAbbrev") or "").strip())
    abbr = (raw.get("StateAbbrev") or "").strip()
    if abbr:
        return STATE_ABBREV.get(abbr, abbr.upper())
    st = (raw.get("State") or "").strip()
    return STATE_ABBREV.get(st)


def parse_row(raw: dict) -> dict:
    chamber, seat = classify(raw)
    phid = (raw.get("PHID") or "").strip() or None
    party = (raw.get("Party") or "").strip() or None
    party_abbrev = (raw.get("PartyAbbrev") or "").strip() or None
    record = {
        "phid": phid,
        "name": display_name(raw),
        "chamber": chamber,
        "party": party,
        "party_abbrev": party_abbrev,
        "url": PROFILE_TMPL.format(phid=phid) if phid else None,
        "state": state_abbrev(raw, chamber or "", seat),
        "electorate": seat if chamber == "House" else None,
        "region": seat if chamber == "Senate" else None,
        "raw_display_name": (raw.get("DisplayName") or "").strip() or None,
    }
    return record


def fetch_all() -> list[dict]:
    rows: list[dict] = []
    skip = 0
    filt = urllib.parse.quote("InCurrentParliament eq 'True'")
    while True:
        url = f"{API}?$filter={filt}&$top={PAGE}&$skip={skip}"
        print(f"Fetching current members skip={skip}…")
        data = http_get_json(url)
        batch = data.get("value") or []
        print(f"  got {len(batch)}")
        if not batch:
            break
        rows.extend(batch)
        skip += PAGE
        time.sleep(REQUEST_DELAY_SEC)
    return rows


def missing_fields(member: dict) -> list[str]:
    missing: list[str] = []
    for key in ("name", "chamber", "party", "url", "phid", "state"):
        if not member.get(key):
            missing.append(key)
    if member.get("chamber") == "House" and not member.get("electorate"):
        missing.append("electorate")
    if member.get("chamber") == "Senate" and not member.get("region"):
        missing.append("region")
    return missing


def report(members: list[dict]) -> bool:
    print("=== Federal official members fetch report ===")
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

    incomplete = [(m, missing_fields(m)) for m in members if missing_fields(m)]
    print(f"Members missing any field: {len(incomplete)}")
    for m, fields in incomplete[:20]:
        print(f"  {m.get('name')!r}: missing {', '.join(fields)}")

    if members:
        print("Sample (first 5):")
        for m in members[:5]:
            seat = m.get("electorate") or m.get("region") or "?"
            print(f"  {m.get('chamber') or '?':6} {m.get('name')} | {m.get('party')} | {seat}")
            print(f"         {m.get('url')}")
    return counts_ok


def main() -> int:
    raw_rows = fetch_all()
    members = [parse_row(r) for r in raw_rows]
    members.sort(
        key=lambda m: (
            0 if m.get("chamber") == "House" else 1,
            (m.get("name") or "").lower(),
        )
    )
    counts_ok = report(members)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "api_url": API,
        "expected_counts": EXPECTED,
        "members": members,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")

    if not members:
        print("ERROR: fetch returned zero members.", file=sys.stderr)
        return 1
    if not counts_ok:
        print(
            "WARNING: chamber counts differ from expected "
            f"(House {EXPECTED['House']}, Senate {EXPECTED['Senate']}).",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
