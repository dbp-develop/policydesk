# The Policy Desk AU — policydesk.au

A neutral, open-source directory of Australian elected members. Victoria first.

Created by The Policy Desk AU (@PolicyDeskAU).

## What's here
- `index.html`, `css/`, `js/`: the website (plain HTML, CSS and JavaScript; no build step).
- `data/members.json`: current members of the Parliament of Victoria (source: Parliament of Victoria).
- `scripts/`: Python (standard library only) scripts that fetch, build and validate the data.
- `docs/`: data-source records and the roadmap.

## Run locally
```bash
python3 -m http.server 8000
```
Then open http://localhost:8000.

## Check the data
```bash
python3 scripts/validate_members.py
```

## Hosting
Cloudflare Pages serves the repository root as-is (no build command). Custom domain: policydesk.au.

## Licences
- Code: AGPL-3.0 (`LICENSE`).
- Our data and text: CC BY-SA 4.0 (`LICENSE-DATA.md`).
- Third-party data and photos keep their own licences.
- Inter font: SIL Open Font License 1.1 (`fonts/OFL.txt`).

Member facts come from the Parliament of Victoria. This project is independent and not affiliated with the Parliament or any party.
