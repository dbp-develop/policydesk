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
| 7 | New South Wales | 🔄 | Assembly + Council; Geoscape districts; LC statewide; photos/socials in progress |
| 8 | Queensland | ⏳ | Unicameral |
| 9 | Western Australia | ⏳ | |
| 10 | South Australia | ⏳ | |
| 11 | Tasmania | ⏳ | Multi-member divisions |
| 12 | Australian Capital Territory | ⏳ | Unicameral, multi-member |
| 13 | Northern Territory | ⏳ | Unicameral |

## Later Vic and launch

| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 14 | Post-election refresh (after 28 Nov 2026 results) | ⏳ | Paused until results. Update Vic data + vacancies.json; validators green. Do not start now |
| 15 | Compliance and launch | ⛔ | Last phase. About page, sitemap, robots.txt, privacy, final review. See blockers |

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
- `docs/data-sources.md` covers Vic, Federal, NSW, boundaries, news, photos/socials.
  Keep it current when sources change.
