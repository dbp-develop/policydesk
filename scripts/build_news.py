#!/usr/bin/env python3
"""Build data/news/<member-id>.json from The Conversation's Australian Atom feeds.

Stdlib only. Rules (see CLAUDE.md "News rules" and docs/data-sources.md):
- Source: The Conversation, CC BY-ND 4.0. robots.txt allows these feed paths.
- Store headline, source name, date and link ONLY. No summaries, no article text.
- Max 5 items per member, newest first. Same rules for every member and party.
- Match only when the exact full name (word boundaries, case-sensitive) is in
  the headline or standfirst, or when the name is in the body and the member's
  own electorate or region is in the text. Generic context words are not a match.
  Name in headline or standfirst -> verified (match_reason headline).
  Name in the body with the electorate or region -> unverified (match_reason electorate).
- Stored items that fail this rule are dropped, including items still inside 90 days.
- Runs add to existing items (feeds only hold ~1 week), so coverage builds up.
- Runs ONLY in the GitHub Action (.github/workflows/fetch-news.yml). The Conversation's
  robots.txt disallows AI agents such as Claude-Code, so never run it from an AI session.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

import guards

ROOT = Path(__file__).resolve().parents[1]
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
OUT = ROOT / "data" / "news"
USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
SOURCE = "The Conversation"
LICENCE = "CC BY-ND 4.0"
FEEDS = [
    "https://theconversation.com/au/articles.atom",
    "https://theconversation.com/au/politics/articles.atom",
    "https://theconversation.com/au/business/articles.atom",
    "https://theconversation.com/au/education/articles.atom",
    "https://theconversation.com/au/environment/articles.atom",
    "https://theconversation.com/au/health/articles.atom",
    "https://theconversation.com/au/technology/articles.atom",
    "https://theconversation.com/au/arts/articles.atom",
    "https://theconversation.com/au/books/articles.atom",
]
DELAY_SEC = 5
MAX_ITEMS = 5
MAX_AGE_DAYS = 90
NS = {"a": "http://www.w3.org/2005/Atom"}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return guards.read_checked(resp, url)
        except Exception as exc:  # noqa: BLE001
            print(f"fetch {url} attempt {attempt}: {exc}", file=sys.stderr)
            time.sleep(5 * attempt)
    raise RuntimeError(f"could not fetch {url}")


def plain(s: str | None) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()


def fold(s: str) -> str:
    """Matching only: curly apostrophes/quotes -> straight, so O'Brien matches O’Brien."""
    return s.replace("\u2019", "'").replace("\u2018", "'")


def parse(xml: bytes) -> list[dict]:
    root = ET.fromstring(xml)
    out = []
    for e in root.findall("a:entry", NS):
        link = e.find("a:link[@rel='alternate']", NS)
        if link is None:  # (Element truthiness is unreliable, so test for None)
            link = e.find("a:link", NS)
        out.append({
            "title": plain(e.findtext("a:title", "", NS)),
            "url": link.get("href") if link is not None else "",
            "published": (e.findtext("a:published", "", NS) or "")[:10],
            # used for matching only; never written out
            "_lead": plain(e.findtext("a:summary", "", NS)),
            "_body": plain(e.findtext("a:content", "", NS)),
        })
    return out


def name_re(name: str) -> re.Pattern:
    return re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")


def load_members() -> list[dict]:
    members: list[dict] = []
    for path in MEMBER_FILES:
        if not path.exists():
            print(f"WARNING: missing {path.relative_to(ROOT)}", file=sys.stderr)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if "federal" in str(path):
            default_parliament = "federal"
        elif "/nsw/" in str(path) or str(path).endswith("/nsw/members.json"):
            default_parliament = "nsw"
        elif "/qld/" in str(path) or str(path).endswith("/qld/members.json"):
            default_parliament = "qld"
        elif "/wa/" in str(path) or str(path).endswith("/wa/members.json"):
            default_parliament = "wa"
        elif "/sa/" in str(path) or str(path).endswith("/sa/members.json"):
            default_parliament = "sa"
        elif "/tas/" in str(path) or str(path).endswith("/tas/members.json"):
            default_parliament = "tas"
        elif "/act/" in str(path) or str(path).endswith("/act/members.json"):
            default_parliament = "act"
        elif "/nt/" in str(path) or str(path).endswith("/nt/members.json"):
            default_parliament = "nt"
        else:
            default_parliament = "vic"
        parliament = data.get("parliament") or default_parliament
        for m in data.get("members") or []:
            m = dict(m)
            m["_parliament"] = m.get("parliament") or parliament
            members.append(m)
    return members


def article_match(entry: dict, rx: re.Pattern, seat_rx: re.Pattern | None) -> dict | None:
    """Headline/standfirst name, or body name plus this member's electorate or region."""
    in_head = bool(rx.search(fold(entry["title"])) or rx.search(fold(entry["_lead"])))
    in_body = bool(rx.search(fold(entry["_body"])))
    text = " ".join((entry["title"], entry["_lead"], entry["_body"]))
    if in_head:
        reason = "headline"
        verified = True
    elif in_body and seat_rx and seat_rx.search(text):
        reason = "electorate"
        verified = False
    else:
        return None
    return {
        "title": entry["title"],
        "source": SOURCE,
        "url": entry["url"],
        "published": entry["published"],
        "verified": verified,
        "match_reason": reason,
        "licence": LICENCE,
    }


def stored_keeps(item: dict, rx: re.Pattern, seat_rx: re.Pattern | None) -> dict | None:
    """Keep a stored item only if it still passes the match rule.

    The article body is not stored. A legacy row with no match_reason is kept
    only when the member's name is in the title. An electorate match must have
    been recorded as match_reason electorate.
    """
    title = item.get("title") or ""
    name_in_title = bool(rx.search(fold(title)))
    reason = item.get("match_reason")
    if reason == "headline" or (item.get("verified") is True and name_in_title):
        kept = dict(item)
        kept["verified"] = True
        kept["match_reason"] = "headline"
        return kept
    if reason == "electorate" and seat_rx is not None:
        kept = dict(item)
        kept["verified"] = False
        kept["match_reason"] = "electorate"
        return kept
    if name_in_title:
        kept = dict(item)
        kept["verified"] = True
        kept["match_reason"] = "headline"
        return kept
    return None


def main() -> int:
    members = load_members()
    if not members:
        print("ERROR: no members loaded", file=sys.stderr)
        return 1

    entries: dict[str, dict] = {}
    failures = 0
    for i, url in enumerate(FEEDS):
        if i:
            time.sleep(DELAY_SEC)
        try:
            for e in parse(fetch(url)):
                if e["url"].startswith("https://theconversation.com/") and e["title"]:
                    entries.setdefault(e["url"], e)
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"WARNING: {url}: {exc}", file=sys.stderr)
    if failures == len(FEEDS):
        print("ERROR: every feed failed; leaving data/news unchanged", file=sys.stderr)
        return 1
    print(f"feeds: {len(FEEDS) - failures}/{len(FEEDS)} ok, {len(entries)} unique articles")

    OUT.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).date()
    cutoff = (today - timedelta(days=MAX_AGE_DAYS)).isoformat()
    index = {}
    new_total = 0
    for m in members:
        rx = name_re(fold(m["name"]))
        seat = m.get("electorate") or m.get("region") or ""
        seat_rx = re.compile(r"\b" + re.escape(seat) + r"\b") if seat else None
        found = []
        for e in entries.values():
            hit = article_match(e, rx, seat_rx)
            if hit:
                found.append(hit)

        path = OUT / f"{m['id']}.json"
        old = json.loads(path.read_text(encoding="utf-8"))["items"] if path.exists() else []
        merged: dict[str, dict] = {}
        for old_item in old:
            kept = stored_keeps(old_item, rx, seat_rx)
            if kept and kept.get("published", "") >= cutoff:
                merged[kept["url"]] = kept
        for hit in found:
            if hit["url"] not in merged:
                new_total += 1
            merged[hit["url"]] = hit
        items = sorted(
            merged.values(),
            key=lambda i: (i["published"], i["url"]),
            reverse=True,
        )[:MAX_ITEMS]
        doc = {"member_id": m["id"], "member_name": m["name"], "items": items}
        text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
        index[m["id"]] = len(items)

    idx = {
        "source": SOURCE,
        "source_url": "https://theconversation.com/au",
        "licence": LICENCE,
        "licence_url": "https://creativecommons.org/licenses/by-nd/4.0/",
        "rules": "Headline, source, date and link only. Exact full name in the "
                 "headline or standfirst, or in the body together with that "
                 "member's electorate or region. Body-only matches are unverified. "
                 "Max 5 per member.",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "counts": index,
    }
    (OUT / "index.json").write_text(json.dumps(idx, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for stale in OUT.glob("*.json"):
        if stale.name != "index.json" and stale.stem not in index:
            stale.unlink()
            print(f"removed news file for former member: {stale.stem}")
    with_news = sum(1 for v in index.values() if v)
    print(f"members with news: {with_news}/{len(members)}; new items this run: {new_total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
