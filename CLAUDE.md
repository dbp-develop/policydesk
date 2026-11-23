# CLAUDE.md — policydesk.au

Open-source directory of Australian elected members. Victoria first.
Owner is a non-developer on iPad/phone: short, plain-English replies.

## Working rules
1. One stage per session. At each gate stop, summarise in ≤8 lines (what changed,
   what was verified, what the owner must do), then wait for "go".
2. Plan first: ≤10-line plan at the start of each stage, wait for "go".
3. Never invent data. Members, parties, electorates, handles, URLs, photo licences,
   boundaries need a named source and a `source` field. Unknown = null.
   If a fetch fails or is blocked, say so. Never guess.
4. No "done" without proof: run validators/tests and show the real output.
5. Git: one branch per stage, small commits, PR to `main` (owner merges).
   The data workflow may commit data files to `main`. Never force-push.
6. Secrets: never ask for tokens in chat. Use GitHub/Cloudflare dashboard secrets
   and give the exact click path.
7. Keep this file under 150 lines. Use read-only subagents for research and review.
   Don't paste large files into the conversation.
8. End of each stage: independent reviewer subagent checks neutrality across parties,
   licence/credit compliance, no copied text or photos, data matches source,
   accessibility basics. Report its findings unedited.
9. Stay in scope. Extra ideas go under "Suggestions"; don't build them.
10. Ask the owner only when the answer changes what gets built; otherwise state the
    call in one line and continue.

## Project facts
- Map view and list view. Each member: party, portrait, official socials, recent-news popup.
- Vic state election 28 Nov 2026; data changes after it (Stage 6).
- Brand: "The Policy Desk AU" (@PolicyDeskAU). Navy #14213D, saffron #F4A300,
  off-white #FAF8F3. Font Inter. Mobile-first. No party colours. Neutral, plain English.
- Licences: code AGPL-3.0 (`LICENSE`). Data/text CC BY-SA 4.0 (`LICENSE-DATA.md`).
  Third-party photos/data keep their own licences.
  Credit line: "Created by The Policy Desk AU (@PolicyDeskAU)".
- Stack: plain HTML, CSS, vanilla JS. No framework, no build step.
  Scripts: Python standard library only.
- Hosting: GitHub = source of truth; Cloudflare Pages project `policydesk` deploys `main`
  (repo root, no build). policydesk.au + www (www 301 -> apex via Redirect Rule).
  Zoho email DNS records must never be touched. No Worker unless the owner approves.

## Data rules
- Parliament of Victoria official list = primary source for facts only
  (name, chamber, electorate/region, party, profile URL).
- Wikidata enriches X handles and photo credits, matched by name; every match reviewable
  (matching not built yet; build_members.py does not read vic_raw.json).
- No copied biographies. No hotlinked or copied parliament portraits.
- Photos: Wikimedia Commons only, if licence permits reuse, with creator, licence,
  Commons link. Otherwise initials placeholder.
- Socials: official handles only, from the parliament profile or an owner-approved source.
- Brunswick is a legitimate recorded vacancy (`data/vacancies.json`).

## News rules (Stage 4)
- Pre-built static files `data/news/<member-id>.json`; never fetched live in the browser.
- Sources: RSS (e.g. Google News by exact full name + portfolio keyword) and official
  pages (ministerial media releases, department pages). Portfolio holders also get
  department news.
- Show headline, source name, date, link only. No summaries or copied text. Max 5 items.
- Same rules for every party. Uncertain name matches dropped or labelled unverified.
- Checked 2026-11-23: Google News RSS is blocked by robots.txt; most AU publishers forbid
  commercial reuse. Owner chose The Conversation only (CC BY-ND). See docs/data-sources.md.

## Out of scope until owner says so
Federal and other states, user accounts, comments, ads, newsletter, any paid service.

## Folder map
```
.github/workflows/fetch-vic-members.yml  Manual data refresh (workflow_dispatch)
.github/workflows/check-boundaries.yml   Yearly (1 Mar) boundary check; opens an issue if outdated
.github/workflows/fetch-news.yml         Daily news build -> data/news, validated, committed to main
scripts/fetch_vic_official.py   Parliament of Victoria API -> data/vic_official.json
scripts/fetch_vic_members.py    Wikidata SPARQL -> data/vic_raw.json (enrichment)
scripts/build_members.py        vic_official + vacancies -> data/members.json
scripts/validate_members.py     Data gate: 88 Assembly seats (incl. vacancies), 40 Council
scripts/build_boundaries.py     VEC boundaries (Vicmap WFS) -> data/boundaries/*.json (SVG paths)
scripts/validate_boundaries.py  Boundary gate: 88 districts + 8 regions, names match members.json
scripts/check_boundaries.py     Is a newer redivision published? (network; used by yearly workflow)
scripts/build_news.py           The Conversation feeds -> data/news/<member-id>.json (network)
scripts/validate_news.py        News gate: max 5, allowed keys only, source/licence, ids match
data/members.json               Clean member list used by the site
data/vacancies.json             Recorded vacancies (no source field yet; fix in Stage 6)
data/vic_official.json          Raw official fetch
data/vic_raw.json               Raw Wikidata fetch
data/boundaries/                Simplified VEC boundaries, CC BY 4.0 (2020-21 redivision)
data/news/                      Headline/source/date/link per member + index.json
docs/data-sources.md            robots.txt + terms record for each source
docs/ROADMAP.md                 Stages and status
LICENSE / LICENSE-DATA.md       AGPL-3.0 / CC BY-SA 4.0
```
index.html, css/style.css, js/app.js  List + map views (map: own SVG, no tiles/libraries)
fonts/                          Self-hosted Inter + OFL licence (no Google Fonts calls)

## Commands
```bash
python3 scripts/validate_members.py     # data gate; must print OK and exit 0
python3 scripts/fetch_vic_official.py   # refresh official list (network)
python3 scripts/build_members.py        # rebuild members.json
python3 scripts/validate_boundaries.py  # boundary gate; must print OK
python3 scripts/validate_news.py        # news gate; must print OK
python3 scripts/build_boundaries.py     # re-fetch + simplify boundaries (network)
```
Local preview (from Stage 2): `python3 -m http.server 8000` in the repo root.
