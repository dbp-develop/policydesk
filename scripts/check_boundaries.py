#!/usr/bin/env python3
"""Yearly check: are our electoral boundaries still the current ones? (stdlib only)

Victoria: Vicmap WFS layer year and district/region names.
Federal: the national ESRI zip linked on the AEC download page.
NSW, QLD, WA, SA, TAS, ACT, NT: the GDA2020 Esri zip on the data.gov.au
dataset each build script already uses. A new resource URL means a new
Geoscape release (which is how a redistribution is published).

Exit 0 = still current. Exit 1 = boundaries need updating. Exit 2 = the check itself failed
(network error, service moved). The workflow opens an issue for 1 or 2.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request

import guards
import build_act_boundaries
import build_federal_boundaries
import build_nsw_boundaries
import build_nt_boundaries
import build_qld_boundaries
import build_sa_boundaries
import build_tas_boundaries
import build_wa_boundaries
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
        return guards.read_checked(resp, url)


GEOSCAPE = (
    ("NSW", build_nsw_boundaries),
    ("QLD", build_qld_boundaries),
    ("WA", build_wa_boundaries),
    ("SA", build_sa_boundaries),
    ("TAS", build_tas_boundaries),
    ("ACT", build_act_boundaries),
    ("NT", build_nt_boundaries),
)
FEDERAL_PAGE = "https://www.aec.gov.au/electorates/gis/gis_datadownload.htm"
FEDERAL_ZIP = "AUS-March-2025-esri.zip"


def check_vic() -> list[str]:
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
    return problems


def check_federal() -> list[str]:
    page = get(FEDERAL_PAGE).decode("utf-8", "replace")
    hrefs = re.findall(r'href="([^"]+)"', page, re.I)
    national = []
    for href in hrefs:
        path = urllib.parse.urlparse(href).path or href
        if re.search(r"/Electorates/files/\d{4}/AUS-.*-esri\.zip$", path, re.I):
            national.append(path)
    print("Federal national ESRI zips:", ", ".join(national) or "none found")
    problems = []
    if not any(path.endswith(FEDERAL_ZIP) for path in national):
        problems.append(
            f"AEC download page no longer links {FEDERAL_ZIP} "
            f"({build_federal_boundaries.ZIP_URL})."
        )
    extra = [path for path in national if not path.endswith(FEDERAL_ZIP)]
    if extra:
        problems.append(f"AEC download page links a different national ESRI zip: {extra}.")
    return problems


def published_gda2020(package: dict) -> str | None:
    found = []
    for item in package.get("resources") or []:
        name = item.get("name") or ""
        url = item.get("url") or ""
        if (
            "gda2020" in url.lower()
            and url.lower().endswith(".zip")
            and "esri" in name.lower()
        ):
            found.append((item.get("last_modified") or "", url))
    if not found:
        return None
    found.sort()
    return found[-1][1]


def check_geoscape(label: str, mod) -> list[str]:
    slug = mod.DATASET_URL.rstrip("/").rsplit("/", 1)[-1]
    api = "https://data.gov.au/data/api/3/action/package_show?id=" + urllib.parse.quote(slug)
    payload = json.loads(get(api).decode("utf-8"))
    if not payload.get("success"):
        raise RuntimeError(f"{label}: data.gov.au package_show was not successful")
    live = published_gda2020(payload["result"])
    pinned = mod.ZIP_URL
    print(f"{label}: published GDA2020 Esri {live}")
    if not live:
        raise RuntimeError(f"{label}: no GDA2020 Esri zip on {mod.DATASET_URL}")
    if live != pinned:
        return [
            f"{label}: data.gov.au GDA2020 Esri zip differs from scripts/build_{label.lower()}_boundaries.py "
            f"({live})."
        ]
    return []


def main() -> int:
    problems: list[str] = []
    failures: list[str] = []

    def run(label: str, fn) -> None:
        try:
            problems.extend(fn())
        except Exception as exc:  # noqa: BLE001 - one source must not hide the others
            failures.append(f"{label}: {type(exc).__name__}: {exc}")
            print(f"CHECK FAILED for {label}: {type(exc).__name__}: {exc}")

    run("Victoria", check_vic)
    run("Federal", check_federal)
    for label, mod in GEOSCAPE:
        run(label, lambda mod=mod, label=label: check_geoscape(label, mod))

    if problems:
        print("ACTION NEEDED:")
        for item in problems:
            print(f"  - {item}")
        if failures:
            print("ALSO COULD NOT CHECK:")
            for item in failures:
                print(f"  - {item}")
        print("Rebuild the boundary script for that parliament, then update docs/data-sources.md.")
        return 1
    if failures:
        print("CHECK FAILED:")
        for item in failures:
            print(f"  - {item}")
        return 2
    print("OK: boundaries are still current.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - report any failure as "check failed"
        print(f"CHECK FAILED: {type(exc).__name__}: {exc}")
        sys.exit(2)
