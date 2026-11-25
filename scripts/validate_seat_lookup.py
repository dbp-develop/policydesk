#!/usr/bin/env python3
"""Validate data/seat_lookup against member seat names (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "seat_lookup" / "index.json"

STATE_TO_KEY = {
    "VIC": "vic",
    "NSW": "nsw",
    "QLD": "qld",
    "WA": "wa",
    "SA": "sa",
    "TAS": "tas",
    "ACT": "act",
    "NT": "nt",
}

MEMBERS = {
    "vic": ROOT / "data" / "members.json",
    "nsw": ROOT / "data" / "nsw" / "members.json",
    "qld": ROOT / "data" / "qld" / "members.json",
    "wa": ROOT / "data" / "wa" / "members.json",
    "sa": ROOT / "data" / "sa" / "members.json",
    "tas": ROOT / "data" / "tas" / "members.json",
    "act": ROOT / "data" / "act" / "members.json",
    "nt": ROOT / "data" / "nt" / "members.json",
    "federal": ROOT / "data" / "federal" / "members.json",
}


def fold(name: str) -> str:
    s = (name or "").lower().strip()
    s = s.replace("’", "'").replace("`", "'")
    return re.sub(r"\s+", " ", s)


def lower_seats(path: Path) -> set[str]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    seats = {
        fold(m["electorate"])
        for m in doc.get("members") or []
        if m.get("chamber") == "lower" and m.get("electorate")
    }
    for v in doc.get("vacancies") or []:
        if v.get("electorate"):
            seats.add(fold(v["electorate"]))
    return seats


def main() -> int:
    errors: list[str] = []
    if not INDEX.is_file():
        print(f"ERROR: missing {INDEX}")
        return 1

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    for field in ("source", "source_url", "licence", "licence_url", "postcodes", "note"):
        if not index.get(field):
            errors.append(f"index missing {field}")

    if index.get("licence") != "CC BY 4.0":
        errors.append(f"unexpected licence {index.get('licence')!r}")

    fed_seats = lower_seats(MEMBERS["federal"])
    state_seats = {k: lower_seats(p) for k, p in MEMBERS.items() if k != "federal"}

    postcodes = index.get("postcodes") or {}
    if len(postcodes) < 2000:
        errors.append(f"too few postcodes: {len(postcodes)}")

    for pc, entry in postcodes.items():
        if not re.fullmatch(r"\d{4}", pc):
            errors.append(f"bad postcode key {pc!r}")
        if "source" not in entry:
            errors.append(f"{pc}: missing source")
        if entry.get("ambiguous"):
            if not entry.get("suburbs"):
                errors.append(f"{pc}: ambiguous but no suburbs to disambiguate")
            elif not entry.get("states"):
                errors.append(f"{pc}: ambiguous entry missing states")
            continue
        fed = entry.get("federal") or []
        st = entry.get("state") or []
        if len(fed) != 1 or len(st) != 1:
            errors.append(f"{pc}: unambiguous but seat counts federal={len(fed)} state={len(st)}")
            continue
        if fold(fed[0]["name"]) not in fed_seats:
            errors.append(f"{pc}: federal seat {fed[0]['name']!r} not in members")
        parl = st[0].get("parliament")
        if parl not in state_seats:
            errors.append(f"{pc}: bad parliament {parl!r}")
        elif fold(st[0]["name"]) not in state_seats[parl]:
            errors.append(f"{pc}: state seat {st[0]['name']!r} not in {parl} members")

    # Spot-check known postcodes exist (ambiguous flag follows source CSV).
    for pc in ("2000", "2600", "3000", "0800", "4000"):
        if pc not in postcodes:
            errors.append(f"expected postcode {pc} missing")

    # Suburb files
    suburb_files = index.get("suburb_files") or {}
    for st, key in STATE_TO_KEY.items():
        rel = suburb_files.get(key)
        if not rel:
            errors.append(f"missing suburb_files entry for {key}")
            continue
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing suburb file {path}")
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("source_url") != index.get("source_url"):
            errors.append(f"{path.name}: source_url mismatch")
        suburbs = doc.get("suburbs") or {}
        if len(suburbs) < 50 and key not in ("act", "nt"):
            errors.append(f"{path.name}: too few suburbs ({len(suburbs)})")
        for skey, rec in suburbs.items():
            if not rec.get("source"):
                errors.append(f"{path.name}:{skey}: missing source")
            for seat in rec.get("federal") or []:
                if fold(seat["name"]) not in fed_seats:
                    errors.append(f"{path.name}:{skey}: federal {seat['name']!r} unknown")
            for seat in rec.get("state_seats") or []:
                if fold(seat["name"]) not in state_seats[key]:
                    errors.append(f"{path.name}:{skey}: state {seat['name']!r} unknown in {key}")

    # Melbourne CBD should resolve via suburb file
    vic = json.loads((ROOT / "data/seat_lookup/suburbs-vic.json").read_text(encoding="utf-8"))
    mel = (vic.get("suburbs") or {}).get("melbourne")
    if not mel:
        errors.append("vic suburbs missing melbourne")
    else:
        fed_names = {fold(x["name"]) for x in mel.get("federal") or []}
        if "melbourne" not in fed_names:
            errors.append("melbourne suburb missing federal Melbourne")

    if errors:
        print(f"FAIL: {len(errors)} error(s)")
        for e in errors[:40]:
            print(" ", e)
        if len(errors) > 40:
            print(f"  … and {len(errors) - 40} more")
        return 1

    print(
        f"OK seat_lookup: {len(postcodes)} postcodes, "
        f"{sum(1 for p in postcodes.values() if p.get('ambiguous'))} ambiguous, "
        f"source={index.get('source_url')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
