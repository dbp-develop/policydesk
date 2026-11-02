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
