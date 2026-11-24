#!/usr/bin/env python3
"""Validate Vic, Federal and NSW members.json seat counts (stdlib only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PARLIAMENTS = {
    "vic": {
        "path": ROOT / "data" / "members.json",
        "lower": 88,
        "upper": 40,
        "lower_label": "Assembly",
        "upper_label": "Council",
        "vacancy_lower": {"Assembly", "lower"},
    },
    "federal": {
        "path": ROOT / "data" / "federal" / "members.json",
        "lower": 150,
        "upper": 76,
        "lower_label": "House",
        "upper_label": "Senate",
        "vacancy_lower": {"House", "lower"},
    },
    "nsw": {
        "path": ROOT / "data" / "nsw" / "members.json",
        "lower": 93,
        "upper": 42,
        "lower_label": "Assembly",
        "upper_label": "Council",
        "vacancy_lower": {"Assembly", "lower"},
    },
}


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def validate_one(key: str, cfg: dict, errors: list[str]) -> None:
    path: Path = cfg["path"]
    if not path.exists():
        fail(f"{key}: missing {path.relative_to(ROOT)}", errors)
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{key}: members file must be an object", errors)
        return

    members = data.get("members")
    vacancies = data.get("vacancies") or []
    if not isinstance(members, list):
        fail(f"{key}: members must be a list", errors)
        return
    if not isinstance(vacancies, list):
        fail(f"{key}: vacancies must be a list", errors)
        return

    lower = [m for m in members if m.get("chamber") == "lower"]
    upper = [m for m in members if m.get("chamber") == "upper"]
    lower_vacancies = [
        v for v in vacancies if v.get("chamber") in cfg["vacancy_lower"]
    ]

    if len(lower) + len(lower_vacancies) != cfg["lower"]:
        fail(
            f"{key}: {cfg['lower_label']} members + vacancies = "
            f"{len(lower)} + {len(lower_vacancies)} != {cfg['lower']}",
            errors,
        )
    if len(upper) != cfg["upper"]:
        fail(
            f"{key}: {cfg['upper_label']} members = {len(upper)} != {cfg['upper']}",
            errors,
        )

    ids = [m.get("id") for m in members]
    if len(ids) != len(set(ids)):
        seen: set[str] = set()
        dupes = []
        for i in ids:
            if i in seen:
                dupes.append(i)
            seen.add(i)
        fail(f"{key}: duplicate ids: {sorted(set(dupes))}", errors)

    for m in members:
        label = m.get("id") or m.get("name") or "?"
        for field in ("name", "party", "official_url", "source"):
            if not m.get(field):
                fail(f"{key}/{label}: missing {field}", errors)
        chamber = m.get("chamber")
        if chamber == "lower" and not m.get("electorate"):
            fail(f"{key}/{label}: lower-house member missing electorate", errors)
        if chamber == "upper" and not m.get("region"):
            fail(f"{key}/{label}: upper-house member missing region", errors)
        if chamber not in {"lower", "upper"}:
            fail(f"{key}/{label}: invalid chamber {chamber!r}", errors)
        if key in {"federal", "nsw"} and m.get("parliament") not in {key, None}:
            fail(f"{key}/{label}: parliament field {m.get('parliament')!r}", errors)

    print(
        f"{key}: members={len(members)} "
        f"(lower={len(lower)}, upper={len(upper)}); "
        f"vacancies={len(vacancies)} "
        f"({cfg['lower_label']} vacancies={len(lower_vacancies)})"
    )
    print(
        f"  {cfg['lower_label']} fill: {len(lower)} + {len(lower_vacancies)} = "
        f"{len(lower) + len(lower_vacancies)} / {cfg['lower']}"
    )
    print(f"  {cfg['upper_label']} fill: {len(upper)} / {cfg['upper']}")


def main() -> int:
    errors: list[str] = []
    print("=== validate_members ===")
    for key, cfg in PARLIAMENTS.items():
        validate_one(key, cfg, errors)

    # Member ids must not collide across parliaments (news/photo keys).
    id_sets: dict[str, set[str]] = {}
    for key, cfg in PARLIAMENTS.items():
        path = cfg["path"]
        if path.exists():
            id_sets[key] = {
                m["id"]
                for m in json.loads(path.read_text(encoding="utf-8"))["members"]
            }
    keys = list(id_sets)
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            overlap = id_sets[a] & id_sets[b]
            if overlap:
                fail(
                    f"id collision between {a} and {b}: {sorted(overlap)[:10]}",
                    errors,
                )

    if errors:
        print(f"FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
