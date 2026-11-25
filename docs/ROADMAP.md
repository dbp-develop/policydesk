# Roadmap

Status: ✅ done · 🔄 in progress · ⏳ not started · ⛔ blocked

| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 0 | Audit and setup | ✅ | CLAUDE.md, this roadmap, Cursor site files removed |
| 1 | Move hosting to Cloudflare Pages | ✅ | Pages project `policydesk` (policydesk-2u0.pages.dev), auto-deploys from `main`. policydesk.au live on HTTPS; www 301-redirects to apex; GitHub Pages off |
| 2 | List view | ✅ | Search, filters, alphabetical, "Data as of" line, vacancies shown, accessibility |
| 3 | Map view | ✅ | Needs boundary data with a reuse licence; else stop. Text-only fallback |
| 4 | News | ✅ | Daily GitHub Action; The Conversation only (CC BY-ND), headline + link. Google News blocked by robots.txt |
| 5 | Photos and socials | ✅ | Commons photos (66) with licence; owner-approved official handles (31) in `data/socials.json` (PR #13); review report |

## National coverage (owner decision 2026-11-23; order refreshed after Stage 5)

Do these **before** the Vic post-election refresh. Each stage must deliver, for that
parliament: **list view, map view, news, photos, official socials, and official websites**.
Check robots.txt and terms for the member list and boundary data; build + validate members;
add boundaries to the map; then news/photos/socials/websites under the same rules. Stop and
report if a source does not allow reuse.

| # | Parliament | Status | Notes |
|---|-----------|--------|-------|
| 6 | Federal (House of Representatives + Senate) | ✅ | Handbook API; AEC map; parliament picker; photos + social candidates for owner approval |
| 7 | New South Wales | ✅ | 93+42 members; Geoscape districts; LC statewide; 63 photos; 31 social candidates awaiting owner approval |
| 8 | Queensland | ✅ | Unicameral Assembly (93); Geoscape districts; national map live; social candidates awaiting owner approval |
| 9 | Western Australia | ✅ | Assembly 59 + Council 37 (statewide); Geoscape districts + LC polygon; national map live; social candidates awaiting owner approval |
| 10 | South Australia | ✅ | Assembly 47 + Council 22 (statewide); Geoscape districts + LC polygon; national map live; social candidates awaiting owner approval |
| 11 | Tasmania | ✅ | Assembly 35 (5×7 multi-member) + Council 15; Geoscape divisions; national map live; social candidates awaiting owner approval |
| 12 | Australian Capital Territory | ✅ | Unicameral Assembly 25 (5×5); Geoscape; national map live; social candidates awaiting owner approval |
| 13 | Northern Territory | 🔄 | Unicameral Assembly 25 (one division each); Geoscape; national map live; social candidates awaiting owner approval |

## Later Vic and launch

| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 14 | Post-election refresh + results mode (after 28 Nov 2026 results) | ⏳ | Paused until results. Update Vic data + vacancies.json; validators green; then election-night / results view. Do not start now |
| 15 | Compliance and launch | ⛔ | Last phase. About page, sitemap, robots.txt, privacy, final review. See blockers |

## Product value backlog (owner 26 Nov 2026)

Build order after national coverage is stable. **No party colour fills** on maps — use
symbols or short party labels and a neutral legend. Full plan (constraints, open
questions, brainstorm-later items): Project store
`docs/product-value-backlog.md`.

| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 16 | Find my seat | 🔄 | Postcode/suburb → **Federal MP + State MP** (current). Lookup: Political Gadgets CSV (CC BY 4.0; AEC + Geoscape). No seat-win history in v1 |
| 17 | Compare seats | ⏳ | Side-by-side seats/members from existing facts. Neutral |
| 18 | About + elections primer | ⏳ | Short About + plain-English how-elections-work with official links (AEC/VEC/parliament). Not Wikipedia copy. Thin About may precede full Stage 15 |
| 19 | Historic seat map (one parliament) | ⏳ | Pilot one parliament. Patterns/labels/symbols — not party colours. Owner picks parliament |

**Brainstorm later (do not schedule):** budget/inflation/GDP digest (ABS etc.); major
events timeline. **Far future / high care:** promise-kept tracker.

**Map styling note:** prefer party symbols or text abbreviations over colour coding;
party logos are often trademarked — text labels are the safer default.

## Stage 15 blockers
- Parliament of Victoria copyright page allows only "personal, non-commercial use,
  research or study, use within your organisation" and asks for permission beyond
  that (see `docs/data-sources.md` §2, verdict (c) "unclear"). This conflicts with
  allowing reuse and monetisation under CC BY-SA. Needs a decision or a permission
  request to info@parliament.vic.gov.au.
- Parliament of Australia website material is under **CC BY-NC-ND 4.0** (see
  `docs/data-sources.md` Federal section). We store facts only with attribution;
  NC-ND vs CC BY-SA / monetisation needs the same compliance decision.
- Parliament of NSW copyright allows copy/distribute with attribution, but
  charging for access or modifying needs permission (see `docs/data-sources.md`
  NSW section). Facts-only store; same Stage 15 compliance decision.
- Parliament of Queensland: materials not under Creative Commons (Copyright Act;
  fair dealing / permission path); website text separately CC BY-NC-ND 3.0 AU
  (see `docs/data-sources.md` QLD section). Facts-only store; same Stage 15 decision.
- `docs/data-sources.md` covers Vic, Federal, NSW, QLD, WA, SA, TAS, ACT, NT, boundaries,
  news, photos/socials. Keep it current when sources change.
- Parliament of South Australia: no dedicated website copyright/terms page found on
  2026-11-25 (see `docs/data-sources.md` SA section). Facts-only store; same Stage 15
  compliance decision.
- Parliament of Tasmania: no reuse licence page found beyond the footer copyright line
  (see `docs/data-sources.md` TAS section). Facts-only store; same Stage 15 decision.
- ACT Legislative Assembly website content is **CC BY-NC-ND 4.0**; portraits excluded
  (see `docs/data-sources.md` ACT section). Facts-only store; same Stage 15 NC/ND
  compliance decision.
- Legislative Assembly of the Northern Territory disclaimer: no reproduction or reuse
  apart from fair dealing under the Copyright Act, or where expressly provided
  otherwise (see `docs/data-sources.md` NT section). Facts-only store; same Stage 15
  compliance decision.
