#!/usr/bin/env python3
"""Minimal stub: placeholder Victorian members raw fetch for CI wiring."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "vic_raw.json"

PLACEHOLDER = {
    "source": "stub",
    "fetched_at": None,
    "members": [],
}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(PLACEHOLDER, indent=2) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print("=== Vic members fetch report (stub) ===")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"members: {len(PLACEHOLDER['members'])}")
    print("Note: stub only — replace with a real scraper when ready.")


if __name__ == "__main__":
    main()
