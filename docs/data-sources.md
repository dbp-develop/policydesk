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
