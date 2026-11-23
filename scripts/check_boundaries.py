#!/usr/bin/env python3
"""Yearly check: are our electoral boundaries still the current ones? (stdlib only)

1. Lists the state boundary layers on the Vicmap open-data WFS. A layer newer
   than the one we use (e.g. state_assembly_2030) means a redivision has been
   published and data/boundaries must be rebuilt.
2. Fetches only the names (no shapes) of the layer we use and checks they
   still match data/boundaries/*.json.

Exit 0 = still current. Exit 1 = boundaries need updating. Exit 2 = the check itself failed
(network error, service moved). The workflow opens an issue for 1 or 2.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
WFS = "https://opendata.maps.vic.gov.au/geoserver/wfs"
CURRENT = {"assembly": 2022, "council": 2022}
FILES = {
    "assembly": ("vic_districts.json", "district_label", " District"),
    "council": ("vic_regions.json", "region_label", " Region"),
}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def main() -> int:
    problems: list[str] = []
    caps = get(f"{WFS}?service=WFS&version=2.0.0&request=GetCapabilities").decode("utf-8", "replace")
    layers = sorted(set(re.findall(r"open-data-platform:state_(assembly|council)_(\d{4})", caps)))
    print("Boundary layers on the WFS:", ", ".join(f"{k}_{y}" for k, y in layers) or "none found")
    if not layers:
        problems.append("No state boundary layers found on the WFS. The service may have moved.")

    for kind, year in CURRENT.items():
        newer = [int(y) for k, y in layers if k == kind and int(y) > year]
        if newer:
            problems.append(f"Newer {kind} boundaries published: state_{kind}_{max(newer)} (we use {year}).")

        fname, label_key, suffix = FILES[kind]
        url = (f"{WFS}?service=WFS&version=2.0.0&request=GetFeature"
               f"&typeNames=open-data-platform:state_{kind}_{year}"
               f"&propertyName={label_key}&outputFormat=application/json")
        live = {f["properties"][label_key].removesuffix(suffix) for f in json.loads(get(url))["features"]}
        ours = {f["name"] for f in json.loads((ROOT / "data" / "boundaries" / fname).read_text())["features"]}
        print(f"{kind}_{year}: {len(live)} live names, {len(ours)} in {fname}")
        if live != ours:
            problems.append(f"{fname} differs from the live layer: "
                            f"missing {sorted(live - ours)}, extra {sorted(ours - live)}.")

    if problems:
        print("ACTION NEEDED:")
        for p in problems:
            print(f"  - {p}")
        print("Rebuild with: python3 scripts/build_boundaries.py, then update docs/data-sources.md.")
        return 1
    print("OK: boundaries are still current.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - report any failure as "check failed"
        print(f"CHECK FAILED: {type(exc).__name__}: {exc}")
        sys.exit(2)
