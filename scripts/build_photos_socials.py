#!/usr/bin/env python3
"""Stage 5: find reusable photos and candidate social handles (stdlib only).

Only robots.txt-allowed pages are used (no /w/api.php, no /sparql):
  1. en.wikipedia.org/wiki/Members_of_the_Victorian_Legislative_{Assembly,Council},_2022–2026
     -> link to each member's article (matched by exact link text = member name)
  2. the member's Wikipedia article -> its Wikidata item id (Q-number)
  3. www.wikidata.org/wiki/Special:EntityData/<Q>.json
     -> CHECK: "position held" (P39) includes Member of the Victorian Legislative
        Assembly (Q18534408) or Council (Q19185341); otherwise the match is rejected
     -> image (P18), X (P2002), Facebook (P2013), Instagram (P2003)
  4. commons.wikimedia.org/wiki/File:<image> page -> licence, creator
     Accepted licences: CC0, public domain, CC BY, CC BY-SA (no NC/ND).
  5. A 240px copy is saved under images/members/ (no hotlinking).

Outputs:
  data/photos.json            accepted photos with creator, licence and Commons link
  data/socials_review.json    candidate handles from Wikidata, all "approved": false
  docs/review/stage5-review.md  human-readable report of every match and decision
Social handles are shown on the site only after the owner approves them
(they are then copied into data/socials.json).
"""

from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = "PolicyDeskAU/1.0 (https://policydesk.au)"
DELAY = 1.0
LIST_PAGES = {
    "lower": "https://en.wikipedia.org/wiki/Members_of_the_Victorian_Legislative_Assembly,_2022%E2%80%932026",
    "upper": "https://en.wikipedia.org/wiki/Members_of_the_Victorian_Legislative_Council,_2022%E2%80%932026",
}
POSITIONS = {"Q18534408": "Member of the Victorian Legislative Assembly",
             "Q19185341": "Member of the Victorian Legislative Council"}
SOCIAL_PROPS = {"P2002": ("x", "https://x.com/{}"),
                "P2013": ("facebook", "https://www.facebook.com/{}"),
                "P2003": ("instagram", "https://www.instagram.com/{}/")}
OK_LICENCE = re.compile(r"^(CC0( 1\.0)?|Public domain|PD.*|CC BY(-SA)? \d\.\d( [A-Za-z\-]+)?)$", re.I)
BAD_LICENCE = re.compile(r"\b(NC|ND)\b")
THUMB_WIDTH = 240

_last = [0.0]


def get(url: str, binary: bool = False):
    wait = DELAY - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                _last[0] = time.time()
                body = r.read()
                return (body, r.headers.get("content-type", ""), r.url) if binary else body.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            time.sleep(3 * attempt)
        except Exception:  # noqa: BLE001
            time.sleep(3 * attempt)
    raise RuntimeError(f"could not fetch {url}")


def text(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("’", "'")).strip().lower()


def article_links(page: str) -> dict[str, str]:
    """link text -> absolute article URL, for every wiki link on the page."""
    out = {}
    pat = r'<a\b[^>]*href="(?:https://en\.wikipedia\.org/wiki/|/wiki/|\./)([^"#?]+)"[^>]*>(.*?)</a>'
    for m in re.finditer(pat, page, re.S):
        title, label = m.group(1), text(m.group(2))
        if ":" in urllib.parse.unquote(title):
            continue
        out.setdefault(norm(label), "https://en.wikipedia.org/wiki/" + title)
    return out


def claim_values(entity: dict, prop: str) -> list:
    vals = []
    for c in entity.get("claims", {}).get(prop, []):
        if c.get("rank") == "deprecated":
            continue
        dv = c.get("mainsnak", {}).get("datavalue", {})
        v = dv.get("value")
        if isinstance(v, dict) and "id" in v:
            v = v["id"]
        if v:
            vals.append((v, c))
    return vals


def commons_licence(file_name: str) -> dict:
    url = "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(file_name.replace(" ", "_"))
    page = get(url)
    shorts = [text(s) for s in re.findall(r'class="[^"]*licensetpl_short[^"]*"[^>]*>(.*?)</', page, re.S)]
    links = re.findall(r'class="[^"]*licensetpl_link[^"]*"[^>]*>(.*?)</', page, re.S)
    attr = [text(s) for s in re.findall(r'class="[^"]*licensetpl_attr[^"]*"[^>]*>(.*?)</', page, re.S)]
    aut = re.search(r'id="fileinfotpl_aut"[^>]*>.*?</td>\s*<td[^>]*>(.*?)</td>', page, re.S)
    creator = (attr[0] if attr else (text(aut.group(1)) if aut else "")) or None
    return {"commons_url": url, "licences": [s for s in shorts if s],
            "licence_url": text(links[0]) if links else None,
            "creator": creator[:160] if creator else None}


def main() -> int:
    members = json.loads((ROOT / "data/members.json").read_text(encoding="utf-8"))["members"]
    lists = {k: article_links(get(u)) for k, u in LIST_PAGES.items()}
    photos, socials, report = {}, {}, []
    img_dir = ROOT / "images" / "members"
    img_dir.mkdir(parents=True, exist_ok=True)

    for m in sorted(members, key=lambda x: x["id"]):
        row = {"id": m["id"], "name": m["name"], "article": None, "qid": None,
               "check": "", "photo": "none (initials)", "socials": ""}
        report.append(row)
        art = lists[m["chamber"]].get(norm(m["name"]))
        if not art:
            row["check"] = "not found on Wikipedia list page"
            continue
        row["article"] = art
        try:
            page = get(art)
        except Exception as e:  # noqa: BLE001
            row["check"] = f"article fetch failed: {e}"
            continue
        q = re.search(r"wikidata\.org/wiki/(?:Special:EntityPage/)?(Q\d+)", page)
        if not q:
            row["check"] = "no Wikidata item linked"
            continue
        qid = row["qid"] = q.group(1)
        try:
            ent = json.loads(get(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"))["entities"]
            ent = ent.get(qid) or next(iter(ent.values()))
        except Exception as e:  # noqa: BLE001
            row["check"] = f"Wikidata fetch failed: {e}"
            continue
        held = {v for v, _ in claim_values(ent, "P39")} & set(POSITIONS)
        if not held:
            row["check"] = "REJECTED: Wikidata item has no Victorian Parliament seat"
            continue
        row["check"] = "OK: " + "; ".join(POSITIONS[h] for h in sorted(held))

        cands = {}
        for prop, (key, fmt) in SOCIAL_PROPS.items():
            vals = [str(v) for v, _ in claim_values(ent, prop)]
            if vals:
                handle = vals[0].lstrip("@")
                cands[key] = {"handle": handle, "url": fmt.format(urllib.parse.quote(handle, safe="._-"))}
        if cands:
            socials[m["id"]] = {"name": m["name"], "wikidata": f"https://www.wikidata.org/wiki/{qid}",
                                "candidates": cands, "approved": False}
            row["socials"] = ", ".join(f"{k}: {v['handle']}" for k, v in cands.items())

        imgs = [v for v, _ in claim_values(ent, "P18")]
        if not imgs:
            continue
        try:
            lic = commons_licence(imgs[0])
        except Exception as e:  # noqa: BLE001
            row["photo"] = f"licence check failed: {e}"
            continue
        good = [s for s in lic["licences"] if OK_LICENCE.match(s) and not BAD_LICENCE.search(s)]
        if not good or not lic["creator"]:
            row["photo"] = f"rejected: licence {lic['licences'] or 'not found'}, creator {lic['creator'] or 'not found'}"
            continue
        try:
            body, ctype, final = get("https://commons.wikimedia.org/wiki/Special:FilePath/"
                                     + urllib.parse.quote(imgs[0].replace(" ", "_")) + f"?width={THUMB_WIDTH}", binary=True)
        except Exception as e:  # noqa: BLE001
            row["photo"] = f"download failed: {e}"
            continue
        ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(ctype.split(";")[0])
        if not ext or len(body) > 200_000:
            row["photo"] = f"rejected: type {ctype}, {len(body)} bytes"
            continue
        local = f"images/members/{m['id']}.{ext}"
        (ROOT / local).write_bytes(body)
        photos[m["id"]] = {"file": imgs[0], "commons_url": lic["commons_url"], "creator": lic["creator"],
                           "licence": good[0], "licence_url": lic["licence_url"], "local_path": local,
                           "source": "Wikimedia Commons via Wikidata " + qid}
        row["photo"] = f"OK: {good[0]}, by {lic['creator']}"

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    (ROOT / "data/photos.json").write_text(json.dumps(
        {"source": "Wikimedia Commons (via Wikidata, matched through Wikipedia member lists)",
         "generated_at": now, "photos": photos}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "data/socials_review.json").write_text(json.dumps(
        {"source": "Wikidata (CC0): P2002 X, P2013 Facebook, P2003 Instagram",
         "note": "Candidates only. Nothing here is shown on the site until the owner approves it.",
         "generated_at": now, "candidates": socials}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = ["# Stage 5 review: photo and social matches", "",
             f"Generated {now}. Every member, how they were matched, and what was decided.", "",
             "| Member | Wikidata | Match check | Photo | Social candidates (need approval) |",
             "|---|---|---|---|---|"]
    for r in report:
        q = f"[{r['qid']}](https://www.wikidata.org/wiki/{r['qid']})" if r["qid"] else "—"
        lines.append(f"| {r['name']} | {q} | {r['check']} | {r['photo']} | {r['socials'] or '—'} |")
    out = ROOT / "docs/review/stage5-review.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok = sum(1 for r in report if r["check"].startswith("OK"))
    print(f"matched+verified: {ok}/{len(members)}; photos accepted: {len(photos)}; "
          f"members with social candidates: {len(socials)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
