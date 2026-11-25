#!/usr/bin/env python3
"""Build simplified WA boundary JSON for the map (stdlib only).

Assembly: Geoscape WA State Electoral Boundaries (CC BY 4.0) from data.gov.au,
EFF_START=20250308, SECL_CODE=2 (59 districts).

Council: the same release’s statewide Legislative Council polygon (SECL_CODE=3,
name LEGISLATIVE COUNCIL), labelled “Western Australia” to match member regions.

Writes data/boundaries/wa_districts.json and wa_state.json.
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
MEMBERS = ROOT / "data" / "wa" / "members.json"
USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
ZIP_URL = (
    "https://data.gov.au/data/dataset/c72845f8-45ff-4dd1-a955-87a32ee9d073/"
    "resource/8f74e43b-c287-4bb8-9eb9-34307e11a5aa/download/wa_seb_gda2020.zip"
)
DATASET_URL = (
    "https://data.gov.au/data/dataset/"
    "wa-state-electoral-boundaries-geoscape-administrative-boundaries"
)
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"

LAT_MID = -25.0
COS_MID = math.cos(math.radians(LAT_MID))
WIDTH = 10000
TOLERANCE = 1.5
MIN_RING_AREA = 4.0
EFF_START = "20250308"  # 2023 redistribution; in force from 2025 election
STATE_NAME = "Western Australia"
ASSEMBLY_SECL = "2"
COUNCIL_SECL = "3"


def fetch_zip() -> bytes:
    req = urllib.request.Request(ZIP_URL, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return guards.read_checked(resp, ZIP_URL, limit=guards.MAX_BOUNDARY)
        except Exception as exc:  # noqa: BLE001
            print(f"fetch zip attempt {attempt} failed: {exc}", file=sys.stderr)
            time.sleep(5 * attempt)
    raise SystemExit("ERROR: could not download WA Geoscape boundaries zip")


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
    if struct.unpack_from(">i", data, 0)[0] != 9994:
        raise ValueError("not a shapefile")
    shape_type = struct.unpack_from("<i", data, 32)[0]
    if shape_type not in (5, 15):
        raise ValueError(f"unsupported shape type {shape_type}")
    features: list[list[list[tuple[float, float]]]] = []
    pos = 100
    while pos + 8 <= len(data):
        content_len = struct.unpack_from(">i", data, pos + 4)[0] * 2
        pos += 8
        end = pos + content_len
        st = struct.unpack_from("<i", data, pos)[0]
        if st == 0:
            features.append([])
            pos = end
            continue
        if st not in (5, 15):
            raise ValueError(f"record shape type {st}")
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


def titlecase_district(name: str) -> str:
    # "COLLIE - PRESTON" / "MID - WEST" → Collie-Preston / Mid-West
    name = re.sub(r"\s*-\s*", "-", name.strip())
    return " ".join(w[:1] + w[1:].lower() if w else "" for w in name.split())


def fold(s: str) -> str:
    return "".join(ch for ch in (s or "").casefold() if ch.isalnum())


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-zip", dest="zip_path", help="local wa_seb_gda2020.zip")
    args = ap.parse_args()

    if not MEMBERS.exists():
        print(f"ERROR: missing {MEMBERS.relative_to(ROOT)}", file=sys.stderr)
        return 1

    members = json.loads(MEMBERS.read_text(encoding="utf-8"))
    seat_names = {
        m["electorate"]
        for m in members["members"]
        if m.get("chamber") == "lower" and m.get("electorate")
    }
    seat_by_fold = {fold(s): s for s in seat_names}
    if len(seat_names) != 59:
        print(
            f"ERROR: expected 59 Assembly seats in members, got {len(seat_names)}",
            file=sys.stderr,
        )
        return 1

    print("Loading WA Geoscape state electoral boundaries (2025/EFF_START 20250308)…")
    raw = Path(args.zip_path).read_bytes() if args.zip_path else fetch_zip()
    with zipfile.ZipFile(BytesIO(raw)) as zf:
        names = zf.namelist()
        poly_shp = next(n for n in names if n.endswith("POLYGON_shp.shp"))
        poly_dbf = next(n for n in names if n.endswith("POLYGON_shp.dbf"))
        name_dbf = next(
            n for n in names if n.endswith("ELECTORAL_shp.dbf") and "POLYGON" not in n
        )
        shp = guards.read_zip_member(zf, poly_shp)
        dbf = guards.read_zip_member(zf, poly_dbf)
        name_rows = read_dbf(guards.read_zip_member(zf, name_dbf))

    attrs = read_dbf(dbf)
    geoms = read_shp_polygons(shp)
    if len(attrs) != len(geoms):
        print(f"ERROR: {len(attrs)} polygon rows != {len(geoms)} shapes", file=sys.stderr)
        return 1

    pid_to_name: dict[str, str] = {}
    council_pids: set[str] = set()
    for row in name_rows:
        if row.get("EFF_START") != EFF_START:
            continue
        pid = (row.get("SE_PID") or "").strip()
        raw_name = (row.get("NAME") or "").strip()
        secl = (row.get("SECL_CODE") or "").strip()
        if not pid or not raw_name:
            continue
        if secl == COUNCIL_SECL:
            council_pids.add(pid)
            continue
        if secl != ASSEMBLY_SECL:
            continue
        titled = titlecase_district(raw_name)
        canon = seat_by_fold.get(fold(titled))
        if not canon:
            print(f"ERROR: boundary name {titled!r} not in members", file=sys.stderr)
            return 1
        pid_to_name[pid] = canon

    if len(pid_to_name) != 59:
        print(f"ERROR: expected 59 Assembly SE_PIDs, got {len(pid_to_name)}", file=sys.stderr)
        return 1
    if len(council_pids) != 1:
        print(
            f"ERROR: expected 1 Legislative Council SE_PID, got {len(council_pids)}",
            file=sys.stderr,
        )
        return 1

    by_name: dict[str, list[list[tuple[float, float]]]] = defaultdict(list)
    council_rings: list[list[tuple[float, float]]] = []
    for row, rings in zip(attrs, geoms):
        pid = (row.get("SE_PID") or "").strip()
        if pid in council_pids:
            council_rings.extend(rings)
            continue
        name = pid_to_name.get(pid)
        if not name:
            continue
        by_name[name].extend(rings)

    if set(by_name) != seat_names:
        print(
            f"ERROR: boundary names != members: "
            f"extra={sorted(set(by_name) - seat_names)[:10]} "
            f"missing={sorted(seat_names - set(by_name))[:10]}",
            file=sys.stderr,
        )
        return 1
    if not council_rings:
        print("ERROR: no Legislative Council geometry", file=sys.stderr)
        return 1

    all_rings = [rings for rings in by_name.values()] + [council_rings]
    project, height, km_per_unit = make_projector(bounds_of(all_rings))
    fetched = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dist_feats = []
    for name in sorted(by_name):
        feat = build_feature(name, by_name[name], project)
        if feat is None:
            print(f"ERROR: lost geometry for {name}", file=sys.stderr)
            return 1
        dist_feats.append(feat)

    credit = (
        "This product (The Policy Desk AU map) incorporates or was developed using "
        "Administrative Boundaries © Geoscape Australia licensed by the Commonwealth "
        "of Australia under Creative Commons Attribution 4.0 International licence "
        "(CC BY 4.0). Simplified by The Policy Desk AU. Western Australia Legislative "
        "Assembly districts and Legislative Council statewide boundary from the "
        "NOV26/FEB26 GDA2020 Geoscape release (2023 redistribution, EFF_START "
        "2025-03-08; in force from the 2025 state election)."
    )
    modified = (
        f"Simplified (Douglas-Peucker, ~{TOLERANCE * km_per_unit * 1000:.0f} m "
        f"tolerance), slivers under ~{MIN_RING_AREA * km_per_unit ** 2 * 1e6:.0f} m² "
        "dropped, projected to SVG units"
    )
    common = {
        "source": "Geoscape Australia / Commonwealth of Australia (data.gov.au)",
        "dataset": (
            "WA State Electoral Boundaries — Geoscape Administrative Boundaries "
            "(GDA2020, EFF_START 2025-03-08)"
        ),
        "dataset_url": DATASET_URL,
        "licence": "CC BY 4.0",
        "licence_url": LICENCE_URL,
        "credit": credit,
        "boundary_version": (
            "2023 WA electoral redistribution (EFF_START 2025-03-08); "
            "in force from the 2025 state general election"
        ),
        "modified": modified,
        "fetched_at": fetched,
        "viewBox": [0, 0, WIDTH, round(height)],
    }

    dist_doc = {**common, "features": dist_feats}
    dist_out = OUT_DIR / "wa_districts.json"
    dist_out.write_text(json.dumps(dist_doc, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(f"{dist_out.relative_to(ROOT)}: {len(dist_feats)} features, {dist_out.stat().st_size / 1024:.0f} KB")

    state_feat = build_feature(STATE_NAME, council_rings, project)
    if state_feat is None:
        print("ERROR: lost statewide WA Legislative Council geometry", file=sys.stderr)
        return 1

    state_doc = {
        **common,
        "dataset": common["dataset"] + " (Legislative Council statewide polygon)",
        "modified": modified + "; Council shape = Geoscape LEGISLATIVE COUNCIL feature",
        "features": [state_feat],
    }
    state_out = OUT_DIR / "wa_state.json"
    state_out.write_text(json.dumps(state_doc, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(f"{state_out.relative_to(ROOT)}: 1 feature, {state_out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
