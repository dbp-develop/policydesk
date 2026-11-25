#!/usr/bin/env python3
"""Build data/sa/members.json from data/sa_official.json (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "sa_official.json"
VACANCIES_PATH = ROOT / "data" / "sa" / "vacancies.json"
OUT = ROOT / "data" / "sa" / "members.json"

PARTY_SHORT = {
    "Australian Labor Party": "ALP",
    "Liberal Party": "LIB",
    "Independent": "IND",
    "Pauline Hanson's One Nation": "ONP",
    "Greens SA": "GRN",
    "Family First Party": "FFP",
}


def slugify(name: str) -> str:
    text = unicodedata.normalize("NFKD", name)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "member"


def unique_id(name: str, used: set[str]) -> str:
    base = "sa-" + slugify(name)
    candidate = base
    n = 2
    while candidate in used:
        candidate = f"{base}-{n}"
        n += 1
    used.add(candidate)
    return candidate


def iso_date(value: str | None) -> str:
    if value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            pass
    return date.today().isoformat()


def party_short(party: str, fallback: str | None = None) -> str:
    if party in PARTY_SHORT:
        return PARTY_SHORT[party]
    if fallback:
        return fallback
    print(f"WARNING: unmapped party {party!r} → OTH", file=sys.stderr)
    return "OTH"


def transform(raw: dict, used_ids: set[str], last_updated: str) -> dict:
    chamber_raw = raw.get("chamber")
    if chamber_raw == "Assembly":
        chamber = "lower"
        electorate = raw.get("electorate")
        region = None
    elif chamber_raw == "Council":
        chamber = "upper"
        electorate = None
        region = raw.get("region") or "South Australia"
    else:
        raise ValueError(f"Unknown chamber: {chamber_raw!r} for {raw.get('name')!r}")

    party = raw.get("party") or ""
    return {
        "id": unique_id(raw.get("name") or "", used_ids),
        "name": raw.get("name"),
        "chamber": chamber,
        "parliament": "sa",
        "state": "SA",
        "electorate": electorate,
        "region": region,
        "party": party,
        "party_short": party_short(party, raw.get("party_short")),
        "independent": party == "Independent",
        "official_url": raw.get("url"),
        "member_id": raw.get("member_id"),
        "x_handle": None,
        "photo_url": None,
        "photo_credit": None,
        "photo_licence": None,
        "source": "Parliament of South Australia",
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
        raise ValueError("data/sa/vacancies.json must be a JSON array")
    return data


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: missing {SRC.relative_to(ROOT)}", file=sys.stderr)
        return 1

    official = json.loads(SRC.read_text(encoding="utf-8"))
    vacancies = load_vacancies()
    last_updated = iso_date(official.get("fetched_at"))
    used_ids: set[str] = set()
    members = [
        transform(m, used_ids, last_updated) for m in official.get("members") or []
    ]
    members.sort(key=lambda m: ((m.get("name") or "").lower(), m.get("chamber") or ""))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "Parliament of South Australia",
        "source_url": "https://www.parliament.sa.gov.au/en/Members/Members-Home",
        "parliament": "sa",
        "last_updated": last_updated,
        "vacancies": vacancies,
        "members": members,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lower = sum(1 for m in members if m["chamber"] == "lower")
    upper = sum(1 for m in members if m["chamber"] == "upper")
    print("=== build_sa_members ===")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"members: {len(members)} (lower={lower}, upper={upper})")
    print(f"vacancies: {len(vacancies)}")
    print(f"last_updated: {last_updated}")
    missing = [m["name"] for m in members if not m.get("official_url")]
    if missing:
        print(f"WARNING: {len(missing)} without official_url: {missing[:10]}", file=sys.stderr)
        return 1
    if lower + len([v for v in vacancies if v.get("chamber") in {"Assembly", "lower"}]) != 47:
        print(
            f"ERROR: Assembly fill {lower}+vacancies != 47",
            file=sys.stderr,
        )
        return 1
    if upper != 22:
        print(f"ERROR: Council members {upper} != 22", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
