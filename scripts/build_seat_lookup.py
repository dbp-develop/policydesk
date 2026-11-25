#!/usr/bin/env python3
"""Build static postcode/suburb → federal + state seat lookup (stdlib only).

Source: Political Gadgets electorate finder CSVs (CC BY 4.0), derived from
Australian Electoral Commission federal boundaries (2025 election) and
Geoscape Administrative Boundaries state electoral districts (CC BY 4.0).

Download:
  python3 scripts/build_seat_lookup.py
Offline:
  python3 scripts/build_seat_lookup.py --from-dir /path/to/dir
  (expects postcodes.csv and suburbs.csv in that directory)

Writes:
  data/seat_lookup/index.json
  data/seat_lookup/suburbs-{vic,nsw,...}.json
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import guards

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "seat_lookup"
USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"

POSTCODES_URL = "https://politicalgadgets.com/electorate_finder/data/postcodes.csv"
SUBURBS_URL = "https://politicalgadgets.com/electorate_finder/data/suburbs.csv"
FINDER_URL = "https://politicalgadgets.com/electorate_finder/"
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
AEC_CHECK_URL = "https://electorate.aec.gov.au/"

STATE_TO_KEY = {
    "VIC": "vic",
    "NSW": "nsw",
    "QLD": "qld",
    "WA": "wa",
    "SA": "sa",
    "TAS": "tas",
    "ACT": "act",
    "NT": "nt",
}

MEMBERS_PATHS = {
    "VIC": ROOT / "data" / "members.json",
    "NSW": ROOT / "data" / "nsw" / "members.json",
    "QLD": ROOT / "data" / "qld" / "members.json",
    "WA": ROOT / "data" / "wa" / "members.json",
    "SA": ROOT / "data" / "sa" / "members.json",
    "TAS": ROOT / "data" / "tas" / "members.json",
    "ACT": ROOT / "data" / "act" / "members.json",
    "NT": ROOT / "data" / "nt" / "members.json",
    "FEDERAL": ROOT / "data" / "federal" / "members.json",
}


def fold(name: str) -> str:
    s = (name or "").lower().strip()
    s = s.replace("’", "'").replace("`", "'")
    return re.sub(r"\s+", " ", s)


def parse_seats(cell: str) -> list[dict]:
    out: list[dict] = []
    for part in (cell or "").split(";"):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(.+?)\s*\((\d+)%\)\s*$", part)
        if m:
            out.append({"name": m.group(1).strip(), "pct": int(m.group(2))})
        else:
            out.append({"name": part, "pct": None})
    return out


def norm_postcode(raw: str) -> str:
    raw = (raw or "").strip()
    if raw.isdigit():
        return raw.zfill(4)
    return raw


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = guards.read_checked(resp, url, limit=guards.MAX_HTTP)
                return data.decode("utf-8")
        except Exception as exc:  # noqa: BLE001
            print(f"fetch {url} attempt {attempt} failed: {exc}", file=sys.stderr)
            time.sleep(3 * attempt)
    raise SystemExit(f"ERROR: could not download {url}")


def load_csv_text(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def load_valid_seats() -> tuple[dict[str, set[str]], set[str], dict[str, set[str]]]:
    """Return (state→folded lower seats, federal folded seats, state→vacancy seats)."""
    state_seats: dict[str, set[str]] = {}
    vacancies: dict[str, set[str]] = {}
    for st, path in MEMBERS_PATHS.items():
        if st == "FEDERAL":
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        seats: set[str] = set()
        for m in doc.get("members") or []:
            if m.get("chamber") == "lower" and m.get("electorate"):
                seats.add(fold(m["electorate"]))
        vacs: set[str] = set()
        for v in doc.get("vacancies") or []:
            if v.get("electorate") and (
                v.get("chamber") in (None, "Assembly", "lower", "House")
            ):
                vacs.add(fold(v["electorate"]))
                seats.add(fold(v["electorate"]))
        state_seats[st] = seats
        vacancies[st] = vacs

    fed = json.loads(MEMBERS_PATHS["FEDERAL"].read_text(encoding="utf-8"))
    fed_seats = {
        fold(m["electorate"])
        for m in fed.get("members") or []
        if m.get("chamber") == "lower" and m.get("electorate")
    }
    for v in fed.get("vacancies") or []:
        if v.get("electorate"):
            fed_seats.add(fold(v["electorate"]))
    return state_seats, fed_seats, vacancies


def build(postcode_rows: list[dict], suburb_rows: list[dict]) -> tuple[dict, dict[str, dict]]:
    state_seats, fed_seats, _vacancies = load_valid_seats()

    suburbs_by_state: dict[str, dict] = {st: {} for st in STATE_TO_KEY}
    pc_suburb_index: dict[str, list[dict]] = defaultdict(list)
    dropped_state_noise = 0

    for r in suburb_rows:
        st = (r.get("state") or "").strip().upper()
        if st not in STATE_TO_KEY:
            continue
        name = (r.get("suburb") or "").strip()
        if not name:
            continue
        key = fold(name)
        federal = [
            x for x in parse_seats(r.get("federal_electorates") or "") if fold(x["name"]) in fed_seats
        ]
        state_raw = parse_seats(r.get("state_electorates") or "")
        state = []
        for x in state_raw:
            if fold(x["name"]) in state_seats[st]:
                state.append(x)
            else:
                dropped_state_noise += 1
        pcs = [
            norm_postcode(p)
            for p in (r.get("postcodes") or "").split(";")
            if p.strip()
        ]
        if not federal and not state:
            continue
        rec = {
            "name": name,
            "state": st,
            "postcodes": pcs,
            "federal": federal,
            "state_seats": state,
            "source": FINDER_URL,
        }
        # Prefer the first row for a key; warn on clash with different seats.
        if key in suburbs_by_state[st]:
            prev = suburbs_by_state[st][key]
            if prev["federal"] != federal or prev["state_seats"] != state:
                print(
                    f"WARN: duplicate suburb {name!r} {st} with differing seats; keeping first",
                    file=sys.stderr,
                )
            continue
        suburbs_by_state[st][key] = rec
        for pc in pcs:
            pc_suburb_index[pc].append(
                {"name": name, "state": st, "key": key, "parliament": STATE_TO_KEY[st]}
            )

    postcodes: dict[str, dict] = {}
    for r in postcode_rows:
        pc = norm_postcode(r.get("postcode") or "")
        if not pc:
            continue
        states = [s.strip().upper() for s in (r.get("states") or "").split(";") if s.strip()]
        states = [s for s in states if s in STATE_TO_KEY]
        # Skip incomplete rows (no state) — cannot return a State MP.
        if not states:
            print(
                f"WARN: skipping postcode {pc}: no state in source row",
                file=sys.stderr,
            )
            continue
        federal = [
            x for x in parse_seats(r.get("federal_electorates") or "") if fold(x["name"]) in fed_seats
        ]
        state_out = []
        for x in parse_seats(r.get("state_electorates") or ""):
            matched = [s for s in states if fold(x["name"]) in state_seats[s]]
            if len(matched) == 1:
                state_out.append(
                    {
                        "name": x["name"],
                        "pct": x["pct"],
                        "state": matched[0],
                        "parliament": STATE_TO_KEY[matched[0]],
                    }
                )
            elif len(matched) > 1:
                # Same district name in more than one listed state — need suburb.
                state_out.append(
                    {
                        "name": x["name"],
                        "pct": x["pct"],
                        "state": None,
                        "parliament": None,
                    }
                )
            else:
                dropped_state_noise += 1

        unambiguous = (
            len(states) == 1
            and len(federal) == 1
            and federal[0].get("pct") == 100
            and len(state_out) == 1
            and state_out[0].get("pct") == 100
            and state_out[0].get("state") == states[0]
        )

        entry: dict = {
            "states": states,
            "parliaments": [STATE_TO_KEY[s] for s in states],
            "ambiguous": not unambiguous,
            "source": FINDER_URL,
        }
        if unambiguous:
            entry["federal"] = federal
            entry["state"] = state_out
        else:
            # De-dupe suburb picker rows (name+state).
            seen = set()
            suburbs = []
            for item in pc_suburb_index.get(pc, []):
                sig = (item["state"], item["key"])
                if sig in seen:
                    continue
                seen.add(sig)
                suburbs.append(item)
            suburbs.sort(key=lambda x: (x["name"].lower(), x["state"]))
            entry["suburbs"] = suburbs
        postcodes[pc] = entry

    meta = {
        "source": "Political Gadgets electorate finder CSV (postcodes + suburbs)",
        "source_url": FINDER_URL,
        "postcodes_csv": POSTCODES_URL,
        "suburbs_csv": SUBURBS_URL,
        "licence": "CC BY 4.0",
        "licence_url": LICENCE_URL,
        "underlying": [
            {
                "name": "Australian Electoral Commission federal electoral boundaries",
                "role": "federal division geography (as at the 2025 federal election)",
                "note": "Cited by Political Gadgets as the federal boundary source.",
            },
            {
                "name": "Geoscape Administrative Boundaries — state electoral boundaries",
                "licence": "CC BY 4.0",
                "role": "state/territory district geography",
                "note": "Cited by Political Gadgets; Commonwealth of Australia / Geoscape Australia.",
            },
        ],
        "note": (
            "Postcode and suburb correspondences are approximate. A postcode or suburb "
            "can span more than one seat. This is not an official enrolment determination. "
            "For voting and enrolment, check the Australian Electoral Commission and your "
            "state or territory electoral commission."
        ),
        "aec_check_url": AEC_CHECK_URL,
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "postcode_count": len(postcodes),
        "ambiguous_postcode_count": sum(1 for p in postcodes.values() if p.get("ambiguous")),
        "dropped_unmatched_state_seat_mentions": dropped_state_noise,
        "source_field": FINDER_URL,
    }

    index = {
        **meta,
        "postcodes": postcodes,
        "suburb_files": {
            STATE_TO_KEY[st]: f"data/seat_lookup/suburbs-{STATE_TO_KEY[st]}.json"
            for st in STATE_TO_KEY
        },
    }

    suburb_files: dict[str, dict] = {}
    for st, key in STATE_TO_KEY.items():
        suburb_files[key] = {
            "source": meta["source"],
            "source_url": FINDER_URL,
            "licence": "CC BY 4.0",
            "licence_url": LICENCE_URL,
            "state": st,
            "parliament": key,
            "last_updated": meta["last_updated"],
            "suburbs": suburbs_by_state[st],
        }

    print(
        f"postcodes={len(postcodes)} ambiguous={meta['ambiguous_postcode_count']} "
        f"suburbs={sum(len(v) for v in suburbs_by_state.values())} "
        f"dropped_state_noise={dropped_state_noise}"
    )
    return index, suburb_files


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--from-dir",
        type=Path,
        help="Read postcodes.csv and suburbs.csv from this directory instead of downloading",
    )
    args = ap.parse_args()

    if args.from_dir:
        pc_path = args.from_dir / "postcodes.csv"
        sub_path = args.from_dir / "suburbs.csv"
        if not pc_path.is_file() or not sub_path.is_file():
            raise SystemExit(f"ERROR: need {pc_path} and {sub_path}")
        postcode_rows = load_csv_text(pc_path.read_text(encoding="utf-8"))
        suburb_rows = load_csv_text(sub_path.read_text(encoding="utf-8"))
    else:
        postcode_rows = load_csv_text(fetch_text(POSTCODES_URL))
        suburb_rows = load_csv_text(fetch_text(SUBURBS_URL))

    if len(postcode_rows) < 2000 or len(suburb_rows) < 10000:
        raise SystemExit(
            f"ERROR: unexpected CSV sizes postcodes={len(postcode_rows)} suburbs={len(suburb_rows)}"
        )

    index, suburb_files = build(postcode_rows, suburb_rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Compact JSON: generated lookup is large; Cloudflare still gzip/brotli-compresses.
    (OUT_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    for key, doc in suburb_files.items():
        (OUT_DIR / f"suburbs-{key}.json").write_text(
            json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {OUT_DIR / f'suburbs-{key}.json'} ({len(doc['suburbs'])} suburbs)")
    print(f"wrote {OUT_DIR / 'index.json'}")


if __name__ == "__main__":
    main()
