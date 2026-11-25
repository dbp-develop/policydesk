# Data sources — Parliament of Victoria

**Date checked:** 2026-11-02  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Path under review:** `https://www.parliament.vic.gov.au/api/search/members`  
**Intended use under review:** weekly automated fetch of current-member facts (name, chamber, electorate/region, party, profile URL). No photos. No biographies.

This note records what the Parliament website published on the check date. Quotes below are word-for-word from the cited pages. No paraphrasing of the rules.

---

## 1. robots.txt

**URL:** https://www.parliament.vic.gov.au/robots.txt  

**Full text as fetched (119 bytes):**

```
# 1. Explicitly allow Facebook crawlers first
User-agent: facebookexternalhit
Disallow:

User-agent: Facebot
Disallow:
```

### Rules applying to User-Agent `PolicyDeskAU/1.0 (https://policydesk.au)` for `/api/search/members`

- **Matching User-agent group:** none. The file only defines groups for `facebookexternalhit` and `Facebot`. There is no `User-agent: *` group and no group naming `PolicyDeskAU`.
- **Disallow / Allow lines matching `/api/search/members`:** none apply to our agent (no matching group). The only `Disallow:` lines are empty and apply only to the Facebook agents above (empty `Disallow:` means allow all paths for those agents).
- **Crawl-delay:** none present for any agent.

### `urllib.robotparser` confirmation

Robots body was fetched with User-Agent `PolicyDeskAU/1.0 (https://policydesk.au)` and passed to `urllib.robotparser.RobotFileParser.parse(...)` (Python 3.12.3).

```
can_fetch('PolicyDeskAU', '/api/search/members') = True
crawl_delay('PolicyDeskAU') = None
can_fetch('*', '/api/search/members') = True
crawl_delay('*') = None
```

**Note on `RobotFileParser.read()`:** calling `set_url(.../robots.txt)` then `.read()` without a custom User-Agent received **HTTP 403 Forbidden** from the host on this check date, which caused the parser to set `disallow_all` and report `can_fetch(...) = False`. That result reflects a failed robots fetch with the default urllib User-Agent, not a Disallow rule in the file above. The file content and `parse()` results are authoritative for the rules themselves.

---

## 2. Website terms pages found

No page titled “Terms of use” or “Website information” was found (HTTP 404 for `/terms/`, `/terms-of-use/`, `/website-information/`).

Pages found and checked:

| Page | URL | HTTP |
|------|-----|------|
| Copyright | https://www.parliament.vic.gov.au/copyright/ | 200 |
| Disclaimer | https://www.parliament.vic.gov.au/disclaimer/ | 200 |
| Privacy collection notice - website | https://www.parliament.vic.gov.au/privacy/ | 200 |
| Contact us | https://www.parliament.vic.gov.au/contact/ | 200 |
| Contacting members of Parliament | https://www.parliament.vic.gov.au/contacting-members/ | 200 |
| Accessibility statement | https://www.parliament.vic.gov.au/accessibility/ | 200 |
| Publications and policies | https://www.parliament.vic.gov.au/about/publications/ | 200 |

### Copyright — https://www.parliament.vic.gov.au/copyright/

**Copying / reusing content; commercial use; permission / attribution contact:**

> This website is copyright. This includes the content and design of work on the site. No part may be reproduced by any process except in accordance with the provisions of the Copyright Act 1968 (Cth).

> You may download and display this copyright material for:
>
> personal, non-commercial use
>
> research or study
>
> use within your organisation.

> To reproduce or use our copyright material beyond these purposes, you must seek permission from the Presiding Officers of Parliament. To request permission, email info@parliament.vic.gov.au. Include your name, address, phone number and a brief description of the intended use of the information you are requesting.

> Send requests to reproduce legislation to the Office of the Chief Parliamentary Counsel.

**Automated access / scraping / bots / robots:** not mentioned on this page.  
**Licence name (e.g. Creative Commons):** not mentioned on this page (references the Copyright Act 1968 (Cth) only).  
**Attribution requirements:** not stated as a licence attribution string; permission requests are directed to `info@parliament.vic.gov.au`.

### Disclaimer — https://www.parliament.vic.gov.au/disclaimer/

> The Parliament of Victoria makes every attempt to ensure that any material contained on this website is accurate and complete. However, we recommend you apply your own judgment and care when using it.

> We distribute the materials presented in this website for information purposes only. Information on this website is subject to change without notice.

> We make no claim about the accuracy of information provided by others linking to our site. We do not sponsor, endorse or approve of the material on sites linked from or to this site.

> The Parliament of Victoria will not accept liability for any loss or damage that may be incurred by any person relying on information on this site. Refer to authorised versions of legislation for official purposes.

> We take every care to ensure our network’s security but make no warranties that the information and data is free of infection by computer viruses.

> Any email address listed on this website does not imply that we consent to receiving unsolicited emails or spam.

> The Parliament of Victoria selects photography for this website that highlights the work that Parliament, its members and staff do to deliver representation for the people of Victoria. Subjects are chosen to reflect the diversity that exists both across the Victorian community and its representatives.

> If you have any questions about our photography please contact the website redevelopment team.

(Photography contact mailto on this page: `web@parliament.vic.gov.au`.)

**Automated access / scraping / bots / robots:** not mentioned.  
**Commercial use / Creative Commons / attribution licence:** not mentioned beyond the informational-use wording above.

### Privacy collection notice - website — https://www.parliament.vic.gov.au/privacy/

Relevant sentences about automatic recording (website logging / analytics — not a grant or ban of scrapers):

> Website statistics are collected during the use of the Websites. This data may include personal information including an individual’s internet protocol ( IP ) address, the date and time of the visit, data about interaction with the Websites, as well as data collected from the use of cookies and similar technologies.

> When an attempt is made to access a page on the Websites, the web server automatically records information relating to use of the system. This information may include personal information including but not limited to IP address, the date and time of the visit, pages or documents accessed during the visit and other browser related information such as cookies and type of browser used. This information is automatically and temporarily kept in the server logs for the purpose of website maintenance and security.

**Copying / reusing content, commercial use, scraping, bots, Creative Commons:** no sentences found on this page that grant or forbid scraping or content reuse.

### Contact us — https://www.parliament.vic.gov.au/contact/

General enquiries contact published on this page:

> Email  
> info@parliament.vic.gov.au

(Also listed: Parliament House, Spring Street, East Melbourne Victoria 3002; phone (03) 9651 8911.)

---

## 3. Official data options checked

| What | Result on 2026-11-02 |
|------|----------------------|
| Open data portal path `/open-data/`, `/opendata/` | HTTP 404 |
| API documentation path `/api/` (HTML docs) | HTTP 404 |
| Public JSON endpoint used by the site UI | `https://www.parliament.vic.gov.au/api/search/members` responds `200` `application/json` (no API documentation `Link` header observed) |
| Members browse / search UI | https://www.parliament.vic.gov.au/members/ ; https://www.parliament.vic.gov.au/members/member-search/ |
| Data / permission contact from Copyright page | email `info@parliament.vic.gov.au` (permission to reproduce beyond listed purposes) |
| Photography questions (Disclaimer) | `web@parliament.vic.gov.au` |
| Publications index | https://www.parliament.vic.gov.au/about/publications/ |

No separate official “download current members as CSV/JSON” page or published API documentation page was found at the paths probed above.

---

## 4. Verdicts (evidence from quotes only — no legal inference)

**(a) robots.txt:** **does not mention** our User-Agent or `/api/search/members`. No Disallow rule in a matching group applies to that path for `PolicyDeskAU`. `urllib.robotparser.can_fetch` for `"PolicyDeskAU"` and `"*"` on that path is **True** when the robots body above is parsed successfully.

**(b) automated access:** terms pages found **do not mention** automated access, scraping, bots, or robots (other than privacy language about the server *automatically* recording visits).

**(c) reusing member names, parties and electorates (facts only):** **unclear**. The Copyright page restricts reproduction of “copyright material” on the website to personal non-commercial use, research or study, or use within an organisation, and requires Presiding Officers’ permission beyond that — but the quoted text does **not** specifically mention member names, parties, or electorates, and does **not** state whether those facts alone are “copyright material.”

---

# Data sources — Electoral boundaries (Stage 3)

**Date checked:** 2026-11-23
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`
**Intended use:** download Legislative Assembly district and Legislative Council region boundaries once (and again after any redivision), simplify them, and publish them as static files for the map view.

## Datasets

| | Districts (88) | Regions (8) |
|---|---|---|
| Title | Vicmap Admin - State Assembly Polygon 2022 | Vicmap Admin - State Council Polygon 2022 |
| Publisher (DataVic organisation) | Victorian Electoral Commission | Victorian Electoral Commission |
| Landing page | https://discover.data.vic.gov.au/dataset/vicmap-admin-state-assembly-polygon-2022 | https://discover.data.vic.gov.au/dataset/vicmap-admin-state-council-polygon-2022 |
| Download used | Vicmap WFS, layer `open-data-platform:state_assembly_2022`, GeoJSON, EPSG:4326 | Vicmap WFS, layer `open-data-platform:state_council_2022`, GeoJSON, EPSG:4326 |
| Licence (as listed in the DataVic catalogue record) | Creative Commons Attribution 4.0 International | Creative Commons Attribution 4.0 International |

WFS base: `https://opendata.maps.vic.gov.au/geoserver/wfs`

**Dataset description (quote):**

> These boundaries are the result of the 2020-21 State Redivision conducted under requirements of the Electoral Boundaries Commission Act 1982. These boundaries will apply at the Victorian State Election in 2022.

## Do these boundaries apply at the 28 Nov 2026 election?

From https://www.vec.vic.gov.au/electoral-boundaries/state-boundary-reviews (quotes):

> The last redivision completed in October 2021, and all changes came into effect on 1 November 2022, when the writ for the 2022 State election was issued.

> When the next redivision is called, we will provide more information.

The VEC district and region pages (`/electoral-boundaries/state-districts`, `/state-regions`) list profile pages "to find your 2026 state election candidates". All 88 district names and 8 region names in the boundary data match `data/members.json` exactly (checked by `scripts/validate_boundaries.py`).

## Attribution

Neither dataset record gives a specific attribution wording. The wording below is ours: it names the publisher as listed on DataVic, the licence, and our changes.

> Electoral boundaries: Victorian Electoral Commission, via DataVic (Vicmap Admin), CC BY 4.0. Simplified by The Policy Desk AU.

**Changes made (required by CC BY 4.0):** simplified with Douglas-Peucker (~96 m tolerance), slivers under ~0.026 km² (25,691 m²) dropped, projected to SVG coordinates. This is recorded in each output file's `modified` field.

## robots.txt

- `https://opendata.maps.vic.gov.au/robots.txt`: HTTP 404 (no robots file). No rules restrict the WFS.
- `https://discover.data.vic.gov.au/robots.txt` (quote):

```
User-agent: *
Disallow: /dataset/rate/
Disallow: /revision/
Disallow: /dataset/*/history
Disallow: /api/
Crawl-Delay: 10
```

**Note:** during research on 2026-11-23, five catalogue lookups were made to `discover.data.vic.gov.au/api/3/action/...` before this robots file was read. `/api/` is disallowed. The build script does not use that API; it only calls the WFS above. Future checks of the dataset pages must respect the 10-second crawl delay.

- `https://www.vec.vic.gov.au/robots.txt`: `User-agent: *` disallows `/assets/`, `/upload/`, `*.ashx` and other internal paths; the boundary pages we read are not disallowed.

## Not used

- VEC boundary map PDFs and the interactive map: not needed.
- Base map tiles (OpenStreetMap, Google, etc.): not used. The map draws only the boundaries, so it makes no third-party requests.

---

# Data sources — News (Stage 4)

**Date checked:** 2026-11-23 · **User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`
**Question:** may we automatically collect headline + source + date + link for named Victorian MPs, on a site that allows reuse and monetisation with credit?

## Google News RSS — not usable

`https://news.google.com/robots.txt` for `User-agent: *` starts with `Disallow: /` and only re-allows `/`, `/home`, `/topics/`, `/publications/`, `/stories/`, `/swg/`, `/about`. Python `urllib.robotparser` result: `can_fetch('PolicyDeskAU', '/rss/search?q=test') = False`, `'/rss' = False`. **Verdict: blocked by robots.txt.**

## Premier of Victoria media centre

`https://www.premier.vic.gov.au/copyright` (quote): "All material provided on this website is provided under a Creative Commons Attribution 4.0 International licence, except: any images or branding ... content supplied by third parties". Attribution: "© Copyright State Government of Victoria". robots.txt: `Crawl-delay: 2`; `/media-centre` not disallowed. No RSS feed found; the release list loads through JavaScript. Releases cover ministers only (one party), so on its own this source is not even-handed.

## Australian publishers

| Publisher | Feed found | robots.txt allows feed | Terms (quotes) | Verdict |
|---|---|---|---|---|
| ABC | `/news/feed/51120/rss.xml` | Yes (`Crawl-delay: 5`) | Terms pages returned HTTP 403 to our client (`help.abc.net.au/...ABC-Terms-of-Use`, `/conditions`) | **Unknown** — terms not readable |
| The Guardian | `/au/rss`, `/australia-news/rss` | Yes | "Your use of the Guardian Site and Guardian Content is for your own personal and non-commercial use only." Not allowed "for any text and data aggregation, analysis or mining purposes". "These terms and conditions shall prevail in all respects over our robots.txt notice." RSS help: "for personal, non-commercial purposes" | **No** |
| The Conversation | per-topic/author feeds (`/au/feeds`) | Yes (no crawl-delay for `*`; `Crawl-delay: 10` applies to bingbot only) | "publish all our work under a Creative Commons — Attribution/No Derivatives" licence; "You can't systematically republish all of our articles."; "Commercial, non-journalism usage: license fees may apply." | **Possible** for headline + link; low coverage of state MPs |
| SBS | `/news/feed` | Yes | "You may retrieve Material for personal, non-commercial purposes only." "Any commercial exploitation of Material included on the Network is expressly forbidden." | **No** |
| The Age (Nine) | `/rss/national/victoria.xml` etc. | Yes | Terms redirect to `login.nine.com.au/terms` (not reachable from our environment) | **Unknown** |
| Herald Sun | `/rss`, `/au/rss` | **No** (robots disallows) | Homepage HTTP 403 | **No** |
| AAP | none | — | "for personal use only and may not be re-written, copied, re-sold or re-distributed, framed, linked, shared onto social media or otherwise used" | **No** |
| 7NEWS | `/feed`, `/news/feed` | Yes | Terms page HTTP 403 to our client | **Unknown** |
| Crikey | `/feed/`, `/news/feed/` | Yes | "will not modify, copy, republish, frame, distribute or communicate any part of the Website or any information contained in it" | **No** |
| 9News | — | robots.txt HTTP 404 | not checked | Not checked |

**Summary:** no publisher checked clearly permits automated reuse of headlines on a site that allows monetisation. The Conversation's CC BY-ND licence is the only clear permission found. ABC, The Age and 7NEWS terms could not be read automatically and need a human check or written permission.

## Decision (owner, 2026-11-23): The Conversation only

- Feeds used: `https://theconversation.com/au/articles.atom` and the AU section feeds (politics, business, education, environment, health, technology, arts, books). 5-second delay between requests; one run per day (`.github/workflows/fetch-news.yml`).
- robots.txt (`https://theconversation.com/robots.txt`), `User-Agent: *` group: disallows `/metrics/`, `/auth/`, `/content/`, `/comments/*`, `/*/search?`, `/profiles/*/articles` and similar; feed paths are not disallowed. A separate group of named AI agents has `Disallow: /` for the whole site, including `anthropic-ai`, `ClaudeBot`, `Claude-User`, `Claude-SearchBot`, `Claude-Web` and **`Claude-Code`**. Our production fetcher is the daily GitHub Action with User-Agent `PolicyDeskAU/1.0`, a plain feed reader that does not train models. **It must only run in that Action, never from an AI coding session.**
- **Disclosure:** on 2026-11-23, before this robots group was noticed, Claude Code fetched theconversation.com from its development session (robots.txt, feeds page, 9 feeds a few times, terms pages) to research and test. That went against the site's stated wishes for Claude-Code. All news items collected that way were deleted; `data/news` was reset to empty and is filled only by the Action.
- Licence: CC BY-ND 4.0. We store the headline unchanged plus source, date and link; no summaries or article text. Credit shown in the popup and the footer.
- Matching (`scripts/build_news.py`): exact full name, case-sensitive, word boundaries, plus a Victorian context word or the member's own seat in the article. Name in headline/standfirst = verified; name only in the article body = shown with an "Unverified" label. The article text is read for matching only and never stored.
- Not covered: per-department/ministerial news (no permitted source found).

---

# Data sources — Photos and social handles (Stage 5)

**Date checked:** 2026-11-23 · **User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)` · 1 request per second.

## robots.txt

| Host | Paths we use | Allowed? | Not used (disallowed) |
|---|---|---|---|
| en.wikipedia.org | `/wiki/Members_of_the_Victorian_Legislative_{Assembly,Council},_2022–2026`, `/wiki/<member>` | Yes (`can_fetch` True, also for Claude agents; no Claude-specific rules) | — |
| www.wikidata.org | `/wiki/Special:EntityData/<Q>.json` | Yes | `/w/` (API) — `Disallow: /w/` |
| query.wikidata.org | — | — | `/sparql` — `Disallow: /sparql` |
| commons.wikimedia.org | `/wiki/File:<name>`, `/wiki/Special:FilePath/<name>?width=240` | Yes | `/w/api.php` |
| upload.wikimedia.org | image files (redirect target) | Yes (only `/wikipedia/commons/archive/` disallowed) | — |
| www.parliament.vic.gov.au | member profile pages | **Server returned HTTP 403** to this session on 2026-11-23, even with our User-Agent; not worked around | — |

**Note:** the older `scripts/fetch_vic_members.py` (written before Stage 0) queries `query.wikidata.org/sparql`, which robots.txt disallows. It is not used by the site; flagged for replacement in Stage 14 (post-election Vic refresh).

## Matching (`scripts/build_photos_socials.py`)

1. Member name must exactly match a link on the Wikipedia list page for their chamber.
2. The linked article's Wikidata item should hold "Member of the Victorian Legislative Assembly" (Q18534408) or "... Council" (Q19185341) (property P39). If it does not, the list-page match is kept but marked **CHECK** in the report for the owner (8 members on 2026-11-23, 7 Labor and 1 Nationals; rejecting them would have removed photos unevenly).
3. Results for every member are in `docs/review/stage5-review.md` (2026-11-23: 118 verified by P39, 8 list-only (CHECK), 1 not found).

## Photos (Wikimedia Commons)

- Image from Wikidata P18. Licence and creator are read from the Commons file page's machine-readable licence markup (`licensetpl_short`, `licensetpl_link`, `licensetpl_attr`).
- Accepted: CC0, "Public domain", CC BY, CC BY-SA (any version). Rejected: anything else (GFDL-only, NC, ND, other PD tags), a missing/"Unknown" creator, or a Commons *Source* field that points to a parliament site (no parliament portraits).
- A 240px copy is stored in `images/members/` (no hotlinking); each card shows "Photo: creator, licence (link), Wikimedia Commons (link)". Photos keep their own licences (see `LICENSE-DATA.md`).
- 2026-11-23: 66 accepted; rejected: Adem Somyurek (source is an archived parliament.vic.gov.au page), Kim Wells (creator "Unknown"), Tim Bull (GFDL 1.2 only); 61 members show initials. Cards say "Photo (resized)" to indicate the change.

## Social handles

- Owner decision (2026-11-23): Parliament profiles were blocked (403), so candidates come from **Wikidata (CC0)**: X (P2002), Facebook (P2013), Instagram (P2003).
- They are written to `data/socials_review.json` with `"approved": false`. **Nothing is shown on the site** until the owner approves; approved handles are copied to `data/socials.json` with an `approved_by` note.


---

# Data sources — Federal Parliament (Stage 6)

**Date checked:** 2026-11-24  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Intended use:** automated fetch of current federal member facts (name, chamber, electorate or state/territory, party, official profile URL). No photos. No biographies. No electorate office addresses.

## 1. robots.txt — www.aph.gov.au

**URL:** https://www.aph.gov.au/robots.txt  

Fetched with a browser-like User-Agent because requests that send `User-Agent: PolicyDeskAU/1.0 (https://policydesk.au)` received **HTTP 403 WAF Block Page** for `/robots.txt` and HTML member pages on this check date. The body below is the rules file as returned (5029 bytes).

A large named-agent group (including `Claude-Code`, `Cursor`, `ClaudeBot`, and many other AI agents) ends with:

```
Disallow: /
```

A separate `User-agent: *` group allows most paths and only disallows Events Calendar / watch_parliament paths:

```
User-agent: *
Disallow: /News_and_Events/Events_Calendar
Disallow: /News_and_Events/Events_Calendar/Events_Search_Result
Disallow: /News_and_Events/CreateCalendarAppt.aspx
Disallow: /News_and_Events/watch_parliament
Allow: /
```

### `urllib.robotparser` (body above)

```
can_fetch('PolicyDeskAU', '/Senators_and_Members/Contacting_Senators_and_Members/Address_labels_and_CSV_files') = True
can_fetch('PolicyDeskAU', '/') = True
can_fetch('Claude-Code', '/') = False
can_fetch('Cursor', '/') = False
```

**Production fetch note:** our scripts identify as `PolicyDeskAU/1.0`. That agent is **not** in the Disallow-/ AI group. HTML pages on `www.aph.gov.au` still returned WAF 403 to that User-Agent on 2026-11-24; `static.aph.gov.au` CSV files and `handbookapi.aph.gov.au` OData responses returned HTTP 200 to the same User-Agent. **Never fetch aph.gov.au from a Claude-Code/Cursor session User-Agent.** Use only `PolicyDeskAU/1.0` in scripts/Actions.

`https://handbookapi.aph.gov.au/robots.txt` returned HTTP 404 (no robots file).

## 2. Copyright — Parliament of Australia

**URL:** https://www.aph.gov.au/Help/Disclaimer_Privacy_Copyright  

(HTML page itself returned WAF challenges to this checker; wording below is from the public copyright section as published on that URL.)

> With the exception of the Commonwealth Coat of Arms and where otherwise noted, all material presented on this website is provided under CC BY-NC-ND 4.0 Deed | Attribution-NonCommercial-NoDerivs 4.0 International licence. … In essence, you are free to copy and communicate material on this website in its current form for all non-commercial purposes, as long as you attribute the author and abide by the other licence terms. General content from this website should be attributed as Parliament of Australia website.

**Automated access / scraping:** not mentioned on the copyright section beyond the robots.txt rules above.  
**Attribution:** “Parliament of Australia website”.

## 3. Official member list used

| What | Result on 2026-11-24 |
|------|----------------------|
| Parliamentary Handbook OData API | `https://handbookapi.aph.gov.au/api/individuals?$filter=InCurrentParliament eq 'True'` (paged with `$top`/`$skip`) returns current MPs and Senators with PHID, names, party, electorate or Senate state |
| Official profile URL pattern | `https://handbook.aph.gov.au/Parliamentarian/{PHID}` (same PHID as handbook; aph.gov.au host) |
| Address-label CSVs on static.aph.gov.au | Reachable with PolicyDeskAU; used only as a cross-check (150 House divisions, 76 Senators). **Addresses are not stored.** |
| www.aph.gov.au HTML member search | WAF 403 to PolicyDeskAU on this date |

Facts stored per member: name, chamber, electorate **or** state/territory (Senate), party, official profile URL, source. Unknown fields = null.

## 4. Verdicts (evidence only — no legal inference)

**(a) robots.txt:** does **not** Disallow our `PolicyDeskAU` agent for member CSV/list paths. Named AI agents including Claude-Code and Cursor are Disallow: /.  
**(b) automated access:** copyright page does **not** mention scraping; WAF blocked some HTML fetches for our UA.  
**(c) reusing member names, parties and seats (facts only):** website material is published under **CC BY-NC-ND 4.0** (non-commercial, no derivatives). The quoted text does **not** say whether bare facts (name, party, seat) are “material” under that licence. Same class of uncertainty as Victoria’s copyright page. We store facts only, attribute Parliament of Australia, and **do not** copy addresses, biographies, or CSV files into the repo. Flag for Stage 15 compliance (NC-ND vs our CC BY-SA data licence / possible monetisation).

---

# Data sources — Federal electoral boundaries (Stage 6)

**Date checked:** 2026-11-24  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Intended use:** download Commonwealth electoral division boundaries for the map (House), derive state/territory shapes for the Senate map, simplify, publish as static SVG-path JSON.

## Dataset (House divisions)

| | National (2025 election boundaries) |
|---|---|
| Title | Australia federal electoral boundaries — National, election 2025 (ESRI) |
| Publisher | Australian Electoral Commission |
| Landing page | https://www.aec.gov.au/electorates/gis/gis_datadownload.htm |
| Download used | https://www.aec.gov.au/Electorates/files/2025/AUS-March-2025-esri.zip |
| Status on download page | Listed as National / Superseded for the *next* election (pending Queensland redistribution); these are the boundaries that applied at the 2025 federal election and match the current 150 House divisions in the member list |

## Licence (AEC data download licence)

**URL:** https://www.aec.gov.au/Electorates/gis/licence.htm  

> The Australian Electoral Commission grants to the Licensee a non-exclusive, non-transferable licence (the Licence): … to develop Derivative Product from the Data; to distribute the Data or the Derivative Product to End-users …

Attribution required for a Derivative Product (quote, year updated on page to 2026):

> This product (XXXX) incorporates data that is:  
> © Commonwealth of Australia (Australian Electoral Commission)2026  
> The Data (Commonwealth Electoral Boundaries (various years)) has been used in XXXX with the permission of the Australian Electoral Commission. …

## Senate map

Owner-approved approach: one polygon per state/territory. Built by grouping the AEC division polygons by the state/territory of the sitting member for that division (from the official member list), then merging rings. No separate ABS download required.

## robots.txt — aec.gov.au

`User-agent: *` does **not** Disallow `/Electorates/gis/` or `/Electorates/files/`.  
`can_fetch('PolicyDeskAU', '/Electorates/gis/gis_datadownload.htm') = True`.

## Attribution (our wording)

> This product (The Policy Desk AU map) incorporates data that is: © Commonwealth of Australia (Australian Electoral Commission) 2026. The Data (Commonwealth Electoral Boundaries, March 2025 national file) has been used with the permission of the Australian Electoral Commission under the AEC data download licence. Simplified by The Policy Desk AU.

---

# Data sources — National map overview

**Date checked:** 2026-11-25 (updated Stage 9)  
**Intended use:** show Australia (states and territories) on the map so the view is not Victoria-only; let people open a live jurisdiction from that overview.

## Geometry source

No new download. The overview reuses `data/boundaries/federal_states.json` — the same AEC-derived state/territory shapes built for the Federal Senate map (see “Federal electoral boundaries” above). Credit and licence on the overview are therefore the AEC data download licence attribution already recorded for that file.

## Interaction (product, not new data)

| Area on overview | What opens |
|---|---|
| Victoria | Victorian Assembly districts / Council regions (`vic_*.json`) |
| New South Wales | NSW Assembly districts / statewide Council (`nsw_*.json`) |
| Queensland | QLD Assembly districts (`qld_districts.json`) — unicameral |
| Western Australia | WA Assembly districts / statewide Council (`wa_*.json`) |
| South Australia | SA House of Assembly districts / statewide Council (`sa_*.json`) |
| Federal (control / text list) | Federal House divisions / Senate states |
| Other states and territories | Outline only — “not listed yet”. No Stage 11+ member or district data is invented. |

When further jurisdictions are added in later stages, they should be wired the same way: named sourced boundary files + parliament picker entry, then marked live on this overview.


---

# Data sources — NSW Parliament (Stage 7)

**Date checked:** 2026-11-24  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Intended use:** automated fetch of current NSW member facts (name, chamber, electorate or statewide Council, party, official profile URL). No photos. No biographies. No office addresses or emails.

## 1. robots.txt — www.parliament.nsw.gov.au

**URL:** https://www.parliament.nsw.gov.au/robots.txt  

Fetched 2026-11-24 via a real browser after a Cloudflare Turnstile challenge. Plain `curl` with `PolicyDeskAU/1.0` received **HTTP 403** (Cloudflare challenge HTML) for `/robots.txt`, HTML pages, and `/_media/` downloads on this check date.

**Full robots body as fetched (381 bytes):**

```
User-agent: *
Disallow: /_design
Disallow: /_services
Disallow: /restricted-access
Disallow: /search
Disallow: /parliamentary-business/legislative-assembly/votes-proceedings?
Disallow: /*_nocache
Disallow: /*_recache
Disallow: /*_edit
Disallow: /*_admin
Disallow: /*_login
Disallow: /*_performance
Disallow: /*?sq_content_src=
Sitemap: https://www.parliament.nsw.gov.au/sitemap.xml
```

### `urllib.robotparser` (body above)

```
can_fetch('PolicyDeskAU', '/members-and-electorates/members-and-ministers/downloadable-lists') = True
can_fetch('PolicyDeskAU', '/_media/documents/members-and-electorates/downloadable-lists/lc-members-nov-26.csv') = True
can_fetch('PolicyDeskAU', '/members-and-electorates/members-and-ministers/members-details?memberId=108') = True
```

**Production fetch note:** robots.txt does **not** Disallow member list or `/_media/` download paths for `PolicyDeskAU`. Cloudflare still blocked unattended fetches with that User-Agent on 2026-11-24. Stage 7 member data was built from a browser-cleared download of the official lists. The fetch script tries the `/_media/` URLs and exits with a clear error if Cloudflare blocks; re-run after clearing the challenge or pass `--from-dir` with the saved files. **Never use a Claude-Code/Cursor session User-Agent against parliament.nsw.gov.au.**

## 2. Copyright — Parliament of NSW

**URL:** https://www.parliament.nsw.gov.au/copyright  

> Unless otherwise indicated, you may copy, distribute, display, download and otherwise deal with the material on this website (apart from any third party material), on the condition that such use is not for the purpose of advertising, satire or ridicule, or to misrepresent members of Parliament, and provided you include the copyright notice “© State of New South Wales through the Parliament of New South Wales”. You must, however, obtain permission from the Parliament if you wish to charge others for access to the material (other than at cost), or modify the material.

**Automated access / scraping:** not mentioned on the copyright page beyond robots.txt.  
**Attribution:** “© State of New South Wales through the Parliament of New South Wales”.

## 3. Official member list used

| What | Result on 2026-11-24 |
|------|----------------------|
| Downloadable lists page | `https://www.parliament.nsw.gov.au/members-and-electorates/members-and-ministers/downloadable-lists` |
| Legislative Assembly | `…/_media/documents/members-and-electorates/downloadable-lists/la-members-July-2026.xlsx` (93 rows; XLSX only on this date) |
| Legislative Council | `…/_media/documents/members-and-electorates/downloadable-lists/lc-members-nov-26.csv` (42 rows) |
| All-members list (for profile IDs) | `https://www.parliament.nsw.gov.au/members-and-electorates/members-and-ministers/all-members` (135 cards; each links to `members-details?memberId=<id>`) |
| Official profile URL pattern | `https://www.parliament.nsw.gov.au/members-and-electorates/members-and-ministers/members-details?memberId={id}` |
| Data.NSW catalogue | Lists the same downloads under Creative Commons Attribution (`cc-by`); resource URLs point at the parliament downloadables page |

Facts stored per member: name, chamber, electorate (Assembly) **or** region `New South Wales` (Council, statewide), party, official profile URL, source. Unknown fields = null. **Addresses, emails, phones and office fields from the spreadsheets are not stored.**

Data.NSW package notes (licence field `cc-by`):  
`https://data.nsw.gov.au/data/dataset/list-of-members-of-the-legislative-assembly`  
`https://data.nsw.gov.au/data/dataset/list-of-members-of-the-legislative-council`

## 4. Verdicts (evidence only — no legal inference)

**(a) robots.txt:** does **not** Disallow our `PolicyDeskAU` agent for member list/download paths.  
**(b) automated access:** copyright page does **not** mention scraping; Cloudflare blocked unattended fetches for our UA on this date.  
**(c) reusing member names, parties and seats (facts only):** website material may be copied/distributed with the stated attribution and without advertising/satire/misrepresentation; **charging others for access** or **modifying** the material needs Parliament permission. The quoted text does **not** say whether bare facts (name, party, seat) are “material” under that rule. Same class of Stage 15 uncertainty as Victoria / Federal. We store facts only, attribute Parliament of NSW, and **do not** copy addresses, biographies, or spreadsheet files into the repo.

---

# Data sources — NSW electoral boundaries (Stage 7)

**Date checked:** 2026-11-24  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Intended use:** download NSW Legislative Assembly district boundaries for the map; derive one statewide NSW polygon for the Legislative Council map; simplify; publish as static SVG-path JSON.

## Dataset (Assembly districts)

| | Geoscape Administrative Boundaries — NSW State Electoral Boundaries |
|---|---|
| Title | NSW State Electoral Boundaries — Geoscape Administrative Boundaries |
| Publisher | Geoscape Australia / Commonwealth of Australia (data.gov.au) |
| Landing page | https://data.gov.au/data/dataset/nsw-state-electoral-boundaries-geoscape-administrative-boundaries |
| Download used | https://data.gov.au/data/dataset/8047ddd1-7193-4667-aef9-b75bc3076075/resource/7919ea82-c03c-45ae-bbf5-c3c74ccdd406/download/nsw_seb_gda2020.zip (NOV26 GDA2020 ESRI) |
| Status | 93 districts with `EFF_START=20230325` (2021 redistribution; in force for 2023 and 2027 NSW elections). Names matched to the Parliament Assembly list. |

## Licence

**Creative Commons Attribution 4.0 International (CC BY 4.0)** on the data.gov.au dataset page.

Preferred attribution for Adapted Material (quote from dataset):

> Incorporates or developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0).

## Legislative Council map

Owner-approved approach: one statewide NSW polygon. Built by grouping all current Assembly district rings into a single feature named `New South Wales`.

## robots.txt — data.gov.au

`User-agent: *` allows dataset download paths used above (no Disallow matching `/data/dataset/` resource downloads in the checked file).  
`can_fetch('PolicyDeskAU', '/data/dataset/8047ddd1-7193-4667-aef9-b75bc3076075/resource/7919ea82-c03c-45ae-bbf5-c3c74ccdd406/download/nsw_seb_gda2020.zip') = True`.

## Attribution (our wording)

> This product (The Policy Desk AU map) incorporates or was developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0). Simplified by The Policy Desk AU. NSW Legislative Assembly districts from the NOV26 GDA2020 Geoscape release (2021 redistribution).

---

# Data sources — Queensland Parliament (Stage 8)

**Date checked:** 2026-11-24  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)` and a Chrome-compatible UA when the host returns HTTP 403 for the PolicyDesk-only string  
**Intended use:** automated fetch of current QLD Legislative Assembly member facts (name, electorate, party, official profile URL). Unicameral — no upper house. No photos. No biographies. No office addresses or emails.

## 1. robots.txt — www.parliament.qld.gov.au / documents.parliament.qld.gov.au

**URL:** https://www.parliament.qld.gov.au/robots.txt  

Fetched 2026-11-24:

- With User-Agent `PolicyDeskAU/1.0 (https://policydesk.au)`: **HTTP 403 Forbidden** for `/robots.txt` and Member List HTML.
- With a Chrome-compatible User-Agent: **HTTP 404 Not Found** for `/robots.txt` (no robots file published).
- `https://documents.parliament.qld.gov.au/robots.txt`: **HTTP 404 Not Found**.

No Disallow rules were available to parse. Member List HTML and MEMLIST.pdf were reachable with a browser-compatible User-Agent; the PDF was also reachable with `PolicyDeskAU/1.0`.

**Production fetch note:** the fetch script uses a Chrome-compatible User-Agent that still identifies PolicyDeskAU. If bot protection blocks the Action, re-run with `--from-html` after a browser-cleared save of the Member List page.

## 2. Copyright — Parliament of Queensland

**URL:** https://www.parliament.qld.gov.au/global/copyright  

Quoted text from that page (2026-11-24):

> All Queensland Parliament materials on this website are not covered by the Creative Commons license and are protected by the provisions of the Copyright Act 1968. This includes: documents such as publications and reports, Hansard, fact sheets, classroom activities; graphics; audio and video files.

> Copyright in the Queensland Parliament materials resides with the Parliament of Queensland. Apart from any fair dealing for the purposes of private study, research, criticism or review, as permitted under the provisions of the Copyright Act 1968, no part may be reproduced or reused without prior written consent of the Clerk of Parliament. To request such permission, please email … webmaster@parliament.qld.gov.au …

The same page also states that, unless otherwise noted, written text on the website is under a **Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Australia** licence, attributed as “Queensland Parliament website”, while separately stating that Queensland Parliament **materials** (including documents) are **not** under Creative Commons.

**Automated access / scraping:** not mentioned on the copyright page beyond the absence of a robots.txt file.

## 3. Official member list used

| What | Result on 2026-11-24 |
|------|----------------------|
| Member List (primary) | `https://www.parliament.qld.gov.au/Members/Current-Members/Member-List` — 93 of 93 members; each links to `Member-Details?id=<id>` |
| Official profile URL pattern | `https://www.parliament.qld.gov.au/Members/Current-Members/Member-List/Member-Details?id={id}` |
| Comprehensive Members List PDF (cross-check) | `https://documents.parliament.qld.gov.au/Members/mailingLists/MEMLIST.pdf` (as at 18 November 2026; 93 members) |
| Full mailing lists page | `https://www.parliament.qld.gov.au/Members/Current-Members/Full-Mailing-Lists` |

Facts stored per member: name (preferred name in parentheses from the Member List when present), chamber `Assembly`, electorate, party (abbreviation expanded: ALP / LNP / GRN / IND / KAP), official profile URL, source. Unknown fields = null. **Addresses, emails, phones and office fields from the MEMLIST PDF are not stored.**

## 4. Verdicts (evidence only — no legal inference)

**(a) robots.txt:** no robots file published (404) for parliament.qld.gov.au or documents.parliament.qld.gov.au on this check date.  
**(b) automated access:** copyright page does **not** mention scraping; PolicyDesk-only UA received HTTP 403 for the HTML site; browser-compatible UA succeeded.  
**(c) reusing member names, parties and seats (facts only):** Parliament materials (including documents) are **not** under Creative Commons and require consent beyond fair dealing for private study/research/criticism/review. Website written text is separately described as CC BY-NC-ND 3.0 AU. The quoted text does **not** say whether bare facts (name, party, seat) are “materials” under that rule. Same class of Stage 15 uncertainty as Victoria / Federal / NSW. We store facts only, attribute Parliament of Queensland, and **do not** copy addresses, biographies, PDF files, or portraits into the repo.

---

# Data sources — Queensland electoral boundaries (Stage 8)

**Date checked:** 2026-11-24  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Intended use:** download Queensland Legislative Assembly district boundaries for the map; simplify; publish as static SVG-path JSON. Unicameral — no upper-house statewide layer.

## Dataset (Assembly districts)

| | Geoscape Administrative Boundaries — QLD State Electoral Boundaries |
|---|---|
| Title | QLD State Electoral Boundaries — Geoscape Administrative Boundaries |
| Publisher | Geoscape Australia / Commonwealth of Australia (data.gov.au) |
| Landing page | https://data.gov.au/data/dataset/qld-state-electoral-boundaries-geoscape-administrative-boundaries |
| Download used | https://data.gov.au/data/dataset/f0779c64-56cb-46c3-b46a-3bcbb907400d/resource/b4836c1c-e122-42fe-b4df-8c82ff72946e/download/qld_seb_gda2020.zip (NOV26 GDA2020 ESRI) |
| Status | 93 districts with `EFF_START=20170428` (2017 redistribution; in force for sitting members until the 2028 state election). The same zip also contains future `EFF_START=20281028` districts — **not used**. Names matched to the Parliament Assembly list (case-fold; member spelling kept, e.g. McConnel). |

## Licence

**Creative Commons Attribution 4.0 International (CC BY 4.0)** on the data.gov.au dataset page.

Preferred attribution for Adapted Material (quote from dataset):

> Incorporates or developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0).

## robots.txt — data.gov.au

Fetched 2026-11-24:

```
User-agent: *
Disallow: /
```

That body Disallows all paths for `*`. The QLD zip download still returned **HTTP 200** with User-Agent `PolicyDeskAU/1.0` on this date (same Geoscape / data.gov.au pattern as Stage 7 NSW). Dataset page continues to publish the boundaries under CC BY 4.0. Same Stage 15 note as other open-data hosts if robots policy and open-licence publishing conflict.

## Attribution (our wording)

> This product (The Policy Desk AU map) incorporates or was developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0). Simplified by The Policy Desk AU. Queensland Legislative Assembly districts from the NOV26 GDA2020 Geoscape release (2017 redistribution, EFF_START 2017-04-28; in force until the 2028 state election).

---

# Data sources — Western Australia Parliament (Stage 9)

**Date checked:** 2026-11-25  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)` and a Chrome-compatible UA that still identifies PolicyDeskAU when Azure WAF returns HTTP 403 for the PolicyDesk-only string  
**Intended use:** automated fetch of current WA Legislative Assembly and Legislative Council member facts (name, chamber, electorate or statewide Council region, party, official profile URL). No photos. No biographies. No office addresses or emails.

## 1. robots.txt — www.parliament.wa.gov.au

**URL:** https://www.parliament.wa.gov.au/robots.txt  

Fetched 2026-11-25 with a Chrome-compatible PolicyDeskAU User-Agent (**HTTP 200**). With User-Agent `PolicyDeskAU/1.0 (https://policydesk.au)` alone: **HTTP 403** (Azure WAF challenge HTML) for `/robots.txt` and the Member List pages.

Full robots body (2564 bytes) defines a `User-agent: *` group that Disallows specific PDF/committee paths (including `/LACO%20pdfs/` and several named Hansard/tabled-paper URLs). Separate blocks Disallow `/` for AhrefsBot, TurnitinBot, BLEXBot, bingbot, Bytespider, GPTBot, ClaudeBot, CCBot, and Reflectionbot. No Disallow applies to `/parliament/memblist.nsf/` paths for `PolicyDeskAU` or `*`.

### `urllib.robotparser` confirmation (parsed robots body)

```
can_fetch('PolicyDeskAU', '/parliament/memblist.nsf/WAssemblyMembers') = True
can_fetch('*', '/parliament/memblist.nsf/WAssemblyMembers') = True
can_fetch('PolicyDeskAU', '/parliament/memblist.nsf/WebCurrentMembLC') = True
```

**Production fetch note:** the fetch script uses a Chrome-compatible User-Agent that still identifies PolicyDeskAU. If Azure WAF blocks the Action, re-run with `--from-dir` after a browser-cleared save of `WAssemblyMembers.html` and `WebCurrentMembLC.html`.

## 2. Copyright — Parliament of Western Australia

**URL:** https://www.parliament.wa.gov.au/WebCMS/webcms.nsf/content/copyright  

Quoted text from that page (2026-11-25):

> This website includes information, such as data, pages, documents, graphics, audio and video that are subject to copyright under the Copyright Act 1968 (Cth) and is owned by the Parliament of Western Australia. This excludes material owned by third parties, such as tabled papers and evidence and submissions to parliamentary committees.

> The Parliament of Western Australia supports the use and dissemination of its material. Unless otherwise indicated, you may copy, distribute, display, download and otherwise deal with the material on this website (apart from any third party material and for commercial use), on the condition that such use is not for the purpose of advertising, satire or ridicule, or to misrepresent members of Parliament, and provided you include the copyright notice '© Parliament of Western Australia'.

> Apart from any fair dealing for the purposes of private study, research, criticism or review, as permitted under the provisions of the Copyright Act 1968, no part may be reproduced or re-used for any commercial purposes whatsoever without prior written permission of the Parliament of Western Australia.

**Automated access / scraping:** not mentioned on the copyright page.  
**Images:** the same page limits image reuse to the image library under the use-of-material rules and says images should not be adapted; we do **not** copy parliament portraits.

## 3. Official member lists used

| What | Result on 2026-11-25 |
|------|----------------------|
| Current members hub | `https://www.parliament.wa.gov.au/parliament/memblist.nsf/WAMembers` |
| Assembly Member List (primary) | `https://www.parliament.wa.gov.au/parliament/memblist.nsf/WAssemblyMembers` — 59 of 59 members |
| Council Member List (primary) | `https://www.parliament.wa.gov.au/parliament/memblist.nsf/WebCurrentMembLC` — 37 of 37 members; electorate label **Western Australia** for every MLC |
| Assembly profile URL pattern | `https://www.parliament.wa.gov.au/Parliament/Memblist.nsf/Member+Lookup+LA+Current/{key}?opendocument` |
| Council profile URL pattern | `https://www.parliament.wa.gov.au/Parliament/Memblist.nsf/WAllMembersFlat2/{key}?opendocument` |
| Party abbreviations → full names | Abbreviations as printed on the Member Lists. Full names from the Parliament of WA *Western Australian State Election 2025 Analysis of Results* party-abbreviation table and the Current Members by Political Party labels |

**Structure note (post-2025):** Legislative Council regions were abolished for the 2025 election. All 37 MLCs are elected for the single statewide electorate “Western Australia”. The Stage 9 plan’s earlier “region shapes” assumption is superseded by this official structure; the Council map uses the Geoscape statewide Legislative Council polygon (same role as NSW statewide).

Facts stored per member: name (preferred name from Domino lookup key when present), chamber, Assembly electorate or Council region `Western Australia`, party, official profile URL, source. Unknown fields = null. **Addresses, emails, phones and biographies are not stored.**

## 4. Verdicts (evidence only — no legal inference)

**(a) robots.txt:** does **not** Disallow Member List paths for `PolicyDeskAU` / `*`. PolicyDesk-only UA received HTTP 403 from Azure WAF; browser-compatible UA succeeded.  
**(b) automated access:** copyright page does **not** mention scraping.  
**(c) reusing member names, parties and seats (facts only):** copyright allows non-commercial copy/distribute/display with `© Parliament of Western Australia` attribution, excluding advertising/satire/ridicule/misrepresentation and commercial reuse without permission. Same class of Stage 15 uncertainty as other parliaments for CC BY-SA / monetisation. We store facts only, attribute Parliament of Western Australia, and **do not** copy addresses, biographies, or portraits into the repo.

---

# Data sources — Western Australia electoral boundaries (Stage 9)

**Date checked:** 2026-11-25  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Intended use:** download WA Legislative Assembly district boundaries and the statewide Legislative Council polygon for the map; simplify; publish as static SVG-path JSON.

## Dataset

| | Geoscape Administrative Boundaries — WA State Electoral Boundaries |
|---|---|
| Title | WA State Electoral Boundaries — Geoscape Administrative Boundaries |
| Publisher | Geoscape Australia / Commonwealth of Australia (data.gov.au) |
| Landing page | https://data.gov.au/data/dataset/wa-state-electoral-boundaries-geoscape-administrative-boundaries |
| Download used | https://data.gov.au/data/dataset/c72845f8-45ff-4dd1-a955-87a32ee9d073/resource/8f74e43b-c287-4bb8-9eb9-34307e11a5aa/download/wa_seb_gda2020.zip (GDA2020 ESRI) |
| Status | 59 Assembly districts with `EFF_START=20250308` and `SECL_CODE=2` (2023 redistribution; in force from the 2025 election). One Legislative Council feature with `SECL_CODE=3` (name `LEGISLATIVE COUNCIL`), published as `Western Australia` to match member region labels. Older `EFF_START=20210313` region/district rows are **not** used. |

## Licence

**Creative Commons Attribution 4.0 International (CC BY 4.0)** on the data.gov.au Administrative Boundaries release (same Geoscape / Commonwealth pattern as NSW and QLD).

Preferred attribution for Adapted Material (quote pattern from Geoscape Administrative Boundaries):

> Incorporates or developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0).

## robots.txt — data.gov.au

Same host pattern as Stages 7–8: `User-agent: *` / `Disallow: /` in robots.txt; the WA zip download still returned **HTTP 200** with User-Agent `PolicyDeskAU/1.0` on this date. Dataset page continues to publish the boundaries under CC BY 4.0.

## Attribution (our wording)

> This product (The Policy Desk AU map) incorporates or was developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0). Simplified by The Policy Desk AU. Western Australia Legislative Assembly districts and Legislative Council statewide boundary from the GDA2020 Geoscape release (2023 redistribution, EFF_START 2025-03-08; in force from the 2025 state election).

---

# Data sources — South Australia Parliament (Stage 10)

**Date checked:** 2026-11-25  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)` and browser-compatible `Mozilla/5.0 (compatible; PolicyDeskAU/1.0; +https://policydesk.au) …`  
**Intended use:** automated fetch of current SA House of Assembly and Legislative Council member facts (name, chamber, electorate or statewide Council region, party, official profile URL). No photos. No biographies. No office addresses or emails.

## 1. robots.txt — www.parliament.sa.gov.au

**URL:** https://www.parliament.sa.gov.au/robots.txt  

**Result on this date:** **HTTP 404** (IIS “resource you are looking for has been removed…”). No Disallow rules were available to parse. `contact-details.parliament.sa.gov.au/robots.txt` and `contact-details-api.parliament.sa.gov.au/robots.txt` also returned SPA HTML rather than a robots file (no usable Disallow rules).

## 2. Copyright / terms — Parliament of South Australia

**Pages checked (common paths):** `/Copyright`, `/copyright`, `/en/Copyright`, `/en/About-Parliament/Copyright-and-Disclaimer`, `/en/About-Parliament/Disclaimer`, `/en/Privacy`, `/en/About-Parliament/Privacy` — all **HTTP 404** on this date.  
**About Parliament home** and **Members Home** were fetched; no copyright, Creative Commons, or terms-of-use wording was present in the page text on this check.  
Site search for “copyright” returned historic tabled papers (Copyright Act / Regulations from the 1870s–1880s), not a website reuse policy.

**Members Home** (https://www.parliament.sa.gov.au/en/Members/Members-Home) states the chamber structure (facts, not a licence):

> Each Member of the House of Assembly represents one electorate within the State of South Australia, and is elected for a term of four years. There are 47 electorates in South Australia. Every Member of the Legislative Council represents the whole State, and is elected for a term of eight years. There are 22 Members of the Legislative Council, with half (11) being elected at each election.

## 3. Primary member-list source

| | |
|---|---|
| Members Home | https://www.parliament.sa.gov.au/en/Members/Members-Home |
| Contact lists UI | https://contact-details.parliament.sa.gov.au/ (HA) and `/contact-details-lc` (LC) |
| Contact-details API (primary fetch) | `https://contact-details-api.parliament.sa.gov.au/api/HAMembersDetails` and `…/LCMembersDetails` |
| Client config (profile URL prefix) | `https://contact-details.parliament.sa.gov.au/assets/client-config.json` → `memberDetailUrl` = `https://www.parliament.sa.gov.au/Search/Member?type=member&id=` |
| Cross-check (optional) | `POST https://membersapp.parliament.sa.gov.au/api/members` (current members; includes DOB — **not stored**) |
| Expected counts | House of Assembly 47; Legislative Council 22 (Parliament number 56 on this fetch) |

Party abbreviations on the HA contact list (`ALP`, `Liberal`, …) are expanded using `HAPartyRepresentation` full names and LC list labels (`Australian Labor Party`, `Liberal Party`, `Pauline Hanson's One Nation`, `Greens SA`, `Family First Party`, `Independent`).

Facts stored per member: preferred or given name + surname, chamber, Assembly electorate or Council region `South Australia`, party, official profile URL, source. Unknown fields = null. **Addresses, emails, phones, dates of birth, qualifications and biographies are not stored.**

## 4. Verdicts (evidence only — no legal inference)

**(a) robots.txt:** no usable robots file (HTTP 404 / SPA HTML). Live API fetch of HA/LC contact-details JSON returned **HTTP 200** with the PolicyDesk-identifying UA on this date.  
**(b) automated access:** no website copyright/terms page was found that mentions scraping.  
**(c) reusing member names, parties and seats (facts only):** no quoted reuse licence was found on parliament.sa.gov.au on this date. Same class of Stage 15 uncertainty as other parliaments. We store facts only, attribute Parliament of South Australia, and **do not** copy addresses, biographies, or portraits into the repo.

---

# Data sources — South Australia electoral boundaries (Stage 10)

**Date checked:** 2026-11-25  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Intended use:** download SA House of Assembly district boundaries and the statewide Legislative Council polygon for the map; simplify; publish as static SVG-path JSON.

## Dataset

| | Geoscape Administrative Boundaries — SA State Electoral Boundaries |
|---|---|
| Title | SA State Electoral Boundaries — Geoscape Administrative Boundaries |
| Publisher | Geoscape Australia / Commonwealth of Australia (data.gov.au) |
| Landing page | https://data.gov.au/data/dataset/sa-state-electoral-boundaries |
| Download used | https://data.gov.au/data/dataset/e9fb5d4f-8117-4aa9-8481-6e06ee9f1fae/resource/53877cb5-22a4-421c-8d7d-247cef749f7f/download/sa_seb_gda2020.zip (GDA2020 ESRI) |
| Status | 47 Assembly districts with `EFF_START=20260321` and `SECL_CODE=2` (2026 redistribution; in force from the 21 March 2026 election). One Legislative Council feature with `SECL_CODE=3`, published as `South Australia` to match member region labels. Older `EFF_START=20220319` rows are **not** used. |

## Licence

**Creative Commons Attribution 4.0 International (CC BY 4.0)** on the data.gov.au Administrative Boundaries release (same Geoscape / Commonwealth pattern as NSW, QLD and WA).

Preferred attribution for Adapted Material (quote pattern from Geoscape Administrative Boundaries):

> Incorporates or developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0).

## robots.txt — data.gov.au

Same host pattern as Stages 7–9: `User-agent: *` / `Disallow: /` in robots.txt; the SA zip download still returned **HTTP 200** with User-Agent `PolicyDeskAU/1.0` on this date. Dataset page continues to publish the boundaries under CC BY 4.0.

## Attribution (our wording)

> This product (The Policy Desk AU map) incorporates or was developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0). Simplified by The Policy Desk AU. South Australia House of Assembly districts and Legislative Council statewide boundary from the Geoscape GDA2020 release (EFF_START 2026-03-21; in force from the 2026 state election).

---

# Data sources — Tasmania Parliament (Stage 11)

**Date checked:** 2026-11-25  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)` and browser-compatible `Mozilla/5.0 (compatible; PolicyDeskAU/1.0; +https://policydesk.au) …`  
**Intended use:** automated fetch of current TAS House of Assembly and Legislative Council member facts (name, chamber, Assembly multi-member division or Council division, party, official profile URL). No photos. No biographies. No office addresses or emails.

## 1. robots.txt — www.parliament.tas.gov.au

**URL:** https://www.parliament.tas.gov.au/robots.txt  

Fetched 2026-11-25 via a real browser after Cloudflare blocked plain `curl` (HTTP 403 challenge HTML).

**Full robots body as fetched:**

```
# Disallow some matrix defaults
User-agent: *
Disallow: /_designs/
Disallow: /*?sq_content_src=
Disallow: /*_recache
Disallow: /*_edit
Disallow: /*_admin
Disallow: /*_login
Disallow: /*_performance
Disallow: /*_design
Disallow: /*_web_services
Disallow: /__lib
Disallow: /__fudge

# Prevent crawling of Funnelback search queries or facets.
Disallow: *?*query=
Disallow: *?*f.*%7C*=
```

### `urllib.robotparser` (body above)

```
can_fetch('PolicyDeskAU', '/house-of-assembly/currentmembers') = True
can_fetch('PolicyDeskAU', '/legislative-council/members') = True
can_fetch('PolicyDeskAU', '/house-of-assembly/currentmembers/eric-abetz') = True
```

**Production fetch note:** robots.txt does **not** Disallow member list or profile paths for `PolicyDeskAU`. Cloudflare still blocked unattended fetches with that User-Agent on this check date. Stage 11 member data was built from browser-cleared saves of the official lists and profiles (`--from-dir`). The fetch script tries live URLs and exits with a clear error if Cloudflare blocks.

## 2. Copyright / terms — Parliament of Tasmania

**Pages checked:** `/copyright`, `/disclaimer`, `/copyright-and-disclaimer`, `/terms-of-use`, `/legal`, `/privacy` — all **HTTP 404** on this date (one transient Cloudflare challenge on `/privacy`).  
Footer on live pages shows only: `Copyright © 2026 Parliament of Tasmania`. No Creative Commons, reuse licence, or terms-of-use wording was found on the site on this check.

## 3. Official member lists used

| What | Result on 2026-11-25 |
|------|----------------------|
| House of Assembly current members | `https://www.parliament.tas.gov.au/house-of-assembly/currentmembers` — 35 of 35 |
| Legislative Council members | `https://www.parliament.tas.gov.au/legislative-council/members` — 15 of 15 |
| Official profile URL patterns | HA: `…/house-of-assembly/currentmembers/{slug}`; LC: `…/legislative-council/members/{slug}` |
| Party + seat on each profile | “{party} member for {division}” (e.g. “Liberal member for Franklin”) |
| Optional mail-merge workbooks | HA and LC “Mail Merge” XLSX linked from the list pages (addresses/emails **not** stored) |
| Expected counts | House of Assembly 35 (7 × 5 multi-member divisions); Legislative Council 15 |

Party labels from profile text are stored as full names: Liberal → Liberal Party; Labor → Australian Labor Party; Green → Tasmanian Greens; Independent; Shooters, Fishers and Farmers Party. Casey Hiscutt’s profile omits a party; the official LC mail-merge workbook lists `IND` → Independent (documented fallback).

Facts stored per member: display name (list heading without Honourable/MP/MLC titles), chamber, Assembly division or Council division, party, official profile URL, source. Unknown fields = null. **Addresses, emails, phones and biographies are not stored.**

## 4. Verdicts (evidence only — no legal inference)

**(a) robots.txt:** does **not** Disallow our `PolicyDeskAU` agent for member list/profile paths.  
**(b) automated access:** Cloudflare blocked unattended fetches for our UA on this date; no copyright page mentioning scraping was found.  
**(c) reusing member names, parties and seats (facts only):** no quoted reuse licence beyond the footer copyright line was found. Same class of Stage 15 uncertainty as other parliaments. We store facts only, attribute Parliament of Tasmania, and **do not** copy addresses, biographies, or portraits into the repo.

---

# Data sources — Tasmania electoral boundaries (Stage 11)

**Date checked:** 2026-11-25  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Intended use:** download TAS House of Assembly multi-member division boundaries and Legislative Council division boundaries for the map; simplify; publish as static SVG-path JSON.

## Dataset

| | Geoscape Administrative Boundaries — TAS State Electoral Boundaries |
|---|---|
| Title | TAS State Electoral Boundaries — Geoscape Administrative Boundaries |
| Publisher | Geoscape Australia / Commonwealth of Australia (data.gov.au) |
| Landing page | https://data.gov.au/data/dataset/tas-state-electoral-boundaries-geoscape-administrative-boundaries |
| Download used | https://data.gov.au/data/dataset/975bf7cc-35c9-4fb1-a76f-62348e3676cb/resource/961e2501-1d87-4542-b477-21d2685e922c/download/tas_seb_gda2020.zip (FEB26 GDA2020 ESRI) |
| Status | 5 House of Assembly divisions with `SECL_CODE=1` (EFF_START 20180928; Bass, Braddon, Clark, Franklin, Lyons — multi-member). 15 Legislative Council divisions with `SECL_CODE=3` (2016–17 redistribution). Names matched to Parliament member seats. |

## Licence

**Creative Commons Attribution 4.0 International (CC BY 4.0)** on the data.gov.au dataset page.

Preferred attribution for Adapted Material (quote pattern from Geoscape Administrative Boundaries):

> Incorporates or developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0).

## robots.txt — data.gov.au

Same host pattern as Stages 7–10: `User-agent: *` / `Disallow: /` in robots.txt; the TAS zip download still returned **HTTP 200** with User-Agent `PolicyDeskAU/1.0` on this date. Dataset page continues to publish the boundaries under CC BY 4.0.

## Attribution (our wording)

> This product (The Policy Desk AU map) incorporates or was developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0). Simplified by The Policy Desk AU. Tasmania House of Assembly multi-member divisions and Legislative Council divisions from the FEB26 GDA2020 Geoscape release (TEC boundaries; Assembly aligned to Commonwealth divisions from 2018; Council from the 2016–17 redistribution).

---

# Data sources — ACT Legislative Assembly (Stage 12)

**Date checked:** 2026-11-25  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)` and browser-compatible `Mozilla/5.0 (compatible; PolicyDeskAU/1.0; +https://policydesk.au) …`  
**Intended use:** automated fetch of current ACT Legislative Assembly member facts (name, multi-member electorate, party, official profile URL). No photos. No biographies. No office addresses or emails.

## 1. robots.txt — www.parliament.act.gov.au

**URL:** https://www.parliament.act.gov.au/robots.txt  

Fetched 2026-11-25 via a real browser after Cloudflare blocked plain `curl` (HTTP 403 challenge HTML).

**Full robots body as fetched:**

```
# www.robotstxt.org/

# http://code.google.com/web/controlcrawlindex/



User-agent: *
Crawl-delay: 20
Disallow: /search
Disallow: /designs
Disallow: /*?sq_content_src=
Disallow: /*_recache
Disallow: /*_edit
Disallow: /*_admin
Disallow: /*_login
Disallow: /*_performance
Disallow: /_performance
Disallow: /_designs/
Disallow: /*_design
Disallow: /*_web_services
Disallow: /__lib
Disallow: /__fudge

User-Agent: Funnelback
Crawl-delay: 0

# Prevent crawling of Funnelback search queries or facets.
Disallow: *?*query=
Disallow: *?*f.*%7C*=
```

### `urllib.robotparser` (body above)

```
can_fetch('PolicyDeskAU', '/members/current') = True
can_fetch('PolicyDeskAU', '/members/current/barr') = True
crawl_delay('PolicyDeskAU') = 20
```

**Production fetch note:** robots.txt does **not** Disallow member list or profile paths for `PolicyDeskAU` (20 s crawl-delay). Cloudflare still blocked unattended fetches with that User-Agent on this check date. Stage 12 member data was built from a browser-cleared save of `/members/current` (`--from-html`). The fetch script tries live URLs and exits with a clear error if Cloudflare blocks.

## 2. Copyright / terms — ACT Legislative Assembly

**Page checked:** https://www.parliament.act.gov.au/functions/footer/reuse-policy (“Reusing our content”) — HTTP 200 (browser).

Quoted from that page:

> Except where otherwise noted, all content on the websites: parliament.act.gov.au … is provided under the Creative Commons Attribution-Non-Commercial-NoDerivatives 4.0 International License (CC BY-NC-ND 4.0). This lets you copy and share unaltered content for non-commercial purposes so long as you attribute it to the ACT Legislative Assembly.

> Members’ official portraits: These remain copyright of the ACT Legislative Assembly. They cannot be used for political or commercial purposes. Requests for use must be sent to ola@parliament.act.gov.au.

## 3. Official member list used

| What | Result on 2026-11-25 |
|------|----------------------|
| Current members table | `https://www.parliament.act.gov.au/members/current` — 25 of 25 |
| Official profile URL pattern | `https://www.parliament.act.gov.au/members/current/{slug}` |
| Party + seat | Affiliation and Electorate columns on the current-members table |
| Expected counts | 25 MLAs; 5 multi-member electorates × 5 members |

Party labels from the Affiliation column are stored as full names: Labor → Australian Labor Party; Liberal / Liberals → Liberal Party; Green → ACT Greens; Independent. Emerson’s affiliation cell HTML splits the word Independent (`⬤ I</span>ndependent`); the fetch script normalises that glitch before mapping.

Facts stored per member: display name (list link text without role lines or post-nominals such as CSC), chamber Assembly, electorate, party, official profile URL, source. Unknown fields = null. **Addresses, emails, phones and biographies are not stored. Parliament portraits are not copied.**

## 4. Verdicts (evidence only — no legal inference)

**(a) robots.txt:** does **not** Disallow our `PolicyDeskAU` agent for member list/profile paths; crawl-delay 20.  
**(b) automated access:** Cloudflare blocked unattended fetches for our UA on this date.  
**(c) reusing member names, parties and seats (facts only):** website content is CC BY-NC-ND 4.0; portraits are excluded. Same class of Stage 15 NC/ND vs CC BY-SA / monetisation uncertainty as Federal and QLD website text. We store facts only, attribute ACT Legislative Assembly, and **do not** copy addresses, biographies, or portraits into the repo.

---

# Data sources — ACT electoral boundaries (Stage 12)

**Date checked:** 2026-11-25  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Intended use:** download ACT Legislative Assembly multi-member electorate boundaries for the map; simplify; publish as static SVG-path JSON.

## Dataset

| | Geoscape Administrative Boundaries — ACT State Electoral Boundaries |
|---|---|
| Title | ACT State Electoral Boundaries — Geoscape Administrative Boundaries |
| Publisher | Geoscape Australia / Commonwealth of Australia (data.gov.au) |
| Landing page | https://data.gov.au/data/dataset/act-state-electoral-boundaries-geoscape-administrative-boundaries |
| Download used | https://data.gov.au/data/dataset/2ca66004-3669-46f8-8ffc-14e1a05ea170/resource/39eaad81-c5f6-45c5-880f-400e3af0a4d6/download/act_seb_gda2020.zip (NOV26 GDA2020 ESRI) |
| Status | 5 Legislative Assembly electorates with `SECL_CODE=2` and `EFF_START=20241019` (2023 redistribution; in force from the 2024 ACT election). Older `EFF_END=20241018` rows are **not** used. Names matched to the Parliament current-members table. |

## Licence

**Creative Commons Attribution 4.0 International (CC BY 4.0)** on the data.gov.au dataset page.

Preferred attribution for Adapted Material (quote pattern from Geoscape Administrative Boundaries):

> Incorporates or developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0).

## robots.txt — data.gov.au

Same host pattern as Stages 7–11: `User-agent: *` / `Disallow: /` in robots.txt; the ACT zip download still returned **HTTP 200** with User-Agent `PolicyDeskAU/1.0` on this date. Dataset page continues to publish the boundaries under CC BY 4.0.

## Attribution (our wording)

> This product (The Policy Desk AU map) incorporates or was developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0). Simplified by The Policy Desk AU. Australian Capital Territory Legislative Assembly multi-member electorates from the NOV26 GDA2020 Geoscape release (Elections ACT 2023 redistribution; EFF_START 2024-10-19).

---

# Data sources — Northern Territory Legislative Assembly (Stage 13)

**Date checked:** 2026-11-25  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)` and a real Chrome browser after Cloudflare.  
**Intended use:** automated fetch of current NT Legislative Assembly member facts (name, single-member division, party, official profile URL). No photos. No biographies. No office addresses or emails.

## 1. robots.txt — parliament.nt.gov.au

**URL:** https://parliament.nt.gov.au/robots.txt  

Plain `curl` with `PolicyDeskAU/1.0` received **HTTP 403** (Cloudflare “Just a moment…” challenge HTML) for `/robots.txt` and member pages on this check date. The rules below were read in Chrome after the challenge cleared. The saved body is 176 bytes.

**Full robots body as fetched:**

```
User-agent: *
Disallow: /?sq_content_src=
Disallow: /_recache
Disallow: /_edit
Disallow: /_admin
Disallow: /_login
Disallow: /_performance
Disallow: /_designs
Disallow: /search
```

### `urllib.robotparser` (body above)

```
can_fetch('PolicyDeskAU', '/members') = True
can_fetch('PolicyDeskAU', '/members/by-name') = True
can_fetch('PolicyDeskAU', '/members/by-name/lia-finocchiaro') = True
can_fetch('PolicyDeskAU', '/disclaimer') = True
can_fetch('PolicyDeskAU', '/search') = False
crawl_delay('PolicyDeskAU') = None
```

**Production fetch note:** robots.txt does **not** Disallow the member list or profile paths for `PolicyDeskAU`. Cloudflare still blocked unattended fetches with that User-Agent on this check date. Stage 13 member data was built from a browser-cleared save (`--from-dir`: `by-name.html` plus `profiles/{slug}.html`). The fetch script tries live URLs and exits with a clear error if Cloudflare blocks.

## 2. Copyright / terms — Legislative Assembly of the Northern Territory

Pages probed and not found (the site’s own “Page Not Found”): `/copyright`, `/privacy`, `/terms`, `/legal`.

The footer link “Copyright, Disclaimer and Privacy” goes to https://parliament.nt.gov.au/disclaimer (last updated 18 May 2017). That is the only copyright/terms page found. The sitemap lists no other legal page.

Quoted from https://parliament.nt.gov.au/disclaimer :

> Copyright in the material which appears on this website is subject to the Copyright Act 1968 (Cth) ("the Act").

> No part of this website may be reproduced or reused for any purpose whatsoever, apart from:

> fair dealing for the purposes of private study, research, criticism or review, as permitted under the Act

> or where expressly provided otherwise.

> Where specific licence terms are applied to any materials on this website, those terms prevail to the extent of any inconsistency with this statement, and end users wishing to rely upon such licence must comply with those terms in all respects.

**Creative Commons:** not mentioned on this page.  
**Commercial use:** not mentioned beyond the reuse sentence above.  
**Automated access / scraping / bots:** not mentioned on this page. The only automated-access rules found are the robots.txt Disallow lines above.

## 3. Official member list used

| What | Result on 2026-11-25 |
|------|----------------------|
| Intro page | `https://parliament.nt.gov.au/members` — “There are 25 Members of the Legislative Assembly, each representing a single electoral division.” Last updated 10 Sep 2024. The member-card container in the served HTML is empty, so names are not taken from this page. |
| Current member list | `https://parliament.nt.gov.au/members/by-name` — 25 profile links. “Members of the 15th Assembly were elected at the General Election on 24 August 2024.” Last updated 21 Jul 2026. |
| Official profile URL | `https://parliament.nt.gov.au/members/by-name/{slug}` (slugs kept as published, including `Ed-Smelt` and `Dheran-Young`) |
| Party + division | Electorate and Party cells on each profile. Not taken from the by-name page, which lists names only. |
| Expected counts | 25 members; 25 divisions; one member each. No vacancy on the current list. |

Party cells are stored as printed: Country Liberal Party (17), Territory Labor (6), Independent (2). The page does not print a party abbreviation. Display names drop a leading “Hon” and a trailing “OAM”. The by-name link for Karama uses a curly apostrophe in O’Gallagher; the stored name uses a straight apostrophe, the same form as other O'Brien records.

Facts stored per member: display name, chamber Assembly, division, party, official profile URL, source. Unknown fields = null. **Addresses, emails, phones, ministries and biographies are not stored. Parliament portraits are not copied.**

## 4. Verdicts (evidence only — no legal inference)

**(a) robots.txt:** does **not** Disallow our `PolicyDeskAU` agent for `/members`, `/members/by-name`, or profile paths. `/search` is Disallow.  
**(b) automated access:** Cloudflare blocked unattended fetches for our UA on this date. The disclaimer page does not mention bots.  
**(c) reusing member names, parties and divisions (facts only):** the disclaimer says no part of the website may be reproduced or reused apart from fair dealing under the Copyright Act, or where expressly provided otherwise. It does **not** say whether a name, party and division on their own are “material” under that sentence. Same class of Stage 15 uncertainty as Victoria. We store facts only, attribute the Legislative Assembly of the Northern Territory, and **do not** copy addresses, biographies, or portraits into the repo.

---

# Data sources — Northern Territory electoral boundaries (Stage 13)

**Date checked:** 2026-11-25  
**Checker User-Agent:** `PolicyDeskAU/1.0 (https://policydesk.au)`  
**Intended use:** download Northern Territory Legislative Assembly division boundaries for the map; simplify; publish as static SVG-path JSON. Keep only divisions named on the current official member list.

## Dataset

| | Geoscape Administrative Boundaries — NT State Electoral Boundaries |
|---|---|
| Title | NT State Electoral Boundaries — Geoscape Administrative Boundaries |
| Publisher | Geoscape Australia / Commonwealth of Australia (data.gov.au) |
| Landing page | https://data.gov.au/data/dataset/nt-state-electoral-boundaries-geoscape-administrative-boundaries |
| Download used | https://data.gov.au/data/dataset/19c0bd08-d8c7-42c8-953e-d9d1969f116b/resource/bedb117b-ea60-4842-b428-71d9fc827a29/download/nt_seb_gda2020.zip (NOV26 GDA2020 ESRI) |
| Catalogue licence | CKAN `license_id` `cc-by-4.0`, `license_title` Creative Commons Attribution 4.0 International |
| Status | 25 current divisions with `SECL_CODE=2` and `EFF_START=20240824` (empty `EFF_END`). The earlier 25 rows with `EFF_END=20240823` (including Nhulunbuy and Stuart, replaced by Mulka and Gwoja) are **not** used. Names matched to the Assembly profile Electorate cells. |

## Licence

**Creative Commons Attribution 4.0 International (CC BY 4.0)** on the data.gov.au dataset record.

Preferred attribution for Adapted Material (quote pattern from Geoscape Administrative Boundaries):

> Incorporates or developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0).

## robots.txt — data.gov.au

Fetched 2026-11-25 with User-Agent `PolicyDeskAU/1.0` (HTTP 200). Relevant lines:

```
User-agent: *
Disallow: /
Allow: /data/api/
```

The NT zip path is under `/data/dataset/…/download/`, which the `Disallow: /` line covers, and it is not under `/data/api/`. The same request still returned **HTTP 200** `application/zip` (656311 bytes). The dataset record publishes the boundaries under CC BY 4.0. Same reuse pattern as Stages 7–12.

## Attribution (our wording)

> This product (The Policy Desk AU map) incorporates or was developed using Administrative Boundaries © Geoscape Australia licensed by the Commonwealth of Australia under Creative Commons Attribution 4.0 International licence (CC BY 4.0). Simplified by The Policy Desk AU. Northern Territory Legislative Assembly divisions from the NOV26 GDA2020 Geoscape release (EFF_START 2024-08-24, in force for the 2024 election).

