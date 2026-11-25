#!/usr/bin/env python3
"""Build data/federal/members.json from data/federal_official.json (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import guards

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "federal_official.json"
VACANCIES_PATH = ROOT / "data" / "federal" / "vacancies.json"
OUT = ROOT / "data" / "federal" / "members.json"

# Prefer handbook PartyAbbrev; map to short codes used in the UI.
ABBREV_SHORT = {
    "ALP": "ALP",
    "LIB": "LIB",
    "LP": "LIB",
    "LNP": "LNP",
    "NP": "NAT",
    "NATS": "NAT",
    "GRN": "GRN",
    "AG": "GRN",
    "IND": "IND",
    "ON": "ON",
    "PHON": "ON",
    "KAP": "KAP",
    "CA": "CA",
    "JLN": "JLN",
    "UAP": "UAP",
    "UAP [2018]": "UAP",
    "CLP": "CLP",
    "CSA": "CSA",
    "AV": "AV",
}

PARTY_SHORT = {
    "Australian Labor Party": "ALP",
    "Liberal Party of Australia": "LIB",
    "The Nationals": "NAT",
    "Liberal National Party of Queensland": "LNP",
    "Australian Greens": "GRN",
    "Independent": "IND",
    "One Nation": "ON",
    "Pauline Hanson's One Nation": "ON",
    "Katter's Australian Party": "KAP",
    "Centre Alliance": "CA",
    "Jacqui Lambie Network": "JLN",
    "United Australia Party": "UAP",
    "United Australia Party [2018]": "UAP",
    "Country Liberal Party": "CLP",
    "Community Strong Australia": "CSA",
    "Australia's Voice": "AV",
}


def slugify(name: str) -> str:
    text = unicodedata.normalize("NFKD", name)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "member"


def unique_id(name: str, used: set[str]) -> str:
    base = "fed-" + slugify(name)
    candidate = base
    n = 2
    while candidate in used:
        candidate = f"{base}-{n}"
        n += 1
    used.add(candidate)
    return candidate


def iso_date(value: str | None) -> str:
    return guards.iso_date(value)


def party_short(party: str, abbrev: str | None) -> str:
    if abbrev:
        key = abbrev.strip()
        if key in ABBREV_SHORT:
            return ABBREV_SHORT[key]
        # trailing-space variants from the API
        if key.strip() in ABBREV_SHORT:
            return ABBREV_SHORT[key.strip()]
    if party in PARTY_SHORT:
        return PARTY_SHORT[party]
    print(f"WARNING: unmapped party {party!r} / abbrev {abbrev!r} → OTH", file=sys.stderr)
    return "OTH"


def transform(raw: dict, used_ids: set[str], last_updated: str) -> dict:
    chamber_raw = raw.get("chamber")
    if chamber_raw == "House":
        chamber = "lower"
        electorate = raw.get("electorate")
        region = None
    elif chamber_raw == "Senate":
        chamber = "upper"
        electorate = None
        region = raw.get("region")
    else:
        raise ValueError(f"Unknown chamber: {chamber_raw!r} for {raw.get('name')!r}")

    party = raw.get("party") or ""
    return {
        "id": unique_id(raw.get("name") or "", used_ids),
        "name": raw.get("name"),
        "chamber": chamber,
        "parliament": "federal",
        "state": raw.get("state"),
        "electorate": electorate,
        "region": region,
        "party": party,
        "party_short": party_short(party, raw.get("party_abbrev")),
        "independent": party == "Independent" or (raw.get("party_abbrev") or "").strip() == "IND",
        "official_url": raw.get("url"),
        "phid": raw.get("phid"),
        "x_handle": None,
        "photo_url": None,
        "photo_credit": None,
        "photo_licence": None,
        "source": "Parliament of Australia (Parliamentary Handbook)",
        "last_updated": last_updated,
    }


def load_vacancies() -> list[dict]:
    if not VACANCIES_PATH.exists():
        print(
            f"WARNING: missing {VACANCIES_PATH.relative_to(ROOT)}; using empty vacancies",
            file=sys.stderr,
        )
        return []
    data = json.loads(VACANCIES_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("data/federal/vacancies.json must be a JSON array")
    return data


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: missing {SRC.relative_to(ROOT)}", file=sys.stderr)
        return 1

    official = json.loads(SRC.read_text(encoding="utf-8"))
    vacancies = load_vacancies()
    try:
        last_updated = iso_date(official.get("fetched_at"))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    used_ids: set[str] = set()
    members = [
        transform(m, used_ids, last_updated) for m in official.get("members") or []
    ]
    members.sort(key=lambda m: ((m.get("name") or "").lower(), m.get("chamber") or ""))

    problem = guards.member_build_error("federal", members, vacancies)
    if problem:
        print(problem)
        if problem.startswith("VACANCY FILLED:"):
            print(
                "A human must edit the vacancy file in the same change as the new member. "
                "members.json was not written."
            )
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "Parliament of Australia (Parliamentary Handbook)",
        "source_url": "https://handbook.aph.gov.au/",
        "parliament": "federal",
        "last_updated": last_updated,
        "vacancies": vacancies,
        "members": members,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lower = sum(1 for m in members if m["chamber"] == "lower")
    upper = sum(1 for m in members if m["chamber"] == "upper")
    print("=== build_federal_members ===")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"members: {len(members)} (lower={lower}, upper={upper})")
    print(f"vacancies: {len(vacancies)}")
    print(f"last_updated: {last_updated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
