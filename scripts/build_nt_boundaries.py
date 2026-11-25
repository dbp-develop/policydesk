#!/usr/bin/env python3
"""Build simplified NT boundary JSON for the map (stdlib only).

Legislative Assembly: Geoscape NT State Electoral Boundaries (CC BY 4.0),
SECL_CODE=2, EFF_START=20240824 — 25 single-member divisions.
Retired rows (EFF_END=20240823, including Nhulunbuy and Stuart) are not used.

Writes data/boundaries/nt_districts.json.
"""

from __future__ import annotations

import argparse
import json
import math
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
MEMBERS = ROOT / "data" / "nt" / "members.json"
USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
ZIP_URL = (
    "https://data.gov.au/data/dataset/19c0bd08-d8c7-42c8-953e-d9d1969f116b/"
    "resource/bedb117b-ea60-4842-b428-71d9fc827a29/download/nt_seb_gda2020.zip"
)
DATASET_URL = (
    "https://data.gov.au/data/dataset/"
    "nt-state-electoral-boundaries-geoscape-administrative-boundaries"
)
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"

LAT_MID = -19.5
COS_MID = math.cos(math.radians(LAT_MID))
WIDTH = 10000
TOLERANCE = 1.5
MIN_RING_AREA = 4.0
ASSEMBLY_SECL = "2"
EFF_START = "20240824"


def fetch_zip() -> bytes:
    req = urllib.request.Request(ZIP_URL, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return guards.read_checked(resp, ZIP_URL, limit=guards.MAX_BOUNDARY)
        except Exception as exc:  # noqa: BLE001
            print(f"fetch zip attempt {attempt} failed: {exc}", file=sys.stderr)
            time.sleep(5 * attempt)
    raise SystemExit("ERROR: could not download NT Geoscape boundaries zip")


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


def titlecase_name(name: str) -> str:
    name = name.strip()
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
    ap.add_argument("--from-zip", dest="zip_path", help="local nt_seb_gda2020.zip")
    args = ap.parse_args()

    if not MEMBERS.exists():
        print(f"ERROR: missing {MEMBERS.relative_to(ROOT)}", file=sys.stderr)
        return 1

    members = json.loads(MEMBERS.read_text(encoding="utf-8"))
    assembly_names = {
        m["electorate"]
        for m in members["members"]
        if m.get("chamber") == "lower" and m.get("electorate")
    }
    assembly_by_fold = {fold(s): s for s in assembly_names}
    if len(assembly_names) != 25:
        print(
            f"ERROR: expected 25 Assembly divisions in members, got {len(assembly_names)}",
            file=sys.stderr,
        )
        return 1

    print("Loading NT Geoscape state electoral boundaries…")
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

    pid_to_assembly: dict[str, str] = {}
    for row in name_rows:
        pid = (row.get("SE_PID") or "").strip()
        raw_name = (row.get("NAME") or "").strip()
        secl = (row.get("SECL_CODE") or "").strip()
        eff = (row.get("EFF_START") or "").strip()
        if not pid or not raw_name:
            continue
        if secl != ASSEMBLY_SECL or eff != EFF_START:
            continue
        titled = titlecase_name(raw_name)
        canon = assembly_by_fold.get(fold(titled))
        if not canon:
            print(f"ERROR: Assembly boundary {titled!r} not in members", file=sys.stderr)
            return 1
        pid_to_assembly[pid] = canon

    if len(pid_to_assembly) != 25:
        print(f"ERROR: expected 25 Assembly SE_PIDs, got {len(pid_to_assembly)}", file=sys.stderr)
        return 1

    by_assembly: dict[str, list[list[tuple[float, float]]]] = defaultdict(list)
    for row, rings in zip(attrs, geoms):
        pid = (row.get("SE_PID") or "").strip()
        if pid in pid_to_assembly:
            by_assembly[pid_to_assembly[pid]].extend(rings)

    if set(by_assembly) != assembly_names:
        print(
            f"ERROR: Assembly boundary names != members: "
            f"extra={sorted(set(by_assembly) - assembly_names)[:10]} "
            f"missing={sorted(assembly_names - set(by_assembly))[:10]}",
            file=sys.stderr,
        )
        return 1

    project, height, km_per_unit = make_projector(bounds_of(list(by_assembly.values())))
    fetched = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    credit = (
        "This product (The Policy Desk AU map) incorporates or was developed using "
        "Administrative Boundaries © Geoscape Australia licensed by the Commonwealth "
        "of Australia under Creative Commons Attribution 4.0 International licence "
        "(CC BY 4.0). Simplified by The Policy Desk AU. Northern Territory "
        "Legislative Assembly divisions from the NOV26 GDA2020 Geoscape release "
        "(EFF_START 2024-08-24, in force for the 2024 election)."
    )
    modified = (
        f"Simplified (Douglas-Peucker, ~{TOLERANCE * km_per_unit * 1000:.0f} m "
        f"tolerance), slivers under ~{MIN_RING_AREA * km_per_unit ** 2 * 1e6:.0f} m² "
        "dropped, projected to SVG units"
    )
    common = {
        "source": "Geoscape Australia / Commonwealth of Australia (data.gov.au)",
        "dataset": (
            "NT State Electoral Boundaries — Geoscape Administrative Boundaries "
            "(GDA2020) (Legislative Assembly divisions)"
        ),
        "dataset_url": DATASET_URL,
        "licence": "CC BY 4.0",
        "licence_url": LICENCE_URL,
        "credit": credit,
        "boundary_version": (
            "NT Electoral Commission / Geoscape NOV26 GDA2020; Assembly SECL_CODE=2 "
            "(EFF_START 2024-08-24; current divisions for the 2024 election). "
            "Earlier rows with EFF_END 2024-08-23 are not used."
        ),
        "modified": modified,
        "fetched_at": fetched,
        "viewBox": [0, 0, WIDTH, round(height)],
    }

    dist_feats = []
    for name in sorted(by_assembly):
        feat = build_feature(name, by_assembly[name], project)
        if feat is None:
            print(f"ERROR: lost geometry for Assembly {name}", file=sys.stderr)
            return 1
        dist_feats.append(feat)

    dist_doc = {**common, "features": dist_feats}
    dist_out = OUT_DIR / "nt_districts.json"
    dist_out.write_text(json.dumps(dist_doc, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(f"{dist_out.relative_to(ROOT)}: {len(dist_feats)} features, {dist_out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
