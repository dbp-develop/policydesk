#!/usr/bin/env python3
"""Find reusable photos and candidate social handles (stdlib only).

Only robots.txt-allowed pages are used (no /w/api.php, no /sparql):
  1. Wikipedia chamber member-list pages -> exact link text = member name
  2. member Wikipedia article -> Wikidata Q-id
  3. Special:EntityData/<Q>.json -> P39 check, P18 image, social props
  4. Commons file page -> licence + creator; 240px local copy

Outputs:
  data/photos.json
  data/socials_review.json  (approved: false until owner approves)
  docs/review/stage5-review.md, stage6-federal-review.md, and/or stage7-nsw-review.md

Usage:
  python3 scripts/build_photos_socials.py              # all parliaments
  python3 scripts/build_photos_socials.py --parliament vic
  python3 scripts/build_photos_socials.py --parliament federal
  python3 scripts/build_photos_socials.py --parliament nsw
  python3 scripts/build_photos_socials.py --parliament qld
  python3 scripts/build_photos_socials.py --parliament wa
  python3 scripts/build_photos_socials.py --parliament sa
  python3 scripts/build_photos_socials.py --parliament tas
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = "PolicyDeskAU/1.0 (https://policydesk.au)"
DELAY = 1.0

PARLIAMENTS = {
    "vic": {
        "members": ROOT / "data" / "members.json",
        "list_pages": {
            "lower": "https://en.wikipedia.org/wiki/Members_of_the_Victorian_Legislative_Assembly,_2022%E2%80%932026",
            "upper": "https://en.wikipedia.org/wiki/Members_of_the_Victorian_Legislative_Council,_2022%E2%80%932026",
        },
        "positions": {
            "Q18534408": "Member of the Victorian Legislative Assembly",
            "Q19185341": "Member of the Victorian Legislative Council",
        },
        "review": ROOT / "docs" / "review" / "stage5-review.md",
        "review_title": "Stage 5 review: photo and social matches (Victoria)",
        "check_label": "Victorian seat",
    },
    "federal": {
        "members": ROOT / "data" / "federal" / "members.json",
        "list_pages": {
            "lower": "https://en.wikipedia.org/wiki/Members_of_the_Australian_House_of_Representatives,_2025%E2%80%932028",
            "upper": "https://en.wikipedia.org/wiki/Members_of_the_Australian_Senate,_2025%E2%80%932028",
        },
        "positions": {
            "Q18944227": "Member of the Australian House of Representatives",
            "Q6814428": "Member of the Australian Senate",
            # Common alternate / related position items seen on sitting members:
            "Q18912794": "Member of the House of Representatives (Australia)",
        },
        "review": ROOT / "docs" / "review" / "stage6-federal-review.md",
        "review_title": "Stage 6 review: photo and social matches (Federal)",
        "check_label": "federal seat",
    },
    "nsw": {
        "members": ROOT / "data" / "nsw" / "members.json",
        "list_pages": {
            "lower": "https://en.wikipedia.org/wiki/Members_of_the_New_South_Wales_Legislative_Assembly,_2023%E2%80%932027",
            "upper": "https://en.wikipedia.org/wiki/Members_of_the_New_South_Wales_Legislative_Council,_2023%E2%80%932027",
        },
        "positions": {
            "Q19202748": "Member of the New South Wales Legislative Assembly",
            "Q18810377": "Member of the New South Wales Legislative Council",
        },
        "review": ROOT / "docs" / "review" / "stage7-nsw-review.md",
        "review_title": "Stage 7 review: photo and social matches (New South Wales)",
        "check_label": "NSW seat",
    },
    "qld": {
        "members": ROOT / "data" / "qld" / "members.json",
        "list_pages": {
            "lower": "https://en.wikipedia.org/wiki/Members_of_the_Queensland_Legislative_Assembly,_2024%E2%80%932028",
        },
        "positions": {
            "Q18526194": "Member of the Queensland Legislative Assembly",
        },
        "review": ROOT / "docs" / "review" / "stage8-qld-review.md",
        "review_title": "Stage 8 review: photo and social matches (Queensland)",
        "check_label": "QLD seat",
    },
    "wa": {
        "members": ROOT / "data" / "wa" / "members.json",
        "list_pages": {
            "lower": "https://en.wikipedia.org/wiki/Members_of_the_Western_Australian_Legislative_Assembly,_2025%E2%80%932029",
            "upper": "https://en.wikipedia.org/wiki/Members_of_the_Western_Australian_Legislative_Council,_2025%E2%80%932029",
        },
        "positions": {
            "Q20165902": "Member of the Western Australian Legislative Assembly",
            "Q19627913": "Member of the Western Australian Legislative Council",
        },
        "review": ROOT / "docs" / "review" / "stage9-wa-review.md",
        "review_title": "Stage 9 review: photo and social matches (Western Australia)",
        "check_label": "WA seat",
    },
    "sa": {
        "members": ROOT / "data" / "sa" / "members.json",
        "list_pages": {
            "lower": "https://en.wikipedia.org/wiki/Members_of_the_South_Australian_House_of_Assembly,_2026%E2%80%932030",
            "upper": "https://en.wikipedia.org/wiki/Members_of_the_South_Australian_Legislative_Council,_2026%E2%80%932030",
        },
        "positions": {
            "Q18220900": "Member of the South Australian House of Assembly",
            "Q18662245": "Member of the South Australian Legislative Council",
        },
        "review": ROOT / "docs" / "review" / "stage10-sa-review.md",
        "review_title": "Stage 10 review: photo and social matches (South Australia)",
        "check_label": "SA seat",
    },
    "tas": {
        "members": ROOT / "data" / "tas" / "members.json",
        "list_pages": {
            "lower": "https://en.wikipedia.org/wiki/Members_of_the_Tasmanian_House_of_Assembly,_2025%E2%80%932029",
            "upper": "https://en.wikipedia.org/wiki/Members_of_the_Tasmanian_Legislative_Council,_2023%E2%80%932029",
        },
        "positions": {
            "Q19007285": "Member of the Tasmanian House of Assembly",
            "Q19299542": "Member of the Tasmanian Legislative Council",
        },
        "review": ROOT / "docs" / "review" / "stage11-tas-review.md",
        "review_title": "Stage 11 review: photo and social matches (Tasmania)",
        "check_label": "TAS seat",
    },
}

SOCIAL_PROPS = {
    "P2002": ("x", "https://x.com/{}"),
    "P2013": ("facebook", "https://www.facebook.com/{}"),
    "P2003": ("instagram", "https://www.instagram.com/{}/"),
}
OK_LICENCE = re.compile(
    r"^(CC0( 1\.0)?|Public domain|CC BY(-SA)? \d\.\d( [A-Za-z\-]+)?)$", re.I
)
BAD_CREATOR = re.compile(r"^(unknown|anonymous|unknown author|author unknown)\b", re.I)
PARLIAMENT_SOURCE = re.compile(
    r"parliament|parl\.|aph\.gov\.au|nsw\.gov\.au|qld\.gov\.au|wa\.gov\.au|sa\.gov\.au|tas\.gov\.au",
    re.I,
)
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
                return (
                    (body, r.headers.get("content-type", ""), r.url)
                    if binary
                    else body.decode("utf-8", "replace")
                )
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
    out = {}
    pat = (
        r'<a\b[^>]*href="(?:https://en\.wikipedia\.org/wiki/|/wiki/|\./)([^"#?]+)"[^>]*>'
        r"(.*?)</a>"
    )
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
    url = "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(
        file_name.replace(" ", "_")
    )
    page = get(url).replace("&#95;", "_")
    shorts = [
        text(s)
        for s in re.findall(
            r'class="(?:[^"]*\s)?licensetpl_short(?:\s[^"]*)?"[^>]*>(.*?)</', page, re.S
        )
    ]
    links = re.findall(
        r'class="(?:[^"]*\s)?licensetpl_link(?:\s[^"]*)?"[^>]*>(.*?)</', page, re.S
    )
    attr = [
        text(s)
        for s in re.findall(
            r'class="(?:[^"]*\s)?licensetpl_attr(?:\s[^"]*)?"[^>]*>(.*?)</', page, re.S
        )
    ]
    aut = re.search(
        r'id="fileinfotpl_aut"[^>]*>.*?</td>\s*<td[^>]*>(.*?)</td>', page, re.S
    )
    src = re.search(
        r'id="fileinfotpl_src"[^>]*>.*?</td>\s*<td[^>]*>(.*?)</td>', page, re.S
    )
    creator = (attr[0] if attr else (text(aut.group(1)) if aut else "")) or None
    return {
        "commons_url": url,
        "licences": shorts,
        "licence_urls": [text(x) for x in links],
        "creator": creator[:160] if creator else None,
        "source_text": (
            (text(src.group(1)) + " " + " ".join(re.findall(r'href="([^"]+)"', src.group(1))))
            if src
            else ""
        ),
    }


def process_parliament(key: str, photos: dict, socials: dict) -> tuple[list[dict], int]:
    cfg = PARLIAMENTS[key]
    members = json.loads(cfg["members"].read_text(encoding="utf-8"))["members"]
    lists = {k: article_links(get(u)) for k, u in cfg["list_pages"].items()}
    positions = cfg["positions"]
    report = []
    img_dir = ROOT / "images" / "members"
    img_dir.mkdir(parents=True, exist_ok=True)

    for m in sorted(members, key=lambda x: x["id"]):
        row = {
            "id": m["id"],
            "name": m["name"],
            "article": None,
            "qid": None,
            "check": "",
            "photo": "none (initials)",
            "socials": "",
        }
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
            ent = json.loads(
                get(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json")
            )["entities"]
            ent = ent.get(qid) or next(iter(ent.values()))
        except Exception as e:  # noqa: BLE001
            row["check"] = f"Wikidata fetch failed: {e}"
            continue
        held = {v for v, _ in claim_values(ent, "P39")} & set(positions)
        if held:
            row["check"] = "OK: " + "; ".join(positions[h] for h in sorted(held))
        else:
            row["check"] = (
                f"CHECK: matched by Wikipedia member list only "
                f"(no {cfg['check_label']} on Wikidata)"
            )

        cands = {}
        for prop, (skey, fmt) in SOCIAL_PROPS.items():
            pairs = claim_values(ent, prop)
            pairs.sort(key=lambda vc: 0 if vc[1].get("rank") == "preferred" else 1)
            vals = [str(v) for v, _ in pairs]
            if vals:
                handle = vals[0].lstrip("@")
                cands[skey] = {
                    "handle": handle,
                    "url": fmt.format(urllib.parse.quote(handle, safe="._-")),
                }
        if cands:
            socials[m["id"]] = {
                "name": m["name"],
                "wikidata": f"https://www.wikidata.org/wiki/{qid}",
                "candidates": cands,
                "approved": False,
            }
            row["socials"] = ", ".join(f"{k}: {v['handle']}" for k, v in cands.items())

        imgs = [v for v, _ in claim_values(ent, "P18")]
        if not imgs:
            continue
        try:
            lic = commons_licence(imgs[0])
        except Exception as e:  # noqa: BLE001
            row["photo"] = f"licence check failed: {e}"
            continue
        good_i = [
            i
            for i, s in enumerate(lic["licences"])
            if OK_LICENCE.match(s) and not BAD_LICENCE.search(s)
        ]
        if not good_i or not lic["creator"] or BAD_CREATOR.match(lic["creator"]):
            row["photo"] = (
                f"rejected: licence {lic['licences'] or 'not found'}, "
                f"creator {lic['creator'] or 'not found'}"
            )
            continue
        if PARLIAMENT_SOURCE.search(lic["source_text"]):
            row["photo"] = (
                f"rejected: source looks like a parliament site "
                f"({lic['source_text'][:80]})"
            )
            continue
        gi = good_i[0]
        lic_name = lic["licences"][gi]
        lic_url = lic["licence_urls"][gi] if gi < len(lic["licence_urls"]) else None
        if not lic_url and lic_name.lower().startswith(("cc0", "public domain")):
            lic_url = (
                "https://creativecommons.org/publicdomain/zero/1.0/"
                if lic_name.lower().startswith("cc0")
                else None
            )
        body = ctype = None
        for width in (THUMB_WIDTH, 160):
            try:
                body, ctype, _final = get(
                    "https://commons.wikimedia.org/wiki/Special:FilePath/"
                    + urllib.parse.quote(imgs[0].replace(" ", "_"))
                    + f"?width={width}",
                    binary=True,
                )
            except Exception as e:  # noqa: BLE001
                body = None
                row["photo"] = f"download failed: {e}"
                break
            if len(body) <= 200_000:
                break
        if body is None:
            continue
        ext = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
        }.get(ctype.split(";")[0])
        if not ext or len(body) > 200_000:
            row["photo"] = f"rejected: type {ctype}, {len(body)} bytes"
            continue
        local = f"images/members/{m['id']}.{ext}"
        (ROOT / local).write_bytes(body)
        photos[m["id"]] = {
            "file": imgs[0],
            "commons_url": lic["commons_url"],
            "creator": lic["creator"],
            "licence": lic_name,
            "licence_url": lic_url,
            "local_path": local,
            "source": "Wikimedia Commons via Wikidata " + qid,
        }
        row["photo"] = f"OK: {lic_name}, by {lic['creator']}"

    lines = [
        f"# {cfg['review_title']}",
        "",
        f"Generated {datetime.now(timezone.utc).replace(microsecond=0).isoformat()}. "
        "Every member, how they were matched, and what was decided.",
        "",
        "| Member | Wikidata | Match check | Photo | Social candidates (need approval) |",
        "|---|---|---|---|---|",
    ]
    for r in report:
        q = f"[{r['qid']}](https://www.wikidata.org/wiki/{r['qid']})" if r["qid"] else "—"
        lines.append(
            f"| {r['name']} | {q} | {r['check']} | {r['photo']} | {r['socials'] or '—'} |"
        )
    cfg["review"].parent.mkdir(parents=True, exist_ok=True)
    cfg["review"].write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok = sum(1 for r in report if r["check"].startswith("OK"))
    return report, ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--parliament",
        choices=["vic", "federal", "nsw", "qld", "wa", "sa", "tas", "all"],
        default="all",
        help="which parliament(s) to refresh (default: all)",
    )
    args = ap.parse_args()
    targets = (
        ["vic", "federal", "nsw", "qld", "wa", "sa", "tas"]
        if args.parliament == "all"
        else [args.parliament]
    )

    photos_path = ROOT / "data" / "photos.json"
    socials_path = ROOT / "data" / "socials_review.json"
    photos = (
        json.loads(photos_path.read_text(encoding="utf-8")).get("photos", {})
        if photos_path.exists()
        else {}
    )
    socials = (
        json.loads(socials_path.read_text(encoding="utf-8")).get("candidates", {})
        if socials_path.exists()
        else {}
    )

    # Drop entries for members we are about to rebuild, so removals stick.
    for key in targets:
        ids = {
            m["id"]
            for m in json.loads(PARLIAMENTS[key]["members"].read_text(encoding="utf-8"))[
                "members"
            ]
        }
        for mid in list(photos):
            if mid in ids:
                # remove old local file if we replace or drop the photo
                old = photos.pop(mid)
                p = ROOT / old.get("local_path", "")
                if p.exists() and p.is_file():
                    p.unlink()
        for mid in list(socials):
            if mid in ids:
                socials.pop(mid)

    totals = []
    for key in targets:
        print(f"=== {key} ===")
        report, ok = process_parliament(key, photos, socials)
        members_n = len(report)
        photos_n = sum(
            1
            for m in report
            if m["id"] in photos
        )
        socials_n = sum(1 for m in report if m["id"] in socials)
        print(
            f"{key}: matched+verified {ok}/{members_n}; "
            f"photos accepted this parliament: {photos_n}; "
            f"social candidates: {socials_n}"
        )
        totals.append((key, ok, members_n, photos_n, socials_n))

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    photos_path.write_text(
        json.dumps(
            {
                "source": "Wikimedia Commons (via Wikidata, matched through Wikipedia member lists)",
                "generated_at": now,
                "photos": photos,
            },
            indent=1,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    socials_path.write_text(
        json.dumps(
            {
                "source": "Wikidata (CC0): P2002 X, P2013 Facebook, P2003 Instagram",
                "note": "Candidates only. Nothing here is shown on the site until the owner approves it.",
                "generated_at": now,
                "candidates": socials,
            },
            indent=1,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    # Orphan image cleanup against the merged photos map.
    used = {p["local_path"] for p in photos.values()}
    for f in (ROOT / "images" / "members").glob("*"):
        rel = f"images/members/{f.name}"
        if rel not in used:
            f.unlink()
            print(f"removed orphan image {rel}")

    print("=== totals ===")
    for row in totals:
        print(row)
    print(f"photos.json entries: {len(photos)}; socials_review candidates: {len(socials)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
