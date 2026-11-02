#!/usr/bin/env python3
"""Validate data/members.json shape and Vic seat counts (stdlib only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "members.json"

EXPECTED_LOWER = 88
EXPECTED_UPPER = 40


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def main() -> int:
    errors: list[str] = []
    if not PATH.exists():
        print(f"ERROR: missing {PATH.relative_to(ROOT)}", file=sys.stderr)
        return 1

    data = json.loads(PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("ERROR: members.json must be an object", file=sys.stderr)
        return 1

    members = data.get("members")
    vacancies = data.get("vacancies") or []
    if not isinstance(members, list):
        print("ERROR: members must be a list", file=sys.stderr)
        return 1
    if not isinstance(vacancies, list):
        print("ERROR: vacancies must be a list", file=sys.stderr)
        return 1

    lower = [m for m in members if m.get("chamber") == "lower"]
    upper = [m for m in members if m.get("chamber") == "upper"]
    lower_vacancies = [
        v for v in vacancies if v.get("chamber") in {"Assembly", "lower"}
    ]

    if len(lower) + len(lower_vacancies) != EXPECTED_LOWER:
        fail(
            f"Assembly members + vacancies = {len(lower)} + {len(lower_vacancies)} "
            f"!= {EXPECTED_LOWER}",
            errors,
        )
    if len(upper) != EXPECTED_UPPER:
        fail(f"Council members = {len(upper)} != {EXPECTED_UPPER}", errors)

    ids = [m.get("id") for m in members]
    if len(ids) != len(set(ids)):
        seen: set[str] = set()
        dupes = []
        for i in ids:
            if i in seen:
                dupes.append(i)
            seen.add(i)
        fail(f"duplicate ids: {sorted(set(dupes))}", errors)

    for m in members:
        label = m.get("id") or m.get("name") or "?"
        for key in ("name", "party", "official_url"):
            if not m.get(key):
                fail(f"{label}: missing {key}", errors)
        chamber = m.get("chamber")
        if chamber == "lower" and not m.get("electorate"):
            fail(f"{label}: Assembly member missing electorate", errors)
        if chamber == "upper" and not m.get("region"):
            fail(f"{label}: Council member missing region", errors)
        if chamber not in {"lower", "upper"}:
            fail(f"{label}: invalid chamber {chamber!r}", errors)

    print("=== validate_members ===")
    print(f"members: {len(members)} (lower={len(lower)}, upper={len(upper)})")
    print(f"vacancies: {len(vacancies)} (Assembly vacancies={len(lower_vacancies)})")
    print(
        f"Assembly fill: {len(lower)} members + {len(lower_vacancies)} vacancies "
        f"= {len(lower) + len(lower_vacancies)} / {EXPECTED_LOWER}"
    )
    print(f"Council fill: {len(upper)} / {EXPECTED_UPPER}")

    if errors:
        print(f"FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
