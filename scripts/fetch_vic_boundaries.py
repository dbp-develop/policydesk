#!/usr/bin/env python3
"""Fetch Vicmap 2022 state electoral boundaries and write a simplified GeoJSON.

Standard library only. Facts are district and region names plus geometry.
Source: Vicmap Admin via the public state electoral boundary map service
(CC BY 4.0). No photos, no biographies.

Writes data/vic_boundaries.json. Exits 1 if a district or region name does
not match data/members.json or data/vacancies.json.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "vic_boundaries.json"
MEMBERS = ROOT / "data" / "members.json"
VACANCIES = ROOT / "data" / "vacancies.json"

USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
SERVICE = (
    "https://spatial.planning.vic.gov.au/gis/rest/services/"
    "state_electoral_boundary/MapServer"
)
ASSEMBLY_LAYER = 4
COUNCIL_LAYER = 3
DATASET_URL = (
    "https://discover.data.vic.gov.au/dataset/"
    "vicmap-admin-state-assembly-polygon-2022"
)
ATTRIBUTION = (
    "State of Victoria (Victorian Electoral Commission). "
    "Vicmap Admin 2022 state electoral boundaries."
)
REQUEST_DELAY_SEC = 1.5


def http_get_json(url: str) -> dict:
    """GET JSON with a polite User-Agent, timeout, and up to 3 retries."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
            last_err = err
            print(f"  attempt {attempt}/3 failed: {err}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after 3 attempts: {last_err}")


def layer_url(layer: int, fields: str, offset: float) -> str:
    return (
        f"{SERVICE}/{layer}/query?where=1%3D1"
        f"&outFields={fields}"
        "&returnGeometry=true&outSR=4326"
        "&geometryPrecision=5"
        f"&maxAllowableOffset={offset}"
        "&f=geojson"
    )


def title_case(value: str) -> str:
    """Match parliament names: 'NORTH-EASTERN METROPOLITAN' -> that casing."""
    words = []
    for word in value.strip().split(" "):
        words.append("-".join(part.capitalize() for part in word.split("-")))
    return " ".join(words)


def perp_dist(point: tuple[float, float], start: tuple[float, float], end: tuple[float, float]) -> float:
    x, y = point
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
    t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    px, py = x1 + t * dx, y1 + t * dy
    return ((x - px) ** 2 + (y - py) ** 2) ** 0.5


def douglas_peucker(points: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    index = 0
    best = -1.0
    for i in range(1, len(points) - 1):
        dist = perp_dist(points[i], start, end)
        if dist > best:
            best = dist
            index = i
    if best > tol:
        left = douglas_peucker(points[: index + 1], tol)
        right = douglas_peucker(points[index:], tol)
        return left[:-1] + right
    return [start, end]


def ring_tolerance(ring: list[tuple[float, float]]) -> float:
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    diag = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2) ** 0.5
    # Keep city districts (short diagonals) at the server tolerance.
    # Simplify large rural rings more so the statewide file stays small.
    return max(0.00035, diag * 0.0035)


def simplify_ring(ring: list[list[float]]) -> list[list[float]] | None:
    pts = [(float(p[0]), float(p[1])) for p in ring if len(p) >= 2]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 3:
        return None
    simplified = douglas_peucker(pts, ring_tolerance(pts))
    if len(simplified) < 3:
        simplified = pts
    out: list[list[float]] = []
    for x, y in simplified:
        pair = [round(x, 4), round(y, 4)]
        if not out or pair != out[-1]:
            out.append(pair)
    if len(out) < 3:
        return None
    if out[0] != out[-1]:
        out.append(out[0])
    return out


def simplify_geometry(geom: dict) -> dict | None:
    gtype = geom.get("type")
    coords = geom.get("coordinates") or []
    if gtype == "Polygon":
        rings = [simplify_ring(ring) for ring in coords]
        rings = [ring for ring in rings if ring]
        if not rings:
            return None
        return {"type": "Polygon", "coordinates": rings}
    if gtype == "MultiPolygon":
        polygons = []
        for poly in coords:
            rings = [simplify_ring(ring) for ring in poly]
            rings = [ring for ring in rings if ring]
            if rings:
                polygons.append(rings)
        if not polygons:
            return None
        if len(polygons) == 1:
            return {"type": "Polygon", "coordinates": polygons[0]}
        return {"type": "MultiPolygon", "coordinates": polygons}
    raise ValueError(f"Unsupported geometry type: {gtype!r}")


def point_count(geom: dict | None) -> int:
    if not geom:
        return 0
    total = 0
    coords = geom["coordinates"]
    if geom["type"] == "Polygon":
        for ring in coords:
            total += len(ring)
    else:
        for poly in coords:
            for ring in poly:
                total += len(ring)
    return total


def span(geom: dict) -> tuple[float, float]:
    xs: list[float] = []
    ys: list[float] = []

    def take(ring: list[list[float]]) -> None:
        for x, y in ring:
            xs.append(x)
            ys.append(y)

    if geom["type"] == "Polygon":
        for ring in geom["coordinates"]:
            take(ring)
    else:
        for poly in geom["coordinates"]:
            for ring in poly:
                take(ring)
    return max(xs) - min(xs), max(ys) - min(ys)


def load_expected_names() -> tuple[set[str], set[str], set[str]]:
    members = json.loads(MEMBERS.read_text(encoding="utf-8"))["members"]
    vacancies = json.loads(VACANCIES.read_text(encoding="utf-8"))
    electorates = {m["electorate"] for m in members if m.get("electorate")}
    for vacancy in vacancies:
        if vacancy.get("chamber") in {"Assembly", "lower"} and vacancy.get("electorate"):
            electorates.add(vacancy["electorate"])
    regions = {m["region"] for m in members if m.get("region")}
    return electorates, regions, {m["region"] for m in members if m.get("chamber") == "lower" and m.get("region")}


def feature_collection(features: list[dict]) -> dict:
    return {"type": "FeatureCollection", "features": features}


def main() -> int:
    print("Fetching Assembly districts...")
    assembly_raw = http_get_json(
        layer_url(ASSEMBLY_LAYER, "DISTRICT,REGION", 0.00035)
    )
    time.sleep(REQUEST_DELAY_SEC)
    print("Fetching Council regions...")
    council_raw = http_get_json(layer_url(COUNCIL_LAYER, "REGION", 0.0008))

    if assembly_raw.get("error") or council_raw.get("error"):
        print("ERROR: map service returned an error", file=sys.stderr)
        print(assembly_raw.get("error") or council_raw.get("error"), file=sys.stderr)
        return 1

    electorates, regions, _lower_regions = load_expected_names()
    assembly_features: list[dict] = []
    council_features: list[dict] = []
    raw_points = 0
    out_points = 0
    errors: list[str] = []

    for feature in assembly_raw.get("features") or []:
        props = feature.get("properties") or {}
        raw_geom = feature.get("geometry") or {}
        raw_points += point_count(raw_geom)
        name = title_case(props.get("DISTRICT") or "")
        region = title_case(props.get("REGION") or "")
        geom = simplify_geometry(raw_geom)
        if geom is None:
            errors.append(f"{name or '?'}: empty geometry after simplify")
            continue
        out_points += point_count(geom)
        dx, dy = span(geom)
        if name == "Brunswick" and (dx < 0.03 or dy < 0.02):
            errors.append(f"Brunswick geometry collapsed (span {dx:.4f} x {dy:.4f})")
        assembly_features.append(
            {
                "type": "Feature",
                "properties": {"name": name, "region": region},
                "geometry": geom,
            }
        )

    for feature in council_raw.get("features") or []:
        props = feature.get("properties") or {}
        raw_geom = feature.get("geometry") or {}
        raw_points += point_count(raw_geom)
        name = title_case(props.get("REGION") or "")
        geom = simplify_geometry(raw_geom)
        if geom is None:
            errors.append(f"{name or '?'}: empty geometry after simplify")
            continue
        out_points += point_count(geom)
        council_features.append(
            {
                "type": "Feature",
                "properties": {"name": name},
                "geometry": geom,
            }
        )

    assembly_names = [f["properties"]["name"] for f in assembly_features]
    council_names = [f["properties"]["name"] for f in council_features]
    if len(assembly_names) != len(set(assembly_names)):
        errors.append("duplicate Assembly district names")
    if len(council_names) != len(set(council_names)):
        errors.append("duplicate Council region names")

    missing_seats = sorted(electorates - set(assembly_names))
    extra_seats = sorted(set(assembly_names) - electorates)
    missing_regions = sorted(regions - set(council_names))
    extra_regions = sorted(set(council_names) - regions)
    if missing_seats:
        errors.append(f"districts missing from boundaries: {missing_seats}")
    if extra_seats:
        errors.append(f"boundary districts not in member data: {extra_seats}")
    if missing_regions:
        errors.append(f"regions missing from boundaries: {missing_regions}")
    if extra_regions:
        errors.append(f"boundary regions not in member data: {extra_regions}")
    if len(assembly_features) != 88:
        errors.append(f"expected 88 Assembly districts, got {len(assembly_features)}")
    if len(council_features) != 8:
        errors.append(f"expected 8 Council regions, got {len(council_features)}")

    payload = {
        "source": "Vicmap Admin",
        "licence": "CC BY 4.0",
        "attribution": ATTRIBUTION,
        "source_url": DATASET_URL,
        "service_url": SERVICE,
        "fetched_at": datetime.now(timezone.utc).date().isoformat(),
        "assembly": feature_collection(assembly_features),
        "council": feature_collection(council_features),
    }
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(text + "\n", encoding="utf-8")

    print("=== Vic boundary fetch report ===")
    print(f"Assembly districts: {len(assembly_features)}")
    print(f"Council regions: {len(council_features)}")
    print(f"Points: {raw_points} raw -> {out_points} simplified")
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")
    if errors:
        print(f"FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
