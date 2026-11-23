#!/usr/bin/env python3
"""Validate data/boundaries/*.json against data/members.json (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BDIR = ROOT / "data" / "boundaries"
MEMBERS = ROOT / "data" / "members.json"

REQUIRED = ("source", "dataset", "dataset_url", "licence", "licence_url", "credit",
            "boundary_version", "fetched_at", "viewBox", "features")
PATH_RE = re.compile(r"^(M-?\d+ -?\d+l(-?\d+ -?\d+ ?)+z)+$")


def main() -> int:
    errors: list[str] = []
    members = json.loads(MEMBERS.read_text(encoding="utf-8"))
    seats = {
        "districts": {m["electorate"] for m in members["members"] if m["chamber"] == "lower"}
        | {v["electorate"] for v in members.get("vacancies", []) if v.get("chamber") in ("Assembly", "lower")},
        "regions": {m["region"] for m in members["members"] if m["chamber"] == "upper"},
    }
    expected = {"districts": 88, "regions": 8}

    print("=== validate_boundaries ===")
    for key in ("districts", "regions"):
        path = BDIR / f"vic_{key}.json"
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        for k in REQUIRED:
            if not doc.get(k):
                errors.append(f"{key}: missing {k}")
        feats = doc.get("features", [])
        names = [f.get("name") for f in feats]
        if len(feats) != expected[key]:
            errors.append(f"{key}: {len(feats)} features != {expected[key]}")
        if len(set(names)) != len(names):
            errors.append(f"{key}: duplicate names")
        geo, data = set(names), seats[key]
        if geo - data:
            errors.append(f"{key}: in boundaries but not members.json: {sorted(geo - data)}")
        if data - geo:
            errors.append(f"{key}: in members.json but no boundary: {sorted(data - geo)}")
        vb = doc.get("viewBox", [0, 0, 0, 0])
        for f in feats:
            if not PATH_RE.match(f.get("d", "")):
                errors.append(f"{key}/{f.get('name')}: malformed path")
            b = f.get("bbox", [])
            if len(b) != 4 or b[0] > b[2] or b[1] > b[3] or b[0] < vb[0] - 1 or b[3] > vb[3] + 1:
                errors.append(f"{key}/{f.get('name')}: bad bbox {b}")
        size = path.stat().st_size / 1024
        print(f"{key}: {len(feats)}/{expected[key]} features, {len(geo & data)} matched to members.json, "
              f"{size:.0f} KB, licence={doc.get('licence')}")

    if errors:
        print(f"FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
