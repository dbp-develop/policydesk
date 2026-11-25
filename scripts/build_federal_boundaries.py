#!/usr/bin/env python3
"""Build simplified Federal boundary JSON for the map (stdlib only).

House: AEC national ESRI shapefile for the 2025 federal election
  (AUS-March-2025-esri.zip from aec.gov.au/electorates/gis/).
Senate: state/territory shapes by grouping House divisions using the
  sitting member's state from data/federal/members.json.

Writes data/boundaries/federal_divisions.json and federal_states.json.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import struct
import sys
import time
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import guards

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "boundaries"
MEMBERS = ROOT / "data" / "federal" / "members.json"
USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
ZIP_URL = "https://www.aec.gov.au/Electorates/files/2025/AUS-March-2025-esri.zip"
DATASET_URL = "https://www.aec.gov.au/electorates/gis/gis_datadownload.htm"
LICENCE_URL = "https://www.aec.gov.au/Electorates/gis/licence.htm"

LAT_MID = -25.0
COS_MID = math.cos(math.radians(LAT_MID))
WIDTH = 10000
TOLERANCE = 2.5  # SVG units (~ few km at national scale)
MIN_RING_AREA = 8.0

STATE_FULL = {
    "NSW": "New South Wales",
    "VIC": "Victoria",
    "QLD": "Queensland",
    "WA": "Western Australia",
    "SA": "South Australia",
    "TAS": "Tasmania",
    "ACT": "Australian Capital Territory",
    "NT": "Northern Territory",
}


def fetch_zip() -> bytes:
    req = urllib.request.Request(ZIP_URL, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return guards.read_checked(resp, ZIP_URL, limit=guards.MAX_BOUNDARY)
        except Exception as exc:  # noqa: BLE001
            print(f"fetch zip attempt {attempt} failed: {exc}", file=sys.stderr)
            time.sleep(5 * attempt)
    raise SystemExit("ERROR: could not download AEC national boundaries zip")


def read_dbf(data: bytes) -> list[dict]:
    nrecords = struct.unpack_from("<I", data, 4)[0]
    header_len = struct.unpack_from("<H", data, 8)[0]
    record_len = struct.unpack_from("<H", data, 10)[0]
    fields = []
    offset = 32
    while data[offset] != 0x0D:
        name = data[offset : offset + 11].split(b"\0", 1)[0].decode("ascii", "replace")
        typ = chr(data[offset + 11])
        length = data[offset + 16]
        fields.append((name, typ, length))
        offset += 32
    rows = []
    pos = header_len
    for _ in range(nrecords):
        rec = data[pos + 1 : pos + record_len]
        o = 0
        row = {}
        for name, typ, length in fields:
            row[name] = rec[o : o + length].decode("latin1", "replace").strip()
            o += length
        rows.append(row)
        pos += record_len
    return rows


def read_shp_polygons(data: bytes) -> list[list[list[tuple[float, float]]]]:
    """Return list of polygons; each polygon is list of rings; ring is lon/lat pairs."""
    if struct.unpack_from(">i", data, 0)[0] != 9994:
        raise ValueError("not a shapefile")
    shape_type = struct.unpack_from("<i", data, 32)[0]
    if shape_type not in (5, 15):  # Polygon / PolygonZ
        raise ValueError(f"unsupported shape type {shape_type}")
    features: list[list[list[tuple[float, float]]]] = []
    pos = 100
    while pos + 8 <= len(data):
        _rec_num = struct.unpack_from(">i", data, pos)[0]
        content_len = struct.unpack_from(">i", data, pos + 4)[0] * 2
        pos += 8
        end = pos + content_len
        st = struct.unpack_from("<i", data, pos)[0]
        if st == 0:  # null
            features.append([])
            pos = end
            continue
        if st not in (5, 15):
            raise ValueError(f"record shape type {st}")
        # bbox 4 doubles, then numParts, numPoints
        num_parts = struct.unpack_from("<i", data, pos + 36)[0]
        num_points = struct.unpack_from("<i", data, pos + 40)[0]
        parts = list(struct.unpack_from(f"<{num_parts}i", data, pos + 44))
        pts_off = pos + 44 + 4 * num_parts
        coords = struct.unpack_from(f"<{num_points * 2}d", data, pts_off)
        points = [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]
        parts.append(num_points)
        rings = [points[parts[i] : parts[i + 1]] for i in range(num_parts)]
        features.append(rings)
        pos = end
    return features


def rings_as_polygons(rings: list[list[tuple[float, float]]]):
    """Yield each ring (outer + holes treated as separate paths for SVG)."""
    yield from rings


def bounds_of(geoms: list[list[list[tuple[float, float]]]]) -> tuple[float, float, float, float]:
    xs, ys = [], []
    for rings in geoms:
        for ring in rings:
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
    return project, height, 111.32 / scale


def dp(points: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
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
    return abs(
        sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]))
    ) / 2


def ring_to_path(ring: list[tuple[int, int]]) -> str:
    out = [f"M{ring[0][0]} {ring[0][1]}"]
    px, py = ring[0]
    parts = []
    for x, y in ring[1:]:
        parts.append(f"{x - px} {y - py}")
        px, py = x, y
    out.append("l" + " ".join(parts))
    out.append("z")
    return "".join(out)


def build_feature(name: str, rings: list[list[tuple[float, float]]], project) -> dict | None:
    paths = []
    xs, ys = [], []
    for ring in rings:
        pts = [project(lon, lat) for lon, lat in ring]
        if pts and pts[0] == pts[-1]:
            pts = pts[:-1]
        if len(pts) < 3 or area(pts) < MIN_RING_AREA:
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
    return {"name": name, "d": "".join(paths), "bbox": [min(xs), min(ys), max(xs), max(ys)]}


def fold_name(name: str) -> str:
    """Case-fold division names so AEC 'Mcewen' matches handbook 'McEwen'."""
    return re.sub(r"[^a-z0-9]+", "", name.casefold())


def load_division_states() -> dict[str, str]:
    """Map folded House division name -> full state/territory name."""
    data = json.loads(MEMBERS.read_text(encoding="utf-8"))
    out = {}
    for m in data["members"]:
        if m.get("chamber") != "lower":
            continue
        el = m.get("electorate")
        st = m.get("state")
        if el and st and st in STATE_FULL:
            out[fold_name(el)] = STATE_FULL[st]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-zip", dest="zip_path", help="local AUS-March-2025-esri.zip")
    args = ap.parse_args()

    if not MEMBERS.exists():
        print(f"ERROR: missing {MEMBERS.relative_to(ROOT)}", file=sys.stderr)
        return 1

    print("Loading AEC national boundaries…")
    raw = Path(args.zip_path).read_bytes() if args.zip_path else fetch_zip()
    with zipfile.ZipFile(BytesIO(raw)) as zf:
        names = zf.namelist()
        shp_name = next(n for n in names if n.lower().endswith(".shp"))
        dbf_name = next(n for n in names if n.lower().endswith(".dbf"))
        shp = guards.read_zip_member(zf, shp_name)
        dbf = guards.read_zip_member(zf, dbf_name)

    attrs = read_dbf(dbf)
    geoms = read_shp_polygons(shp)
    if len(attrs) != len(geoms):
        print(f"ERROR: {len(attrs)} dbf rows != {len(geoms)} shapes", file=sys.stderr)
        return 1

    divisions = []
    for row, rings in zip(attrs, geoms):
        name = (row.get("Elect_div") or row.get("Sortname") or "").strip()
        if not name:
            print("ERROR: division missing name", file=sys.stderr)
            return 1
        divisions.append((name, rings))

    if len(divisions) != 150:
        print(f"ERROR: expected 150 divisions, got {len(divisions)}", file=sys.stderr)
        return 1

    project, height, km_per_unit = make_projector(bounds_of([g for _, g in divisions]))
    fetched = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    div_state = load_division_states()
    missing = [n for n, _ in divisions if fold_name(n) not in div_state]
    if missing:
        print(f"ERROR: divisions with no member state: {missing}", file=sys.stderr)
        return 1

    # Prefer handbook electorate spelling so map names match members.json.
    handbook_names = {
        fold_name(m["electorate"]): m["electorate"]
        for m in json.loads(MEMBERS.read_text(encoding="utf-8"))["members"]
        if m.get("chamber") == "lower" and m.get("electorate")
    }

    div_feats = []
    for name, rings in divisions:
        canon = handbook_names.get(fold_name(name), name)
        feat = build_feature(canon, rings, project)
        if feat is None:
            print(f"ERROR: lost geometry for {canon}", file=sys.stderr)
            return 1
        div_feats.append(feat)
    div_feats.sort(key=lambda f: f["name"])

    credit = (
        "This product (The Policy Desk AU map) incorporates data that is: "
        "© Commonwealth of Australia (Australian Electoral Commission) 2026. "
        "The Data (Commonwealth Electoral Boundaries, March 2025 national file) "
        "has been used with the permission of the Australian Electoral Commission "
        "under the AEC data download licence. Simplified by The Policy Desk AU."
    )
    modified = (
        f"Simplified (Douglas-Peucker, ~{TOLERANCE * km_per_unit * 1000:.0f} m "
        f"tolerance), slivers under ~{MIN_RING_AREA * km_per_unit ** 2 * 1e6:.0f} m² "
        "dropped, projected to SVG units"
    )
    common = {
        "source": "Australian Electoral Commission",
        "dataset": "Commonwealth Electoral Boundaries — National March 2025 (ESRI)",
        "dataset_url": DATASET_URL,
        "licence": "AEC data download licence",
        "licence_url": LICENCE_URL,
        "credit": credit,
        "boundary_version": "National boundaries for the 2025 federal election (AUS-March-2025)",
        "modified": modified,
        "fetched_at": fetched,
        "viewBox": [0, 0, WIDTH, round(height)],
    }

    div_doc = {**common, "features": div_feats}
    div_out = OUT_DIR / "federal_divisions.json"
    div_out.write_text(json.dumps(div_doc, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(f"{div_out.relative_to(ROOT)}: {len(div_feats)} features, {div_out.stat().st_size / 1024:.0f} KB")

    by_state: dict[str, list[list[tuple[float, float]]]] = defaultdict(list)
    for name, rings in divisions:
        by_state[div_state[fold_name(name)]].extend(rings)

    state_feats = []
    for state_name in sorted(STATE_FULL.values()):
        rings = by_state.get(state_name) or []
        feat = build_feature(state_name, rings, project)
        if feat is None:
            print(f"ERROR: lost state geometry for {state_name}", file=sys.stderr)
            return 1
        state_feats.append(feat)

    if len(state_feats) != 8:
        print(f"ERROR: expected 8 states/territories, got {len(state_feats)}", file=sys.stderr)
        return 1

    state_doc = {
        **common,
        "dataset": common["dataset"] + " (grouped to state/territory for Senate map)",
        "modified": modified + "; Senate shapes = union of House division rings by state",
        "features": state_feats,
    }
    state_out = OUT_DIR / "federal_states.json"
    state_out.write_text(json.dumps(state_doc, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(f"{state_out.relative_to(ROOT)}: {len(state_feats)} features, {state_out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
