# Roadmap

Status: ✅ done · 🔄 in progress · ⏳ not started · ⛔ blocked

| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 0 | Audit and setup | ✅ | CLAUDE.md, this roadmap, Cursor site files removed |
| 1 | Move hosting to Cloudflare Pages | ✅ | Pages project `policydesk` (policydesk-2u0.pages.dev), auto-deploys from `main`. policydesk.au live on HTTPS; www 301-redirects to apex; GitHub Pages off |
| 2 | List view | ✅ | Search, filters, alphabetical, "Data as of" line, vacancies shown, accessibility |
| 3 | Map view | ✅ | Needs boundary data with a reuse licence; else stop. Text-only fallback |
| 4 | News | ⏳ | Plan first: GitHub Action vs n8n. Static `data/news/`, validator |
| 5 | Photos and socials | ⏳ | Commons photos only with licence; official handles only; review report |
| 6 | Post-election refresh (after 28 Nov 2026) | ⏳ | Update data + vacancies.json; validators green |
| 7 | Compliance and launch | ⛔ | About page, sitemap, robots.txt, privacy, final review. See blockers |

## Stage 7 blockers
- Parliament of Victoria copyright page allows only "personal, non-commercial use,
  research or study, use within your organisation" and asks for permission beyond
  that (see `docs/data-sources.md` §2, verdict (c) "unclear"). This conflicts with
  allowing reuse and monetisation under CC BY-SA. Needs a decision or a permission
  request to info@parliament.vic.gov.au.
- `docs/data-sources.md` covers only the Parliament endpoint. Wikidata, Wikimedia
  Commons, boundary data and news sources still need entries.
