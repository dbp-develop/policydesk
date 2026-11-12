# Policy Desk AU

Open directory of Australian elected members: party, electorate and official
links, sourced from official and open data. Live at https://policydesk.au

Non-partisan. Every party is listed in the same way.

## Status

Victorian directory is live: a searchable member list and an electorate map for
the current Parliament, ahead of the 28 November 2026 state election. Federal
and the other states are not in the dataset yet.

## Licence

- **Code:** AGPL-3.0 (see `LICENSE`)
- **Data and text:** CC BY-SA 4.0 (see `LICENSE-DATA.md`)
- Third-party photos and data keep their own licences.

Reuse, including commercial reuse, is welcome with credit:
"Created by The Policy Desk AU (@PolicyDeskAU)". Derived works must stay open.

## Data schema (`data/members.json`)

Top-level object (not a bare array):

```json
{
  "source": "Parliament of Victoria",
  "parliament": "vic",
  "last_updated": "YYYY-MM-DD",
  "vacancies": [
    {
      "electorate": "Brunswick",
      "chamber": "Assembly",
      "reason": "Death of sitting member; no by-election; to be decided 28 Nov 2026"
    }
  ],
  "members": [
    {
      "id": "slug",
      "name": "",
      "chamber": "lower|upper",
      "parliament": "vic",
      "state": "VIC",
      "electorate": "Assembly only (null for Council)",
      "region": "Council only (null for Assembly)",
      "party": "",
      "party_short": "ALP|LIB|NAT|GRN|IND|…",
      "independent": false,
      "official_url": "",
      "x_handle": null,
      "photo_url": null,
      "photo_credit": null,
      "photo_licence": null,
      "source": "Parliament of Victoria",
      "last_updated": "YYYY-MM-DD"
    }
  ]
}
```

Build with `python scripts/build_members.py` from `data/vic_official.json` plus
hand-edited `data/vacancies.json`, then `python scripts/validate_members.py`
(Assembly members + vacancies = 88; Council = 40).

## Map boundaries

`data/vic_boundaries.json` is a simplified extract of the 2022 Victorian
Legislative Assembly districts and Legislative Council regions from
[Vicmap Admin](https://discover.data.vic.gov.au/dataset/vicmap-admin-state-assembly-polygon-2022)
(CC BY 4.0). Refresh it manually — boundaries change at a redistribution, not
with the weekly member update:

```bash
python scripts/fetch_vic_boundaries.py
```

The script checks that every district and region name matches `members.json`
and `vacancies.json`. `validate_members.py` checks the same thing.

## Updating the raw data

GitHub → Actions → **Fetch Vic members** → Run workflow. This refreshes
`data/vic_raw.json` (Wikidata), `data/vic_official.json` (Parliament of Victoria),
then rebuilds and validates `data/members.json`. Always check official data against
https://www.parliament.vic.gov.au before publishing.
