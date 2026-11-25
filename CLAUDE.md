# CLAUDE.md — policydesk.au

Open-source directory of Australian elected members. Victoria first.
Owner is a non-developer on iPad/phone: short, plain-English replies.

**Lead tooling:** Cursor (this Project / Cursor cloud agents). Claude Code is no longer
in use; keep this filename for continuity. Follow the same stage/gate/"go" rules below.

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
- Map view and list view. Parliament picker (Victoria + Federal + NSW + Queensland +
  WA + SA + TAS + ACT + NT). Each member: party, portrait, official socials, recent-news
  popup, official website.
- National Australia map overview; live: Vic, NSW, QLD, WA, SA, TAS, ACT, NT (+ Federal
  via picker).
- Vic state election 28 Nov 2026; post-election data refresh is Stage 14 (paused).
- Brand: "The Policy Desk AU" (@PolicyDeskAU). Navy #14213D, saffron #F4A300,
  off-white #FAF8F3. Font Inter. Mobile-first. No party colours. Neutral, plain English.
- Licences: code AGPL-3.0 (`LICENSE`). Data/text CC BY-SA 4.0 (`LICENSE-DATA.md`).
  Third-party photos/data keep their own licences.
- Stack: plain HTML, CSS, vanilla JS. No framework, no build step. Python stdlib only.
- Hosting: GitHub = source of truth; Cloudflare Pages project `policydesk` deploys `main`.
  Zoho email DNS must never be touched. No Worker unless the owner approves.

## Data rules
- Vic: Parliament of Victoria official list = primary facts.
- Federal: Parliamentary Handbook API = primary facts; profiles on `handbook.aph.gov.au`.
- NSW: Parliament of NSW downloadable lists = primary facts; profiles
  `members-details?memberId=`. Cloudflare may block unattended fetch — see
  `docs/data-sources.md`. Use `--from-dir` when needed.
- QLD: Parliament of Queensland Member List = primary facts (unicameral Assembly);
  profiles `Member-Details?id=`. Bot protection may block PolicyDesk-only UA — see
  `docs/data-sources.md`. Use `--from-html` when needed.
- WA: Parliament of Western Australia Member Lists = primary facts (Assembly +
  Council); Council is statewide after 2025. Azure WAF may block PolicyDesk-only
  UA — see `docs/data-sources.md`. Use `--from-dir` when needed.
- SA: Parliament of South Australia contact-details API = primary facts (Assembly +
  Council statewide); profiles `Search/Member?type=member&id=`. Use `--from-json`
  when needed — see `docs/data-sources.md`.
- TAS: Parliament of Tasmania member lists = primary facts (Assembly multi-member
  divisions + Council divisions); profiles under `currentmembers/` and
  `legislative-council/members/`. Cloudflare may block unattended fetch — see
  `docs/data-sources.md`. Use `--from-dir` when needed.
- ACT: ACT Legislative Assembly current members = primary facts (unicameral,
  5 multi-member electorates × 5); profiles `/members/current/{slug}`. Cloudflare
  may block unattended fetch — see `docs/data-sources.md`. Use `--from-html` when needed.
- NT: Northern Territory Legislative Assembly by-name list = primary facts
  (unicameral, 25 single-member divisions); profiles `/members/by-name/{slug}`.
  Cloudflare may block unattended fetch — see `docs/data-sources.md`. Use
  `--from-dir` when needed.
- No copied biographies. No hotlinked or copied parliament portraits.
- Photos: Wikimedia Commons only if licence permits; else initials.
- Socials: owner-approval gate (`socials_review.json` → `socials.json`).
- Brunswick vacancy remains in `data/vacancies.json`.

## News rules
- Static `data/news/<member-id>.json`; never live in the browser. The Conversation only.
- NEVER fetch theconversation.com from a Cursor/cloud agent session. Action only.

## Out of scope until owner says so
User accounts, comments, ads, newsletter, any paid service.
Compliance/launch: Stage 15.

## Folder map
```
.github/workflows/fetch-vic-members.yml / fetch-federal-members.yml /
  fetch-nsw-members.yml / fetch-qld-members.yml / fetch-wa-members.yml /
  fetch-sa-members.yml / fetch-tas-members.yml / fetch-act-members.yml /
  fetch-nt-members.yml / fetch-news.yml
scripts/fetch_*_official.py, build_*_members.py, build_*_boundaries.py, validate_*.py
scripts/build_news.py (Action ONLY), build_photos_socials.py (--parliament)
data/members.json (Vic), data/federal/, data/nsw/, data/qld/, data/wa/, data/sa/,
  data/tas/, data/act/, data/nt/, data/*_official.json
data/boundaries/vic_*.json, federal_*.json, nsw_*.json, qld_districts.json,
  wa_*.json, sa_*.json, tas_*.json, act_districts.json, nt_districts.json
data/news/, data/photos.json, data/socials_review.json, data/socials.json
docs/data-sources.md, docs/ROADMAP.md, docs/review/stage{5,6,7,8,9,10,11,12,13}-*.md
```
index.html, css/style.css, js/app.js — list + map + parliament picker

## Commands
```bash
python3 scripts/validate_members.py
python3 scripts/validate_boundaries.py
python3 scripts/validate_news.py
python3 scripts/validate_photos_socials.py
python3 scripts/fetch_nt_official.py && python3 scripts/build_nt_members.py
python3 scripts/build_nt_boundaries.py
```
Local preview: `python3 -m http.server 8000` in the repo root.
