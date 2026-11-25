#!/usr/bin/env python3
"""Validate data/photos.json, data/socials_review.json and data/socials.json (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OK_LICENCE = re.compile(r"^(CC0( 1\.0)?|Public domain|CC BY(-SA)? \d\.\d( [A-Za-z\-]+)?)$", re.I)
PHOTO_KEYS = {"file", "commons_url", "creator", "licence", "licence_url", "local_path", "source"}
SOCIAL_HOSTS = {"x": "https://x.com/", "facebook": "https://www.facebook.com/", "instagram": "https://www.instagram.com/"}
MAX_BYTES = 200_000


def load_ids() -> set[str]:
    ids: set[str] = set()
    for path in (
        ROOT / "data/members.json",
        ROOT / "data/federal/members.json",
        ROOT / "data/nsw/members.json",
        ROOT / "data/qld/members.json",
        ROOT / "data/wa/members.json",
        ROOT / "data/sa/members.json",
        ROOT / "data/tas/members.json",
    ):
        if path.exists():
            ids |= {m["id"] for m in json.loads(path.read_text(encoding="utf-8"))["members"]}
    return ids


def main() -> int:
    errors: list[str] = []
    ids = load_ids()

    photos = json.loads((ROOT / "data/photos.json").read_text(encoding="utf-8"))
    if not photos.get("source"):
        errors.append("photos.json: missing source")
    for mid, p in photos.get("photos", {}).items():
        if mid not in ids:
            errors.append(f"photo for unknown member {mid}")
        if set(p) != PHOTO_KEYS:
            errors.append(f"{mid}: photo keys {sorted(p)}")
            continue
        if not OK_LICENCE.match(p["licence"]) or re.search(r"\b(NC|ND)\b", p["licence"]):
            errors.append(f"{mid}: licence not allowed: {p['licence']}")
        if not p["creator"] or re.match(r"^(unknown|anonymous)", p["creator"], re.I):
            errors.append(f"{mid}: missing or unknown creator")
        if p["licence"].startswith("CC BY") and not (p["licence_url"] or "").startswith(("http://", "https://")):
            errors.append(f"{mid}: CC BY licence needs a licence link")
        if not p["commons_url"].startswith("https://commons.wikimedia.org/wiki/File:"):
            errors.append(f"{mid}: bad Commons link")
        f = ROOT / p["local_path"]
        if not (p["local_path"].startswith("images/members/") and f.exists()):
            errors.append(f"{mid}: local image missing {p['local_path']}")
        elif f.read_bytes()[:4] not in (b"\xff\xd8\xff\xe0", b"\xff\xd8\xff\xe1", b"\xff\xd8\xff\xdb", b"\x89PNG", b"RIFF") \
                and f.read_bytes()[:3] != b"\xff\xd8\xff":
            errors.append(f"{mid}: file is not a JPEG/PNG/WebP image")
        elif f.stat().st_size > MAX_BYTES:
            errors.append(f"{mid}: image too large ({f.stat().st_size} bytes)")
    used = {p["local_path"] for p in photos.get("photos", {}).values()}
    for f in (ROOT / "images/members").glob("*"):
        if f"images/members/{f.name}" not in used:
            errors.append(f"orphan image with no licence record: {f.name}")

    review = json.loads((ROOT / "data/socials_review.json").read_text(encoding="utf-8"))
    for mid, c in review.get("candidates", {}).items():
        if mid not in ids:
            errors.append(f"social candidate for unknown member {mid}")
        if not c.get("wikidata", "").startswith("https://www.wikidata.org/wiki/Q"):
            errors.append(f"{mid}: candidate missing Wikidata source link")

    approved_path = ROOT / "data/socials.json"
    approved = json.loads(approved_path.read_text(encoding="utf-8")) if approved_path.exists() else {"socials": {}}
    if approved.get("socials") and not approved.get("approved_by"):
        errors.append("socials.json: approved handles need an approved_by note")
    for mid, s in approved.get("socials", {}).items():
        if mid not in ids:
            errors.append(f"approved social for unknown member {mid}")
        if not s.get("source"):
            errors.append(f"{mid}: approved social missing source")
        for k, v in s.get("links", {}).items():
            if k not in SOCIAL_HOSTS or not v.startswith(SOCIAL_HOSTS[k]):
                errors.append(f"{mid}: bad {k} link {v!r}")

    print("=== validate_photos_socials ===")
    print(f"photos: {len(photos.get('photos', {}))} (all with licence, creator, Commons link, local copy); "
          f"social candidates: {len(review.get('candidates', {}))}; approved socials: {len(approved.get('socials', {}))}")
    if errors:
        print(f"FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors[:40]:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
