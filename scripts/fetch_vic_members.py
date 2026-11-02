#!/usr/bin/env python3
"""Fetch current Victorian MPs (Legislative Assembly + Council) from Wikidata.

Standard library only. Writes data/vic_raw.json and prints a report.

Approach:
  1. Look up the Wikidata item IDs of the two parliamentary positions by exact
     English label (so we never hard-code IDs from memory).
  2. Run one SPARQL query for everyone holding those positions with NO end
     date on the position statement.
  3. Collapse rows to one record per person and print an accuracy report.

Wikidata can be incomplete or stale. Treat the output as a RAW starting point
and verify it against https://www.parliament.vic.gov.au before publishing.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "vic_raw.json"

USER_AGENT = "PolicyDeskAU/1.0 (https://policydesk.au)"
API_URL = "https://www.wikidata.org/w/api.php"
SPARQL_URL = "https://query.wikidata.org/sparql"

# Exact English labels of the position items we want.
POSITIONS = {
    "member of the victorian legislative assembly": "Assembly",
    "member of the victorian legislative council": "Council",
}
EXPECTED = {"Assembly": 88, "Council": 40}


def http_get_json(url: str, params: dict, accept: str = "application/json") -> dict:
    """GET with a polite User-Agent and a few retries."""
    full = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        full, headers={"User-Agent": USER_AGENT, "Accept": accept}
    )
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
            last_err = err
            print(f"  attempt {attempt}/3 failed: {err}", file=sys.stderr)
            time.sleep(3 * attempt)
    raise RuntimeError(f"Request failed after 3 attempts: {last_err}")


def find_position_ids() -> dict[str, str]:
    """Return {wikidata_qid: chamber} for the two positions, by exact label."""
    found: dict[str, str] = {}
    for label, chamber in POSITIONS.items():
        data = http_get_json(
            API_URL,
            {
                "action": "wbsearchentities",
                "search": label,
                "language": "en",
                "type": "item",
                "limit": 20,
                "format": "json",
            },
        )
        for hit in data.get("search", []):
            if hit.get("label", "").strip().lower() == label:
                found[hit["id"]] = chamber
    return found


def build_query(position_ids: list[str]) -> str:
    values = " ".join(f"wd:{q}" for q in position_ids)
    return f"""
SELECT ?person ?personLabel ?pos ?district ?districtLabel
       ?party ?partyLabel ?website ?xhandle ?image WHERE {{
  VALUES ?pos {{ {values} }}
  ?person p:P39 ?st .
  ?st ps:P39 ?pos .
  FILTER NOT EXISTS {{ ?st pq:P582 ?end }}
  OPTIONAL {{ ?st pq:P768 ?district }}
  OPTIONAL {{
    ?person p:P102 ?pst .
    ?pst ps:P102 ?party .
    FILTER NOT EXISTS {{ ?pst pq:P582 ?pend }}
  }}
  OPTIONAL {{ ?person wdt:P856 ?website }}
  OPTIONAL {{ ?person wdt:P2002 ?xhandle }}
  OPTIONAL {{ ?person wdt:P18 ?image }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""


def qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def commons_filename(uri: str) -> str:
    return urllib.parse.unquote(uri.rsplit("/", 1)[-1])


def collapse(rows: list[dict], pos_to_chamber: dict[str, str]) -> list[dict]:
    """Merge SPARQL rows into one record per (person, chamber)."""
    people: dict[tuple[str, str], dict] = {}
    for row in rows:
        pid = qid(row["person"]["value"])
        chamber = pos_to_chamber[qid(row["pos"]["value"])]
        rec = people.setdefault(
            (pid, chamber),
            {
                "wikidata_id": pid,
                "name": row.get("personLabel", {}).get("value", ""),
                "chamber": chamber,
                "district": None,
                "party": None,
                "official_url": None,
                "x_handle": None,
                "image_file": None,
                "wikidata_url": f"https://www.wikidata.org/wiki/{pid}",
            },
        )
        # Keep the first non-empty value for each field.
        if not rec["district"] and "districtLabel" in row:
            rec["district"] = row["districtLabel"]["value"]
        if not rec["party"] and "partyLabel" in row:
            rec["party"] = row["partyLabel"]["value"]
        if not rec["official_url"] and "website" in row:
            rec["official_url"] = row["website"]["value"]
        if not rec["x_handle"] and "xhandle" in row:
            rec["x_handle"] = row["xhandle"]["value"].lstrip("@")
        if not rec["image_file"] and "image" in row:
            rec["image_file"] = commons_filename(row["image"]["value"])
    return sorted(people.values(), key=lambda r: (r["chamber"], r["name"]))


def report(members: list[dict]) -> None:
    print("=== Vic members fetch report ===")
    print(f"Total records: {len(members)}")
    for chamber, expected in EXPECTED.items():
        count = sum(1 for m in members if m["chamber"] == chamber)
        flag = "OK" if count == expected else f"CHECK (expected {expected})"
        print(f"  {chamber}: {count}  [{flag}]")
    print("Missing fields:")
    for field in ("district", "party", "official_url", "x_handle", "image_file"):
        missing = sum(1 for m in members if not m[field])
        print(f"  no {field}: {missing}")
    print("Sample (first 5):")
    for m in members[:5]:
        print(f"  {m['chamber']:8} {m['name']} | {m['party']} | {m['district']}")


def main() -> int:
    print("Looking up position IDs on Wikidata...")
    pos_to_chamber = find_position_ids()
    print(f"Position IDs found: {pos_to_chamber}")
    if len(pos_to_chamber) == 0:
        print("ERROR: could not find the parliamentary position items.", file=sys.stderr)
        return 1

    print("Running SPARQL query...")
    data = http_get_json(
        SPARQL_URL,
        {"query": build_query(list(pos_to_chamber)), "format": "json"},
        accept="application/sparql-results+json",
    )
    rows = data.get("results", {}).get("bindings", [])
    print(f"Raw rows returned: {len(rows)}")

    members = collapse(rows, pos_to_chamber)
    report(members)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "Wikidata (CC0)",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "position_ids": pos_to_chamber,
        "expected_counts": EXPECTED,
        "members": members,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")

    return 0 if members else 1


if __name__ == "__main__":
    sys.exit(main())
