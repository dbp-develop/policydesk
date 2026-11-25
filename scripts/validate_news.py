#!/usr/bin/env python3
"""Validate data/news/ against the news rules (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEWS = ROOT / "data" / "news"
MEMBER_FILES = [
    ROOT / "data" / "members.json",
    ROOT / "data" / "federal" / "members.json",
    ROOT / "data" / "nsw" / "members.json",
    ROOT / "data" / "qld" / "members.json",
    ROOT / "data" / "wa" / "members.json",
    ROOT / "data" / "sa" / "members.json",
    ROOT / "data" / "tas" / "members.json",
    ROOT / "data" / "act" / "members.json",
    ROOT / "data" / "nt" / "members.json",
]

ITEM_KEYS = {"title", "source", "url", "published", "verified", "licence"}
SOURCES = {"The Conversation": ("https://theconversation.com/", "CC BY-ND 4.0")}
MAX_ITEMS = 5
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_ids() -> dict[str, str]:
    ids: dict[str, str] = {}
    for path in MEMBER_FILES:
        if not path.exists():
            continue
        for m in json.loads(path.read_text(encoding="utf-8"))["members"]:
            ids[m["id"]] = m["name"]
    return ids


def main() -> int:
    errors: list[str] = []
    ids = load_ids()
    if not ids:
        print("ERROR: no members found", file=sys.stderr)
        return 1
    idx_path = NEWS / "index.json"
    if not idx_path.exists():
        print("ERROR: missing data/news/index.json", file=sys.stderr)
        return 1
    idx = json.loads(idx_path.read_text(encoding="utf-8"))
    for k in ("source", "licence", "licence_url", "rules", "generated_at", "counts"):
        if not idx.get(k) and idx.get(k) != {}:
            errors.append(f"index.json: missing {k}")
    counts = idx.get("counts", {})
    if set(counts) != set(ids):
        errors.append(
            f"index.json members differ from members files: "
            f"missing {sorted(set(ids) - set(counts))[:5]}, "
            f"extra {sorted(set(counts) - set(ids))[:5]}"
        )

    files = {p.stem: p for p in NEWS.glob("*.json") if p.name != "index.json"}
    if set(files) != set(ids):
        errors.append(
            f"news files differ from members: missing {sorted(set(ids) - set(files))[:5]}, "
            f"extra {sorted(set(files) - set(ids))[:5]}"
        )

    total = verified = 0
    for mid, path in sorted(files.items()):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if set(doc) != {"member_id", "member_name", "items"}:
            errors.append(f"{mid}: unexpected keys {sorted(set(doc))}")
        if doc.get("member_id") != mid or doc.get("member_name") != ids.get(mid):
            errors.append(f"{mid}: member_id/member_name mismatch")
        items = doc.get("items", [])
        if len(items) > MAX_ITEMS:
            errors.append(f"{mid}: {len(items)} items > {MAX_ITEMS}")
        if counts.get(mid) != len(items):
            errors.append(f"{mid}: index count {counts.get(mid)} != {len(items)}")
        urls = [i.get("url") for i in items]
        if len(set(urls)) != len(urls):
            errors.append(f"{mid}: duplicate urls")
        dates = [i.get("published", "") for i in items]
        if dates != sorted(dates, reverse=True):
            errors.append(f"{mid}: items not newest-first")
        for i in items:
            if set(i) != ITEM_KEYS:
                errors.append(f"{mid}: item keys {sorted(set(i))} != {sorted(ITEM_KEYS)}")
                continue
            prefix, licence = SOURCES.get(i["source"], (None, None))
            if not prefix:
                errors.append(f"{mid}: unknown source {i['source']!r}")
            elif not i["url"].startswith(prefix) or i["licence"] != licence:
                errors.append(f"{mid}: url/licence does not match source {i['source']}")
            if not DATE.match(i["published"]):
                errors.append(f"{mid}: bad date {i['published']!r}")
            if not (5 <= len(i["title"]) <= 200) or "<" in i["title"] or "\n" in i["title"]:
                errors.append(f"{mid}: suspicious title {i['title'][:60]!r}")
            if not isinstance(i["verified"], bool):
                errors.append(f"{mid}: verified must be true/false")
            total += 1
            verified += i["verified"] is True

    print("=== validate_news ===")
    print(
        f"member files: {len(files)}/{len(ids)}; members with news: "
        f"{sum(1 for v in counts.values() if v)}; "
        f"items: {total} ({verified} verified, {total - verified} unverified)"
    )

    if errors:
        print(f"FAILED ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
