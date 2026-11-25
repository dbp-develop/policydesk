#!/usr/bin/env python3
"""Build data/act/members.json from data/act_official.json (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import guards

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "act_official.json"
VACANCIES_PATH = ROOT / "data" / "act" / "vacancies.json"
OUT = ROOT / "data" / "act" / "members.json"

PARTY_SHORT = {
    "Australian Labor Party": "ALP",
    "Liberal Party": "LIB",
    "ACT Greens": "GRN",
    "Independent": "IND",
}


def slugify(name: str) -> str:
    text = unicodedata.normalize("NFKD", name)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "member"


def unique_id(name: str, used: set[str]) -> str:
    base = "act-" + slugify(name)
    candidate = base
    n = 2
    while candidate in used:
        candidate = f"{base}-{n}"
        n += 1
    used.add(candidate)
    return candidate


def iso_date(value: str | None) -> str:
    return guards.iso_date(value)


def party_short(party: str, fallback: str | None = None) -> str:
    if party in PARTY_SHORT:
        return PARTY_SHORT[party]
    if fallback:
        return fallback
    print(f"WARNING: unmapped party {party!r} → OTH", file=sys.stderr)
    return "OTH"


def transform(raw: dict, used_ids: set[str], last_updated: str) -> dict:
    chamber_raw = raw.get("chamber")
    if chamber_raw != "Assembly":
        raise ValueError(f"Unknown chamber: {chamber_raw!r} for {raw.get('name')!r}")

    party = raw.get("party") or ""
    return {
        "id": unique_id(raw.get("name") or "", used_ids),
        "name": raw.get("name"),
        "chamber": "lower",
        "parliament": "act",
        "state": "ACT",
        "electorate": raw.get("electorate"),
        "region": None,
        "party": party,
        "party_short": party_short(party, raw.get("party_short")),
        "independent": party == "Independent",
        "official_url": raw.get("url"),
        "member_id": raw.get("member_id"),
        "x_handle": None,
        "photo_url": None,
        "photo_credit": None,
        "photo_licence": None,
        "source": "ACT Legislative Assembly",
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
        raise ValueError("data/act/vacancies.json must be a JSON array")
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
    members.sort(key=lambda m: ((m.get("name") or "").lower(), m.get("electorate") or ""))

    problem = guards.member_build_error("act", members, vacancies)
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
        "source": "ACT Legislative Assembly",
        "source_url": "https://www.parliament.act.gov.au/members/current",
        "parliament": "act",
        "last_updated": last_updated,
        "vacancies": vacancies,
        "members": members,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lower = sum(1 for m in members if m["chamber"] == "lower")
    print("=== build_act_members ===")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"members: {len(members)} (lower={lower})")
    print(f"vacancies: {len(vacancies)}")
    print(f"last_updated: {last_updated}")
    missing = [m["name"] for m in members if not m.get("official_url")]
    if missing:
        print(f"WARNING: {len(missing)} without official_url: {missing[:10]}", file=sys.stderr)
        return 1
    la_vacancies = [
        v for v in vacancies if v.get("chamber") in {"Assembly", "lower"}
    ]
    if lower + len(la_vacancies) != 25:
        print(
            f"ERROR: Assembly fill {lower}+vacancies != 25",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
