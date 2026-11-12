#!/usr/bin/env python3
"""Validate data/members.json shape, Vic seat counts, and boundary names."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "members.json"
BOUNDARIES = ROOT / "data" / "vic_boundaries.json"

EXPECTED_LOWER = 88
EXPECTED_UPPER = 40


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def feature_names(collection: dict, errors: list[str], label: str) -> list[str]:
    features = collection.get("features") if isinstance(collection, dict) else None
    if not isinstance(features, list):
        fail(f"{label}: missing features", errors)
        return []
    names: list[str] = []
    for feature in features:
        props = feature.get("properties") or {}
        name = props.get("name") or ""
        geom = feature.get("geometry") or {}
        if not name:
            fail(f"{label}: feature missing name", errors)
        if geom.get("type") not in {"Polygon", "MultiPolygon"} or not geom.get("coordinates"):
            fail(f"{label}: {name or '?'} has no polygon geometry", errors)
        names.append(name)
    return names


def check_boundaries(lower: list, lower_vacancies: list, upper: list, errors: list[str]) -> None:
    if not BOUNDARIES.exists():
        fail(f"missing {BOUNDARIES.relative_to(ROOT)}", errors)
        print("Boundaries: MISSING")
        return

    payload = json.loads(BOUNDARIES.read_text(encoding="utf-8"))
    districts = feature_names(payload.get("assembly") or {}, errors, "Assembly boundaries")
    regions = feature_names(payload.get("council") or {}, errors, "Council boundaries")
    district_set = set(districts)
    region_set = set(regions)

    expected_seats = {m.get("electorate") for m in lower if m.get("electorate")}
    for vacancy in lower_vacancies:
        if vacancy.get("electorate"):
            expected_seats.add(vacancy["electorate"])
    expected_regions = {m.get("region") for m in upper if m.get("region")}

    if len(districts) != len(district_set):
        fail("duplicate Assembly district names in boundaries", errors)
    if len(regions) != len(region_set):
        fail("duplicate Council region names in boundaries", errors)
    missing_seats = sorted(expected_seats - district_set)
    extra_seats = sorted(district_set - expected_seats)
    missing_regions = sorted(expected_regions - region_set)
    extra_regions = sorted(region_set - expected_regions)
    if missing_seats:
        fail(f"districts missing from boundaries: {missing_seats}", errors)
    if extra_seats:
        fail(f"boundary districts not in member data: {extra_seats}", errors)
    if missing_regions:
        fail(f"regions missing from boundaries: {missing_regions}", errors)
    if extra_regions:
        fail(f"boundary regions not in member data: {extra_regions}", errors)

    for feature in (payload.get("assembly") or {}).get("features") or []:
        region = (feature.get("properties") or {}).get("region")
        if region not in region_set:
            name = (feature.get("properties") or {}).get("name")
            fail(f"{name}: Council region {region!r} is not a region polygon", errors)

    print(f"Boundaries: {len(districts)} districts, {len(regions)} regions")


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
    check_boundaries(lower, lower_vacancies, upper, errors)

    if errors:
        print(f"FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
