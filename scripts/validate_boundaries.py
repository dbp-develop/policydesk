#!/usr/bin/env python3
"""Validate boundary JSON against members for Vic, Federal, NSW and QLD (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BDIR = ROOT / "data" / "boundaries"

REQUIRED = (
    "source",
    "dataset",
    "dataset_url",
    "licence",
    "licence_url",
    "credit",
    "boundary_version",
    "fetched_at",
    "viewBox",
    "features",
)
PATH_RE = re.compile(r"^(M-?\d+ -?\d+l(-?\d+ -?\d+ ?)+z)+$")

CHECKS = [
    {
        "label": "vic",
        "members": ROOT / "data" / "members.json",
        "layers": {
            "districts": {
                "file": "vic_districts.json",
                "expected": 88,
                "seat_from": "electorate",
                "chamber": "lower",
                "vacancy_chambers": {"Assembly", "lower"},
            },
            "regions": {
                "file": "vic_regions.json",
                "expected": 8,
                "seat_from": "region",
                "chamber": "upper",
                "vacancy_chambers": {"Council", "upper"},
            },
        },
    },
    {
        "label": "federal",
        "members": ROOT / "data" / "federal" / "members.json",
        "layers": {
            "divisions": {
                "file": "federal_divisions.json",
                "expected": 150,
                "seat_from": "electorate",
                "chamber": "lower",
                "vacancy_chambers": {"House", "lower"},
            },
            "states": {
                "file": "federal_states.json",
                "expected": 8,
                "seat_from": "region",
                "chamber": "upper",
                "vacancy_chambers": {"Senate", "upper"},
            },
        },
    },
    {
        "label": "nsw",
        "members": ROOT / "data" / "nsw" / "members.json",
        "layers": {
            "districts": {
                "file": "nsw_districts.json",
                "expected": 93,
                "seat_from": "electorate",
                "chamber": "lower",
                "vacancy_chambers": {"Assembly", "lower"},
            },
            "state": {
                "file": "nsw_state.json",
                "expected": 1,
                "seat_from": "region",
                "chamber": "upper",
                "vacancy_chambers": {"Council", "upper"},
            },
        },
    },
    {
        "label": "qld",
        "members": ROOT / "data" / "qld" / "members.json",
        "layers": {
            "districts": {
                "file": "qld_districts.json",
                "expected": 93,
                "seat_from": "electorate",
                "chamber": "lower",
                "vacancy_chambers": {"Assembly", "lower"},
            },
        },
    },
]


def main() -> int:
    errors: list[str] = []
    print("=== validate_boundaries ===")

    for check in CHECKS:
        if not check["members"].exists():
            errors.append(f"{check['label']}: missing {check['members'].relative_to(ROOT)}")
            continue
        members = json.loads(check["members"].read_text(encoding="utf-8"))
        for key, layer in check["layers"].items():
            path = BDIR / layer["file"]
            seat_key = layer["seat_from"]
            seats = {
                m[seat_key]
                for m in members["members"]
                if m.get("chamber") == layer["chamber"] and m.get(seat_key)
            }
            seats |= {
                v[seat_key]
                for v in members.get("vacancies", [])
                if v.get("chamber") in layer["vacancy_chambers"] and v.get(seat_key)
            }

            if not path.exists():
                errors.append(f"{check['label']}/{key}: missing {path.relative_to(ROOT)}")
                continue
            doc = json.loads(path.read_text(encoding="utf-8"))
            for k in REQUIRED:
                if not doc.get(k):
                    errors.append(f"{check['label']}/{key}: missing {k}")
            feats = doc.get("features", [])
            names = [f.get("name") for f in feats]
            if len(feats) != layer["expected"]:
                errors.append(
                    f"{check['label']}/{key}: {len(feats)} features != {layer['expected']}"
                )
            if len(set(names)) != len(names):
                errors.append(f"{check['label']}/{key}: duplicate names")
            geo, data = set(names), seats
            if geo - data:
                errors.append(
                    f"{check['label']}/{key}: in boundaries but not members: "
                    f"{sorted(geo - data)[:10]}"
                )
            if data - geo:
                errors.append(
                    f"{check['label']}/{key}: in members but no boundary: "
                    f"{sorted(data - geo)[:10]}"
                )
            vb = doc.get("viewBox", [0, 0, 0, 0])
            for f in feats:
                if not PATH_RE.match(f.get("d", "")):
                    errors.append(f"{check['label']}/{key}/{f.get('name')}: malformed path")
                b = f.get("bbox", [])
                if (
                    len(b) != 4
                    or b[0] > b[2]
                    or b[1] > b[3]
                    or b[0] < vb[0] - 1
                    or b[3] > vb[3] + 1
                ):
                    errors.append(f"{check['label']}/{key}/{f.get('name')}: bad bbox {b}")
            size = path.stat().st_size / 1024
            print(
                f"{check['label']}/{key}: {len(feats)}/{layer['expected']} features, "
                f"{len(geo & data)} matched, {size:.0f} KB, licence={doc.get('licence')}"
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
