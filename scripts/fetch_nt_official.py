#!/usr/bin/env python3
"""Fetch CURRENT Northern Territory Legislative Assembly members (unicameral).

Writes data/nt_official.json and prints a report. Stdlib only.

Primary list: https://parliament.nt.gov.au/members/by-name
(The /members page states there are 25 members, one division each, but the
member rows on that page are not in the HTML. Names and profile links come
from /members/by-name. Electorate and party come from each profile.)

Profile URLs: https://parliament.nt.gov.au/members/by-name/{slug}

Cloudflare often returns HTTP 403 / challenge HTML for unattended fetches.
Pass --from-dir with a browser-cleared save: by-name.html plus profiles/{slug}.html.

Facts only — no addresses, emails, phones, portraits, or biographies.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import guards

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "nt_official.json"

USER_AGENT = (
    "Mozilla/5.0 (compatible; PolicyDeskAU/1.0; +https://policydesk.au) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SOURCE = "Legislative Assembly of the Northern Territory"
SOURCE_URL = "https://parliament.nt.gov.au/members/by-name"
MEMBERS_INTRO_URL = "https://parliament.nt.gov.au/members"
PROFILE_PREFIX = "https://parliament.nt.gov.au/members/by-name/"
EXPECTED = 25
REQUEST_DELAY_SEC = 1.0

# Current single-member divisions (Geoscape EFF_START 20240824; confirmed on profiles).
DIVISIONS = {
    "Arafura",
    "Araluen",
    "Arnhem",
    "Barkly",
    "Blain",
    "Braitling",
    "Brennan",
    "Casuarina",
    "Daly",
    "Drysdale",
    "Fannie Bay",
    "Fong Lim",
    "Goyder",
    "Gwoja",
    "Johnston",
    "Karama",
    "Katherine",
    "Mulka",
    "Namatjira",
    "Nelson",
    "Nightcliff",
    "Port Darwin",
    "Sanderson",
    "Spillett",
    "Wanguri",
}

# Printed Party cell → (stored name, short code). Short codes are labels for the
# printed name; the page does not print an abbreviation.
PARTY_FULL = {
    "Country Liberal Party": ("Country Liberal Party", "CLP"),
    "Territory Labor": ("Territory Labor", "LAB"),
    "Independent": ("Independent", "IND"),
}

HONORIFIC = re.compile(
    r"^(?:The\s+Hon(?:ourable)?\.?|Hon(?:ourable)?\.?|Mr|Ms|Mrs|Miss|Dr|Prof(?:essor)?)\s+",
    re.I,
)
POSTNOM = re.compile(
    r"\s+(?:CSC|AM|AO|OAM|AC|QC|SC|KC|MP|MLA|JP)(?:\s+(?:CSC|AM|AO|OAM|AC|QC|SC|KC|MP|MLA|JP))*\s*$",
    re.I,
)
LINK_RE = re.compile(
    r'href="(https://parliament\.nt\.gov\.au/members/by-name/([^"/?#]+))"[^>]*>(.*?)</a>',
    re.I | re.S,
)


def http_get(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"},
    )
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = guards.read_checked(resp, url)
                head = body[:900].lower()
                if (
                    b"just a moment" in head
                    or b"cf-mitigated" in head
                    or b"challenge-platform" in head
                ):
                    raise RuntimeError(
                        f"Cloudflare challenge HTML for {url}. "
                        "Re-run with --from-dir after a browser-cleared save."
                    )
                return body
        except (urllib.error.URLError, TimeoutError, RuntimeError) as err:
            last_err = err
            print(f"  attempt {attempt}/3 failed: {err}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after 3 attempts: {last_err}")


def strip_tags(raw: str) -> str:
    text = html_lib.unescape(re.sub(r"<[^>]+>", " ", raw or ""))
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    return re.sub(r"\s+", " ", text).strip()


def display_name(raw: str) -> str:
    name = HONORIFIC.sub("", strip_tags(raw))
    name = POSTNOM.sub("", name)
    return re.sub(r"\s+", " ", name).strip()


def table_value(page: str, label: str) -> str:
    m = re.search(
        rf"<th[^>]*>\s*{label}\s*</th>\s*<td[^>]*>(.*?)</td>",
        page,
        re.I | re.S,
    )
    if not m:
        return ""
    return strip_tags(m.group(1))


def parse_list(html: str) -> list[dict]:
    """Unique profile links from the by-name page, in first-seen order."""
    found: list[dict] = []
    seen: set[str] = set()
    for m in LINK_RE.finditer(html):
        url, slug, label = m.group(1), m.group(2), m.group(3)
        if slug in seen:
            continue
        # Skip the list page itself if a nav link has no slug (regex requires a slug).
        name = display_name(label)
        if not name or name.lower() in {"members", "by name"}:
            continue
        seen.add(slug)
        found.append({"slug": slug, "name": name, "url": url})
    return found


def apply_profile(member: dict, page: str) -> None:
    electorate = table_value(page, "Electorate")
    party_label = table_value(page, "Party")
    if electorate not in DIVISIONS:
        raise ValueError(f"{member['slug']}: unexpected electorate {electorate!r}")
    if party_label not in PARTY_FULL:
        raise ValueError(f"{member['slug']}: unknown party {party_label!r}")
    party, party_short = PARTY_FULL[party_label]
    member["electorate"] = electorate
    member["party"] = party
    member["party_short"] = party_short
    member["party_label_raw"] = party_label


def report(members: list[dict]) -> bool:
    print("=== NT official members fetch report ===")
    print(f"Total records: {len(members)}")
    ok = len(members) == EXPECTED
    flag = "OK" if ok else f"CHECK (expected {EXPECTED})"
    print(f"  Assembly: {len(members)}  [{flag}]")

    party_counts = Counter(m.get("party") or "(missing)" for m in members)
    print("Counts per party:")
    for party, n in sorted(party_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {party}: {n}")

    seats = Counter(m.get("electorate") for m in members)
    print(f"Divisions: {len(seats)}")
    missing = sorted(DIVISIONS - set(seats))
    extra = sorted(set(seats) - DIVISIONS)
    if missing or extra or any(n != 1 for n in seats.values()):
        ok = False
        print(f"ERROR: division mismatch missing={missing} extra={extra}")
        for seat, n in sorted(seats.items()):
            if n != 1:
                print(f"ERROR: {seat} has {n} members")

    missing_url = [m for m in members if not m.get("url")]
    print(f"Members missing profile URL: {len(missing_url)}")
    incomplete = []
    for m in members:
        miss = [k for k in ("name", "chamber", "party", "electorate", "url") if not m.get(k)]
        if miss:
            incomplete.append((m, miss))
    print(f"Members missing required fields: {len(incomplete)}")
    for m, fields in incomplete[:20]:
        print(f"  {m.get('name')!r}: missing {', '.join(fields)}")
        ok = False

    if members:
        print("Sample (first 5):")
        for m in members[:5]:
            print(
                f"  {m.get('chamber')} {m.get('name')} | {m.get('party')} | "
                f"{m.get('electorate')}"
            )
            print(f"           {m.get('url')}")
    return ok and not incomplete and not missing_url


def load_pages(from_dir: str | None) -> tuple[str, dict[str, str]]:
    if from_dir:
        root = Path(from_dir)
        list_path = root / "by-name.html"
        print(f"Reading {list_path}")
        listing = list_path.read_text(encoding="utf-8", errors="replace")
        profiles: dict[str, str] = {}
        for path in sorted((root / "profiles").glob("*.html")):
            profiles[path.stem] = path.read_text(encoding="utf-8", errors="replace")
        return listing, profiles

    print(f"Fetching {SOURCE_URL}…")
    time.sleep(REQUEST_DELAY_SEC)
    listing = http_get(SOURCE_URL).decode("utf-8", "replace")
    stubs = parse_list(listing)
    profiles = {}
    for stub in stubs:
        url = stub["url"]
        print(f"Fetching {url}")
        time.sleep(REQUEST_DELAY_SEC)
        profiles[stub["slug"]] = http_get(url).decode("utf-8", "replace")
    return listing, profiles


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--from-dir",
        help="directory with by-name.html and profiles/{slug}.html from a browser-cleared save",
    )
    args = ap.parse_args()

    try:
        listing, profiles = load_pages(args.from_dir)
        stubs = parse_list(listing)
        members = []
        for stub in stubs:
            page = profiles.get(stub["slug"])
            if page is None:
                raise RuntimeError(f"missing profile HTML for {stub['slug']}")
            apply_profile(stub, page)
            members.append(
                {
                    "member_id": stub["slug"],
                    "name": stub["name"],
                    "chamber": "Assembly",
                    "party": stub["party"],
                    "party_short": stub["party_short"],
                    "party_label_raw": stub["party_label_raw"],
                    "electorate": stub["electorate"],
                    "region": None,
                    "url": stub["url"],
                }
            )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    members.sort(key=lambda m: ((m.get("name") or "").lower(), m.get("electorate") or ""))
    ok = report(members)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "member_list_url": SOURCE_URL,
        "members_intro_url": MEMBERS_INTRO_URL,
        "expected_count": EXPECTED,
        "credit": "Legislative Assembly of the Northern Territory",
        "notes": (
            "Unicameral Legislative Assembly: 25 members, one electoral division each. "
            "Names and profile links from /members/by-name (15th Assembly, elected "
            "24 August 2024). Electorate and party from each profile's Electorate and "
            "Party cells. Country Liberal Party, Territory Labor, and Independent are "
            "stored as printed. Honorifics and post-nominals (Hon, OAM) are not part "
            "of the display name. A curly apostrophe in O’Gallagher is stored as '. "
            "Addresses, emails, phones, ministries and biographies are not stored."
        ),
        "members": members,
    }
    try:
        guards.assert_profile_urls(members, guards.HOSTS["nt"])
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    OUT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {OUT.relative_to(ROOT)}")

    if not members:
        print("ERROR: fetch returned zero members.", file=sys.stderr)
        return 1
    if not ok:
        print("WARNING: counts or required fields incomplete.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
