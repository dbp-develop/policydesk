# Roadmap

Status: ✅ done · 🔄 in progress · ⏳ not started · ⛔ blocked

| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 0 | Audit and setup | ✅ | CLAUDE.md, this roadmap, Cursor site files removed |
| 1 | Move hosting to Cloudflare Pages | ✅ | Pages project `policydesk` (policydesk-2u0.pages.dev), auto-deploys from `main`. policydesk.au live on HTTPS; www 301-redirects to apex; GitHub Pages off |
| 2 | List view | ✅ | Search, filters, alphabetical, "Data as of" line, vacancies shown, accessibility |
| 3 | Map view | ✅ | Needs boundary data with a reuse licence; else stop. Text-only fallback |
| 4 | News | ✅ | Daily GitHub Action; The Conversation only (CC BY-ND), headline + link. Google News blocked by robots.txt |
| 5 | Photos and socials | ✅ | Commons photos only with licence; official handles only; review report |
| 6 | Post-election refresh (after 28 Nov 2026) | ⏳ | Update data + vacancies.json; validators green |
| 7 | Compliance and launch | ⛔ | About page, sitemap, robots.txt, privacy, final review. See blockers |

## National coverage (owner decision 2026-11-23: after Victoria, one parliament per stage)

Each stage repeats the Victorian pattern: check robots.txt and terms for the parliament's
member list and the boundary data, build + validate members, add boundaries to the map,
then news/photos/socials under the same rules. Stop and report if a source does not allow reuse.

| # | Parliament | Status | Notes |
|---|-----------|--------|-------|
| 8 | Federal (House of Representatives + Senate) | ⏳ | AEC boundaries; Senate = states/territories |
| 9 | New South Wales | ⏳ | |
| 10 | Queensland | ⏳ | Unicameral |
| 11 | Western Australia | ⏳ | |
| 12 | South Australia | ⏳ | |
| 13 | Tasmania | ⏳ | Multi-member divisions |
| 14 | Australian Capital Territory | ⏳ | Unicameral, multi-member |
| 15 | Northern Territory | ⏳ | Unicameral |

Site changes needed for national coverage (plan in Stage 8): a parliament picker, per-parliament
data files and "Data as of" lines, and a map that switches between parliaments.

## Stage 7 blockers
- Parliament of Victoria copyright page allows only "personal, non-commercial use,
  research or study, use within your organisation" and asks for permission beyond
  that (see `docs/data-sources.md` §2, verdict (c) "unclear"). This conflicts with
  allowing reuse and monetisation under CC BY-SA. Needs a decision or a permission
  request to info@parliament.vic.gov.au.
- `docs/data-sources.md` covers only the Parliament endpoint. Wikidata, Wikimedia
  Commons, boundary data and news sources still need entries.
