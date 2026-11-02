# Policy Desk AU

Open directory of Australian elected members: party, electorate and official
links, sourced from official and open data. Live at https://policydesk.au

Non-partisan. Every party is listed in the same way.

## Status

Early build. Starting with Victoria ahead of the 28 November 2026 state election,
then federal and the other states.

## Licence

- **Code:** AGPL-3.0 (see `LICENSE`)
- **Data and text:** CC BY-SA 4.0 (see `LICENSE-DATA.md`)
- Third-party photos and data keep their own licences.

Reuse, including commercial reuse, is welcome with credit:
"Created by The Policy Desk AU (@PolicyDeskAU)". Derived works must stay open.

## Data schema (`data/members.json`)

```json
{
  "id": "", "name": "", "chamber": "lower|upper", "parliament": "vic|federal|...",
  "state": "", "electorate": "", "party": "", "independent": false,
  "official_url": "", "x_handle": "", "photo_url": "", "photo_credit": "",
  "photo_licence": "", "source": "", "last_updated": ""
}
```

## Updating the raw data

GitHub → Actions → **Fetch Vic members** → Run workflow. This refreshes
`data/vic_raw.json` from Wikidata. Always check it against
https://www.parliament.vic.gov.au before publishing.
