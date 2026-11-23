#!/usr/bin/env python3
"""Build simplified SVG boundary files for the map view (stdlib only).

Source: Vicmap Admin - State Assembly Polygon 2022 and State Council Polygon 2022,
published by the Victorian Electoral Commission on DataVic under CC BY 4.0.
Fetched from the Vicmap open-data WFS as GeoJSON (EPSG:4326).

Writes data/boundaries/vic_districts.json and data/boundaries/vic_regions.json.
Each feature is a pre-projected SVG path in a shared coordinate space, so the
browser draws the map without any map library or external tiles.

Usage:
  python3 scripts/build_boundaries.py               # fetch from WFS
  python3 scripts/build_boundaries.py --from DIR    # use DIR/state_assembly_2022.json etc.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "boundaries"
USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
WFS = (
    "https://opendata.maps.vic.gov.au/geoserver/wfs?service=WFS&version=2.0.0"
    "&request=GetFeature&typeNames=open-data-platform:{layer}"
    "&outputFormat=application/json&srsName=EPSG:4326"
)

LAYERS = {
    "districts": {
        "layer": "state_assembly_2022",
        "label_key": "district_label",
        "suffix": " District",
        "title": "Vicmap Admin - State Assembly Polygon 2022",
        "dataset_url": "https://discover.data.vic.gov.au/dataset/vicmap-admin-state-assembly-polygon-2022",
        "expected": 88,
    },
    "regions": {
        "layer": "state_council_2022",
        "label_key": "region_label",
        "suffix": " Region",
        "title": "Vicmap Admin - State Council Polygon 2022",
        "dataset_url": "https://discover.data.vic.gov.au/dataset/vicmap-admin-state-council-polygon-2022",
        "expected": 8,
    },
}

# Shared projection so districts and regions line up.
# Simple equirectangular projection centred on Victoria; fine at state scale.
LAT_MID = -37.0
COS_MID = math.cos(math.radians(LAT_MID))
WIDTH = 10000           # SVG units across the bounding box
TOLERANCE = 1.2         # Douglas-Peucker tolerance in SVG units (~100 m)
MIN_RING_AREA = 4.0     # drop slivers/islets smaller than this (SVG units²)


def fetch(layer: str) -> dict:
    url = WFS.format(layer=layer)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.load(resp)
        except Exception as exc:  # noqa: BLE001 - report and retry
            print(f"fetch {layer} attempt {attempt} failed: {exc}", file=sys.stderr)
            time.sleep(5 * attempt)
    raise SystemExit(f"ERROR: could not fetch {layer}")


def rings_of(geom: dict):
    if geom["type"] == "Polygon":
        yield from geom["coordinates"]
    elif geom["type"] == "MultiPolygon":
        for poly in geom["coordinates"]:
            yield from poly
    else:
        raise ValueError(f"unsupported geometry {geom['type']}")


def bounds(collections: list[dict]) -> tuple[float, float, float, float]:
    xs, ys = [], []
    for fc in collections:
        for f in fc["features"]:
            for ring in rings_of(f["geometry"]):
                for lon, lat in ring:
                    xs.append(lon)
                    ys.append(lat)
    return min(xs), min(ys), max(xs), max(ys)


def make_projector(b):
    min_lon, min_lat, max_lon, max_lat = b
    span_x = (max_lon - min_lon) * COS_MID
    scale = WIDTH / span_x

    def project(lon: float, lat: float) -> tuple[float, float]:
        return ((lon - min_lon) * COS_MID * scale, (max_lat - lat) * scale)

    height = (max_lat - min_lat) * scale
    return project, height, 111.32 / scale  # km per SVG unit


def dp(points: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    """Iterative Douglas-Peucker."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        s, e = stack.pop()
        (x1, y1), (x2, y2) = points[s], points[e]
        dx, dy = x2 - x1, y2 - y1
        norm = math.hypot(dx, dy)
        best, idx = -1.0, -1
        for i in range(s + 1, e):
            px, py = points[i]
            if norm == 0:
                d = math.hypot(px - x1, py - y1)
            else:
                d = abs(dy * px - dx * py + x2 * y1 - y2 * x1) / norm
            if d > best:
                best, idx = d, i
        if best > tol and idx > 0:
            keep[idx] = True
            stack.append((s, idx))
            stack.append((idx, e))
    return [p for p, k in zip(points, keep) if k]


def area(ring: list[tuple[float, float]]) -> float:
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]))) / 2


def ring_to_path(ring: list[tuple[int, int]]) -> str:
    """Absolute first point, then relative integer moves."""
    out = [f"M{ring[0][0]} {ring[0][1]}"]
    px, py = ring[0]
    parts = []
    for x, y in ring[1:]:
        parts.append(f"{x - px} {y - py}")
        px, py = x, y
    out.append("l" + " ".join(parts))
    out.append("z")
    return "".join(out)


def build_feature(f: dict, cfg: dict, project) -> dict | None:
    name = f["properties"][cfg["label_key"]].removesuffix(cfg["suffix"])
    paths = []
    xs, ys = [], []
    for ring in rings_of(f["geometry"]):
        pts = [project(lon, lat) for lon, lat in ring]
        if pts and pts[0] == pts[-1]:
            pts = pts[:-1]
        if area(pts) < MIN_RING_AREA:
            continue
        simp = dp(pts + [pts[0]], TOLERANCE)[:-1]
        q = []
        for x, y in simp:
            p = (round(x), round(y))
            if not q or q[-1] != p:
                q.append(p)
        if len(q) < 3:
            continue
        paths.append(ring_to_path(q))
        xs += [p[0] for p in q]
        ys += [p[1] for p in q]
    if not paths:
        return None
    return {
        "name": name,
        "d": "".join(paths),
        "bbox": [min(xs), min(ys), max(xs), max(ys)],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", help="directory with pre-downloaded GeoJSON")
    args = ap.parse_args()

    raw = {}
    for key, cfg in LAYERS.items():
        if args.src:
            raw[key] = json.loads((Path(args.src) / f"{cfg['layer']}.json").read_text())
        else:
            raw[key] = fetch(cfg["layer"])
            time.sleep(2)

    project, height, km_per_unit = make_projector(bounds(list(raw.values())))
    fetched = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ok = True
    for key, cfg in LAYERS.items():
        feats = [build_feature(f, cfg, project) for f in raw[key]["features"]]
        missing = [f["properties"][cfg["label_key"]] for f, b in zip(raw[key]["features"], feats) if b is None]
        feats = sorted((b for b in feats if b), key=lambda b: b["name"])
        if missing or len(feats) != cfg["expected"]:
            print(f"ERROR {key}: {len(feats)} features (expected {cfg['expected']}); lost: {missing}", file=sys.stderr)
            ok = False
        doc = {
            "source": "Victorian Electoral Commission, via DataVic",
            "dataset": cfg["title"],
            "dataset_url": cfg["dataset_url"],
            "licence": "CC BY 4.0",
            "licence_url": "https://creativecommons.org/licenses/by/4.0/",
            "credit": "Electoral boundaries: Victorian Electoral Commission, via DataVic (Vicmap Admin), CC BY 4.0. Simplified by The Policy Desk AU.",
            "boundary_version": "2020-21 State Redivision, in effect from 1 November 2022",
            "modified": f"Simplified (Douglas-Peucker, ~{TOLERANCE * km_per_unit * 1000:.0f} m tolerance), slivers under ~{MIN_RING_AREA * km_per_unit ** 2 * 1e6:.0f} m² dropped, projected to SVG units",
            "fetched_at": fetched,
            "viewBox": [0, 0, WIDTH, round(height)],
            "features": feats,
        }
        out = OUT_DIR / f"vic_{key}.json"
        out.write_text(json.dumps(doc, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{out.relative_to(ROOT)}: {len(feats)} features, {out.stat().st_size / 1024:.0f} KB")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
