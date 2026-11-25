/* The Policy Desk AU: member list and map views. Vanilla JS, no build step. AGPL-3.0. */
(function () {
  "use strict";

  function httpsUrl(url) {
    return typeof url === "string" && /^https:\/\//.test(url);
  }

  var loadGeneration = 0;

  var PARLIAMENTS = {
    vic: {
      label: "Victoria",
      title: "Members of the Parliament of Victoria",
      lede: "Find your state MP. Search by name, party, chamber, electorate or region.",
      electionNote: "The Victorian state election is on 28 November 2026. This list shows members before the election and will be updated once results are official.",
      membersUrl: "data/members.json",
      sourceDefault: "Parliament of Victoria",
      sourceHref: "https://www.parliament.vic.gov.au/members/",
      profileSr: " on the Parliament of Victoria website",
      chamber: { lower: "Legislative Assembly", upper: "Legislative Council" },
      vacancyChamber: { Assembly: "lower", Council: "upper", lower: "lower", upper: "upper" },
      layers: { lower: "districts", upper: "regions" },
      boundaryFiles: { districts: "data/boundaries/vic_districts.json", regions: "data/boundaries/vic_regions.json" },
      seatLabel: { lower: " District", upper: " Region" },
      zoomExtent: "Whole state",
      zoomMetro: "Melbourne",
      showMetro: true,
      mapLower: "Showing the 88 Legislative Assembly districts.",
      mapUpper: "Showing the 8 Legislative Council regions. Each region elects 5 members.",
      mapOtherHint: " Choose Legislative Council under Chamber to see regions.",
      seatFilterLabel: "Electorate or region",
      seatAllLabel: "All electorates and regions",
      mapDesc: "Map of Victorian electoral boundaries. Use the text list of seats below to choose a seat with a keyboard or screen reader.",
      footerFactsHtml: 'Member facts: <a href="https://www.parliament.vic.gov.au/members/">Parliament of Victoria</a>. This site is independent and not affiliated with any parliament or party.',
      footerBoundariesHtml: 'Electoral boundaries: Victorian Electoral Commission via DataVic, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, simplified by us.'
    },
    federal: {
      label: "Federal",
      title: "Members of the Australian Parliament",
      lede: "Find your federal MP or Senator. Search by name, party, chamber, division or state.",
      electionNote: "House of Representatives and Senate. Official websites link to each member’s Parliamentary Handbook profile.",
      membersUrl: "data/federal/members.json",
      sourceDefault: "Parliament of Australia (Parliamentary Handbook)",
      sourceHref: "https://handbook.aph.gov.au/",
      profileSr: " on the Parliament of Australia website",
      chamber: { lower: "House of Representatives", upper: "Senate" },
      vacancyChamber: { House: "lower", Senate: "upper", lower: "lower", upper: "upper" },
      layers: { lower: "divisions", upper: "states" },
      boundaryFiles: { divisions: "data/boundaries/federal_divisions.json", states: "data/boundaries/federal_states.json" },
      seatLabel: { lower: " Division", upper: "" },
      zoomExtent: "Whole country",
      zoomMetro: "South-east",
      showMetro: true,
      mapLower: "Showing the 150 House of Representatives divisions.",
      mapUpper: "Showing the 8 states and territories. Senators are elected for each state or territory.",
      mapOtherHint: " Choose Senate under Chamber to see states and territories.",
      seatFilterLabel: "Division or state",
      seatAllLabel: "All divisions and states",
      mapDesc: "Map of Australian federal electoral boundaries. Use the text list of seats below to choose a seat with a keyboard or screen reader.",
      footerFactsHtml: 'Member facts: <a href="https://handbook.aph.gov.au/">Parliament of Australia (Parliamentary Handbook)</a>. This site is independent and not affiliated with any parliament or party.',
      footerBoundariesHtml: 'Electoral boundaries: Australian Electoral Commission under the <a href="https://www.aec.gov.au/Electorates/gis/licence.htm">AEC data download licence</a>, simplified by us.'
    },
    nsw: {
      label: "New South Wales",
      title: "Members of the Parliament of New South Wales",
      lede: "Find your NSW MP or MLC. Search by name, party, chamber or electorate.",
      electionNote: "Legislative Assembly and Legislative Council. Official websites link to each member’s Parliament of NSW profile.",
      membersUrl: "data/nsw/members.json",
      sourceDefault: "Parliament of New South Wales",
      sourceHref: "https://www.parliament.nsw.gov.au/members-and-electorates/members-and-ministers/downloadable-lists",
      profileSr: " on the Parliament of New South Wales website",
      chamber: { lower: "Legislative Assembly", upper: "Legislative Council" },
      vacancyChamber: { Assembly: "lower", Council: "upper", lower: "lower", upper: "upper" },
      layers: { lower: "districts", upper: "state" },
      boundaryFiles: { districts: "data/boundaries/nsw_districts.json", state: "data/boundaries/nsw_state.json" },
      seatLabel: { lower: " District", upper: "" },
      zoomExtent: "Whole state",
      zoomMetro: "Sydney",
      showMetro: true,
      mapLower: "Showing the 93 Legislative Assembly districts.",
      mapUpper: "Showing New South Wales as one area. Legislative Council members are elected statewide.",
      mapOtherHint: " Choose Legislative Council under Chamber to see the statewide map.",
      seatFilterLabel: "Electorate or state",
      seatAllLabel: "All electorates",
      mapDesc: "Map of New South Wales electoral boundaries. Use the text list of seats below to choose a seat with a keyboard or screen reader.",
      footerFactsHtml: 'Member facts: <a href="https://www.parliament.nsw.gov.au/members-and-electorates/members-and-ministers/downloadable-lists">Parliament of New South Wales</a>. This site is independent and not affiliated with any parliament or party.',
      footerBoundariesHtml: 'Electoral boundaries: Administrative Boundaries © Geoscape Australia, Commonwealth of Australia, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, simplified by us.'
    },
    qld: {
      label: "Queensland",
      title: "Members of the Parliament of Queensland",
      lede: "Find your Queensland MP. Search by name, party or electorate.",
      electionNote: "Queensland’s Parliament is unicameral — Legislative Assembly only. Official websites link to each member’s Parliament of Queensland profile.",
      membersUrl: "data/qld/members.json",
      sourceDefault: "Parliament of Queensland",
      sourceHref: "https://www.parliament.qld.gov.au/Members/Current-Members/Member-List",
      profileSr: " on the Parliament of Queensland website",
      chamber: { lower: "Legislative Assembly", upper: "Legislative Assembly" },
      vacancyChamber: { Assembly: "lower", lower: "lower" },
      layers: { lower: "districts" },
      boundaryFiles: { districts: "data/boundaries/qld_districts.json" },
      seatLabel: { lower: " District", upper: " District" },
      zoomExtent: "Whole state",
      zoomMetro: "Brisbane",
      showMetro: true,
      unicameral: true,
      mapLower: "Showing the 93 Legislative Assembly districts.",
      mapUpper: "",
      mapOtherHint: "",
      seatFilterLabel: "Electorate",
      seatAllLabel: "All electorates",
      mapDesc: "Map of Queensland electoral districts. Use the text list of seats below to choose a seat with a keyboard or screen reader.",
      footerFactsHtml: 'Member facts: <a href="https://www.parliament.qld.gov.au/Members/Current-Members/Member-List">Parliament of Queensland</a>. This site is independent and not affiliated with any parliament or party.',
      footerBoundariesHtml: 'Electoral boundaries: Administrative Boundaries © Geoscape Australia, Commonwealth of Australia, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, simplified by us.'
    },
    wa: {
      label: "Western Australia",
      title: "Members of the Parliament of Western Australia",
      lede: "Find your WA MP or MLC. Search by name, party, chamber or electorate.",
      electionNote: "Legislative Assembly and Legislative Council. Official websites link to each member’s Parliament of Western Australia profile. Council members are elected statewide.",
      membersUrl: "data/wa/members.json",
      sourceDefault: "Parliament of Western Australia",
      sourceHref: "https://www.parliament.wa.gov.au/parliament/memblist.nsf/WAMembers",
      profileSr: " on the Parliament of Western Australia website",
      chamber: { lower: "Legislative Assembly", upper: "Legislative Council" },
      vacancyChamber: { Assembly: "lower", Council: "upper", lower: "lower", upper: "upper" },
      layers: { lower: "districts", upper: "state" },
      boundaryFiles: { districts: "data/boundaries/wa_districts.json", state: "data/boundaries/wa_state.json" },
      seatLabel: { lower: " District", upper: "" },
      zoomExtent: "Whole state",
      zoomMetro: "Perth",
      showMetro: true,
      mapLower: "Showing the 59 Legislative Assembly districts.",
      mapUpper: "Showing Western Australia as one area. Legislative Council members are elected statewide.",
      mapOtherHint: " Choose Legislative Council under Chamber to see the statewide map.",
      seatFilterLabel: "Electorate or state",
      seatAllLabel: "All electorates",
      mapDesc: "Map of Western Australian electoral boundaries. Use the text list of seats below to choose a seat with a keyboard or screen reader.",
      footerFactsHtml: 'Member facts: <a href="https://www.parliament.wa.gov.au/parliament/memblist.nsf/WAMembers">Parliament of Western Australia</a>. This site is independent and not affiliated with any parliament or party.',
      footerBoundariesHtml: 'Electoral boundaries: Administrative Boundaries © Geoscape Australia, Commonwealth of Australia, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, simplified by us.'
    },
    sa: {
      label: "South Australia",
      title: "Members of the Parliament of South Australia",
      lede: "Find your SA MP or MLC. Search by name, party, chamber or electorate.",
      electionNote: "House of Assembly and Legislative Council. Official websites link to each member’s Parliament of South Australia profile. Council members are elected statewide.",
      membersUrl: "data/sa/members.json",
      sourceDefault: "Parliament of South Australia",
      sourceHref: "https://www.parliament.sa.gov.au/en/Members/Members-Home",
      profileSr: " on the Parliament of South Australia website",
      chamber: { lower: "House of Assembly", upper: "Legislative Council" },
      vacancyChamber: { Assembly: "lower", Council: "upper", lower: "lower", upper: "upper" },
      layers: { lower: "districts", upper: "state" },
      boundaryFiles: { districts: "data/boundaries/sa_districts.json", state: "data/boundaries/sa_state.json" },
      seatLabel: { lower: " District", upper: "" },
      zoomExtent: "Whole state",
      zoomMetro: "Adelaide",
      showMetro: true,
      mapLower: "Showing the 47 House of Assembly districts.",
      mapUpper: "Showing South Australia as one area. Legislative Council members are elected statewide.",
      mapOtherHint: " Choose Legislative Council under Chamber to see the statewide map.",
      seatFilterLabel: "Electorate or state",
      seatAllLabel: "All electorates",
      mapDesc: "Map of South Australian electoral boundaries. Use the text list of seats below to choose a seat with a keyboard or screen reader.",
      footerFactsHtml: 'Member facts: <a href="https://www.parliament.sa.gov.au/en/Members/Members-Home">Parliament of South Australia</a>. This site is independent and not affiliated with any parliament or party.',
      footerBoundariesHtml: 'Electoral boundaries: Administrative Boundaries © Geoscape Australia, Commonwealth of Australia, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, simplified by us.'
    },
    tas: {
      label: "Tasmania",
      title: "Members of the Parliament of Tasmania",
      lede: "Find your Tasmanian MP or MLC. Search by name, party, chamber or division.",
      electionNote: "House of Assembly and Legislative Council. Official websites link to each member’s Parliament of Tasmania profile. Assembly divisions elect 7 members each.",
      membersUrl: "data/tas/members.json",
      sourceDefault: "Parliament of Tasmania",
      sourceHref: "https://www.parliament.tas.gov.au/house-of-assembly/currentmembers",
      profileSr: " on the Parliament of Tasmania website",
      chamber: { lower: "House of Assembly", upper: "Legislative Council" },
      vacancyChamber: { Assembly: "lower", Council: "upper", lower: "lower", upper: "upper" },
      layers: { lower: "districts", upper: "council" },
      boundaryFiles: { districts: "data/boundaries/tas_districts.json", council: "data/boundaries/tas_council.json" },
      seatLabel: { lower: " Division", upper: " Division" },
      zoomExtent: "Whole state",
      zoomMetro: "Hobart",
      showMetro: true,
      mapLower: "Showing the 5 House of Assembly divisions. Each division elects 7 members.",
      mapUpper: "Showing the 15 Legislative Council divisions.",
      mapOtherHint: " Choose Legislative Council under Chamber to see Council divisions.",
      seatFilterLabel: "Division",
      seatAllLabel: "All divisions",
      mapDesc: "Map of Tasmanian electoral boundaries. Use the text list of seats below to choose a seat with a keyboard or screen reader.",
      footerFactsHtml: 'Member facts: <a href="https://www.parliament.tas.gov.au/house-of-assembly/currentmembers">Parliament of Tasmania</a>. This site is independent and not affiliated with any parliament or party.',
      footerBoundariesHtml: 'Electoral boundaries: Administrative Boundaries © Geoscape Australia, Commonwealth of Australia, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, simplified by us.'
    },
    act: {
      label: "Australian Capital Territory",
      title: "Members of the ACT Legislative Assembly",
      lede: "Find your ACT MLA. Search by name, party or electorate.",
      electionNote: "The ACT Legislative Assembly is unicameral. Each electorate elects 5 members. Official websites link to each member’s ACT Legislative Assembly profile.",
      membersUrl: "data/act/members.json",
      sourceDefault: "ACT Legislative Assembly",
      sourceHref: "https://www.parliament.act.gov.au/members/current",
      profileSr: " on the ACT Legislative Assembly website",
      chamber: { lower: "Legislative Assembly", upper: "Legislative Assembly" },
      vacancyChamber: { Assembly: "lower", lower: "lower" },
      layers: { lower: "districts" },
      boundaryFiles: { districts: "data/boundaries/act_districts.json" },
      seatLabel: { lower: " Electorate", upper: " Electorate" },
      zoomExtent: "Whole territory",
      zoomMetro: "Canberra",
      showMetro: true,
      unicameral: true,
      mapLower: "Showing the 5 Legislative Assembly electorates. Each electorate elects 5 members.",
      mapUpper: "",
      mapOtherHint: "",
      seatFilterLabel: "Electorate",
      seatAllLabel: "All electorates",
      mapDesc: "Map of ACT Legislative Assembly electorates. Use the text list of seats below to choose a seat with a keyboard or screen reader.",
      footerFactsHtml: 'Member facts: <a href="https://www.parliament.act.gov.au/members/current">ACT Legislative Assembly</a>. This site is independent and not affiliated with any parliament or party.',
      footerBoundariesHtml: 'Electoral boundaries: Administrative Boundaries © Geoscape Australia, Commonwealth of Australia, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, simplified by us.'
    },
    nt: {
      label: "Northern Territory",
      title: "Members of the Northern Territory Legislative Assembly",
      lede: "Find your NT MLA. Search by name, party or division.",
      electionNote: "The Northern Territory Legislative Assembly is unicameral. Each division elects one member. Official websites link to each member’s parliament.nt.gov.au profile.",
      membersUrl: "data/nt/members.json",
      sourceDefault: "Legislative Assembly of the Northern Territory",
      sourceHref: "https://parliament.nt.gov.au/members/by-name",
      profileSr: " on the Northern Territory Legislative Assembly website",
      chamber: { lower: "Legislative Assembly", upper: "Legislative Assembly" },
      vacancyChamber: { Assembly: "lower", lower: "lower" },
      layers: { lower: "districts" },
      boundaryFiles: { districts: "data/boundaries/nt_districts.json" },
      seatLabel: { lower: " Division", upper: " Division" },
      zoomExtent: "Whole territory",
      zoomMetro: "Darwin",
      showMetro: true,
      unicameral: true,
      mapLower: "Showing the 25 Legislative Assembly divisions. Each division elects one member.",
      mapUpper: "",
      mapOtherHint: "",
      seatFilterLabel: "Division",
      seatAllLabel: "All divisions",
      mapDesc: "Map of Northern Territory Legislative Assembly divisions. Use the text list of seats below to choose a seat with a keyboard or screen reader.",
      footerFactsHtml: 'Member facts: <a href="https://parliament.nt.gov.au/members/by-name">Northern Territory Legislative Assembly</a>. This site is independent and not affiliated with any parliament or party.',
      footerBoundariesHtml: 'Electoral boundaries: Administrative Boundaries © Geoscape Australia, Commonwealth of Australia, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, simplified by us.'
    }
  };

  var els = {
    form: document.getElementById("filters"),
    parliament: document.getElementById("parliament"),
    q: document.getElementById("q"),
    chamber: document.getElementById("chamber"),
    chamberLowerOpt: document.getElementById("chamber-lower-opt"),
    chamberUpperOpt: document.getElementById("chamber-upper-opt"),
    party: document.getElementById("party"),
    seat: document.getElementById("seat"),
    list: document.getElementById("list"),
    count: document.getElementById("count"),
    dataLine: document.getElementById("data-line"),
    electionNote: document.getElementById("election-note"),
    pageTitle: document.getElementById("page-title"),
    pageLede: document.getElementById("page-lede"),
    results: document.getElementById("results"),
    skip: document.querySelector(".skip-link"),
    viewList: document.getElementById("view-list"),
    viewMap: document.getElementById("view-map"),
    mapView: document.getElementById("map-view"),
    map: document.getElementById("map"),
    mapStatus: document.getElementById("map-status"),
    mapLayer: document.getElementById("map-layer"),
    mapDetail: document.getElementById("map-detail"),
    seatButtons: document.getElementById("seat-buttons"),
    seatCount: document.getElementById("seat-count"),
    mapCredit: document.getElementById("map-credit"),
    zoomAustralia: document.getElementById("zoom-australia"),
    zoomExtent: document.getElementById("zoom-extent"),
    zoomMetro: document.getElementById("zoom-metro"),
    footerFacts: document.getElementById("footer-facts"),
    footerBoundaries: document.getElementById("footer-boundaries"),
    seatLabel: document.getElementById("seat-label"),
    seatAllOpt: document.getElementById("seat-all-opt"),
    seatListLabel: document.getElementById("seat-list-label"),
    mapDesc: document.getElementById("map-desc"),
    mapHint: document.getElementById("map-hint")
  };
  var SVG_NS = "http://www.w3.org/2000/svg";
  var METRO = /Metropolitan$/;
  /* National overview reuses AEC state/territory shapes (federal_states.json). */
  var OVERVIEW_URL = "data/boundaries/federal_states.json";
  var OVERVIEW_DESC = "Map of Australia. Choose a jurisdiction from the text list below, or tap a live state, to open its electoral boundaries. Keyboard and screen reader users should use the text list.";
  var OVERVIEW_HINT = "On the Australia view, tap a live state or territory (Victoria, New South Wales, Queensland, Western Australia, South Australia, Tasmania, Australian Capital Territory or Northern Territory) or choose Federal from the list. Zoom with + and −, by pinching, or by holding Ctrl and scrolling. Once zoomed in, drag to move the map.";
  var DETAIL_HINT = "Zoom with + and −, by pinching, or by holding Ctrl and scrolling. Once zoomed in, drag to move the map. Use Australia to return to the national map.";
  var STATE_TO_PARLIAMENT = {
    "Victoria": "vic",
    "New South Wales": "nsw",
    "Queensland": "qld",
    "Western Australia": "wa",
    "South Australia": "sa",
    "Tasmania": "tas",
    "Australian Capital Territory": "act",
    "Northern Territory": "nt"
  };
  var OVERVIEW_LIVE = [
    { key: "federal", label: "Federal (House + Senate)" },
    { key: "vic", label: "Victoria" },
    { key: "nsw", label: "New South Wales" },
    { key: "qld", label: "Queensland" },
    { key: "wa", label: "Western Australia" },
    { key: "sa", label: "South Australia" },
    { key: "tas", label: "Tasmania" },
    { key: "act", label: "Australian Capital Territory" },
    { key: "nt", label: "Northern Territory" }
  ];

  var collator = new Intl.Collator("en-AU", { sensitivity: "base" });
  var parliamentKey = "vic";
  var cfg = PARLIAMENTS.vic;
  var rows = [];
  var newsIndex = null;   // data/news/index.json, loaded in the background
  var lastListKey = null;
  var photos = {};        // data/photos.json: id -> {local_path, creator, licence, licence_url, commons_url}
  var socials = {};       // data/socials.json: owner-approved links only
  var extrasVersion = 0;  // bumps when photos/socials load, so cards re-render

  function chamberLabel(key) { return cfg.chamber[key]; }

  function seatOf(m) { return m.chamber === "lower" ? m.electorate : m.region; }

  function initials(name) {
    var parts = name.split(/\s+/).filter(Boolean);
    var first = parts[0] ? parts[0][0] : "";
    var last = parts.length > 1 ? parts[parts.length - 1][0] : "";
    return (first + last).toUpperCase();
  }

  function formatDate(iso) {
    var d = new Date(iso + "T00:00:00");
    if (isNaN(d)) return iso;
    return d.toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" });
  }

  function norm(s) {
    return (s || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function addOptions(select, values) {
    values.forEach(function (v) {
      var o = document.createElement("option");
      o.value = v;
      o.textContent = v;
      select.appendChild(o);
    });
  }

  function buildFilters() {
    while (els.party.options.length > 1) els.party.remove(1);
    while (els.seat.options.length > 1) els.seat.remove(1);
    els.seat.querySelectorAll("optgroup").forEach(function (g) { g.remove(); });

    var parties = {};
    var seats = { lower: {}, upper: {} };
    rows.forEach(function (r) {
      if (r.party) parties[r.party] = true;
      if (r.seat) seats[r.chamber][r.seat] = true;
    });
    addOptions(els.party, Object.keys(parties).sort(collator.compare));

    if (cfg.unicameral) {
      // One chamber only — flat options, no empty duplicate optgroup.
      addOptions(els.seat, Object.keys(seats.lower).sort(collator.compare));
    } else {
      ["lower", "upper"].forEach(function (c) {
        var names = Object.keys(seats[c]).sort(collator.compare);
        if (!names.length) return;
        var group = document.createElement("optgroup");
        group.label = chamberLabel(c);
        addOptions(group, names);
        els.seat.appendChild(group);
      });
    }
  }

  function syncSeatGroups() {
    var chamber = els.chamber.value;
    var groups = els.seat.querySelectorAll("optgroup");
    groups.forEach(function (g, i) {
      var key = i === 0 ? "lower" : "upper";
      g.hidden = !!chamber && chamber !== key;
      g.disabled = g.hidden;
    });
    var opt = els.seat.selectedOptions[0];
    if (opt && opt.parentNode.tagName === "OPTGROUP" && opt.parentNode.disabled) {
      els.seat.value = "";
    }
  }

  function card(r) {
    var li = el("li", r.vacant ? "card card-vacant" : "card");
    var main = el("div", "card-main");
    var photo = !r.vacant && photos[r.id];
    if (photo && /^images\/members\/[\w.-]+$/.test(photo.local_path)) {
      var img = document.createElement("img");
      img.className = "avatar avatar-photo";
      img.src = photo.local_path;
      img.alt = "";  // the name is the heading right next to it
      img.width = 48; img.height = 48;
      img.loading = "lazy";
      main.appendChild(img);
    } else {
      var avatar = el("span", "avatar", r.vacant ? "–" : initials(r.name));
      avatar.setAttribute("aria-hidden", "true");
      main.appendChild(avatar);
    }

    var body = el("div", "card-body");
    body.appendChild(el("h2", null, r.vacant ? "Vacant seat" : r.name));
    if (!r.vacant) body.appendChild(el("p", "party", r.party));
    body.appendChild(el("p", "meta", r.seat + " · " + chamberLabel(r.chamber)));
    if (r.vacant) body.appendChild(el("p", "meta", "Vacancy recorded by The Policy Desk AU; official source not yet linked."));

    var links = el("div", "card-links");
    if (httpsUrl(r.url)) {
      var a = el("a", "profile", "Official website");
      a.href = r.url;
      a.appendChild(el("span", "visually-hidden", " for " + r.name + cfg.profileSr));
      links.appendChild(a);
    }
    var soc = !r.vacant && socials[r.id];
    if (soc && soc.links) {
      [["x", "X"], ["facebook", "Facebook"], ["instagram", "Instagram"]].forEach(function (k) {
        var u = soc.links[k[0]];
        if (httpsUrl(u)) {
          var sa = el("a", null, k[1]);
          sa.href = u;
          sa.appendChild(el("span", "visually-hidden", " (" + r.name + ")"));
          links.appendChild(sa);
        }
      });
    }
    if (links.childElementCount) body.appendChild(links);
    main.appendChild(body);
    li.appendChild(main);

    if (photo) {
      var cr = el("p", "photo-credit");
      cr.appendChild(document.createTextNode("Photo (resized): " + photo.creator + ", "));
      if (httpsUrl(photo.licence_url)) {
        var la = el("a", null, photo.licence);
        la.href = photo.licence_url;
        cr.appendChild(la);
      } else {
        cr.appendChild(document.createTextNode(photo.licence));
      }
      cr.appendChild(document.createTextNode(", "));
      if (httpsUrl(photo.commons_url)) {
        var ca = el("a", null, "Wikimedia Commons");
        ca.href = photo.commons_url;
        ca.appendChild(el("span", "visually-hidden", " (photo of " + r.name + ")"));
        cr.appendChild(ca);
      } else {
        cr.appendChild(document.createTextNode("Wikimedia Commons"));
      }
      li.appendChild(cr);
    }
    var n = !r.vacant && newsIndex && newsIndex.counts ? newsIndex.counts[r.id] : 0;
    if (n > 0) {
      var nb = el("button", "news-btn", "Recent news (" + n + ")");
      nb.type = "button";
      nb.setAttribute("aria-haspopup", "dialog");
      nb.appendChild(el("span", "visually-hidden", " about " + r.name));
      nb.addEventListener("click", function () { openNews(r); });
      li.appendChild(nb);
    }
    return li;
  }

  /* ---------- News popup (pre-built static files, never fetched from publishers) ---------- */
  var newsDialog = document.getElementById("news-dialog");

  function openNews(r) {
    var list = document.getElementById("news-list");
    document.getElementById("news-title").textContent = "Recent news: " + r.name;
    list.replaceChildren(el("li", "news-status", "Loading…"));
    if (newsDialog.showModal) newsDialog.showModal(); else newsDialog.setAttribute("open", "");
    fetch("data/news/" + encodeURIComponent(r.id) + ".json", { cache: "no-cache" })
      .then(function (res) { if (!res.ok) throw new Error("HTTP " + res.status); return res.json(); })
      .then(function (doc) {
        list.replaceChildren();
        (doc.items || []).forEach(function (i) {
          if (!httpsUrl(i.url)) return;
          var li = el("li", "news-item");
          var a = el("a", "news-headline", i.title);
          a.href = i.url;
          li.appendChild(a);
          var meta = el("p", "news-meta");
          meta.appendChild(el("span", "news-source", i.source || ""));
          var when = formatDate(i.published);
          if (when) {
            meta.appendChild(document.createTextNode(" · "));
            var time = el("time", "news-date", when);
            if (i.published) time.setAttribute("datetime", i.published);
            meta.appendChild(time);
          }
          li.appendChild(meta);
          if (!i.verified) {
            li.appendChild(el("p", "news-flag", "Unverified match: the name is in the article text together with the member's electorate or region, not in the headline or summary."));
          }
          list.appendChild(li);
        });
        if (!list.children.length) list.appendChild(el("li", "news-status", "No recent news found."));
      })
      .catch(function () {
        list.replaceChildren(el("li", "news-status", "Sorry, news could not be loaded."));
      });
  }
  document.getElementById("news-close").addEventListener("click", function () {
    if (newsDialog.close) newsDialog.close(); else newsDialog.removeAttribute("open");
  });
  newsDialog.addEventListener("click", function (e) {
    if (e.target !== newsDialog || !newsDialog.close) return;
    var rect = newsDialog.getBoundingClientRect();
    var inside = e.clientX >= rect.left && e.clientX <= rect.right &&
      e.clientY >= rect.top && e.clientY <= rect.bottom;
    if (!inside) newsDialog.close();
  });

  function render() {
    syncSeatGroups();
    var q = norm(els.q.value.trim());
    var chamber = els.chamber.value;
    var party = els.party.value;
    var seat = els.seat.value;

    var shown = rows.filter(function (r) {
      if (chamber && r.chamber !== chamber) return false;
      if (party && r.party !== party) return false;
      if (seat && r.seat !== seat) return false;
      if (q && norm(r.name).indexOf(q) === -1 && norm(r.seat).indexOf(q) === -1) return false;
      return true;
    });

    // Only rebuild the cards when the result actually changed. A "change" event fires when
    // the search box loses focus; rebuilding then would swallow the tap on a card button.
    var listKey = [rows.length, extrasVersion, q, chamber, party, seat, newsIndex ? newsIndex.generated_at : ""].join("|");
    if (listKey !== lastListKey) {
      lastListKey = listKey;
      var frag = document.createDocumentFragment();
      shown.forEach(function (r) { frag.appendChild(card(r)); });
      els.list.replaceChildren(frag);
      if (!shown.length) {
        els.list.appendChild(el("li", "empty", "No members match these filters."));
      }
    }
    if (view === "map") renderMap(shown);
    var vacant = shown.filter(function (r) { return r.vacant; }).length;
    var text = "Showing " + (shown.length - vacant) + " of " +
      rows.filter(function (r) { return !r.vacant; }).length + " members";
    if (vacant) text += " and " + vacant + " vacant seat" + (vacant > 1 ? "s" : "");
    els.count.textContent = text + ".";
  }

  function applyParliamentChrome() {
    document.title = cfg.title.replace(/^Members of /, "") + " · The Policy Desk AU";
    if (els.pageTitle) els.pageTitle.textContent = cfg.title;
    if (els.pageLede) els.pageLede.textContent = cfg.lede;
    if (els.electionNote) els.electionNote.textContent = cfg.electionNote;
    if (els.chamberLowerOpt) els.chamberLowerOpt.textContent = chamberLabel("lower");
    if (els.chamberUpperOpt) {
      els.chamberUpperOpt.textContent = chamberLabel("upper");
      els.chamberUpperOpt.hidden = !!cfg.unicameral;
      if (cfg.unicameral && els.chamber && els.chamber.value === "upper") {
        els.chamber.value = "";
      }
    }
    if (els.chamber) {
      var both = els.chamber.querySelector('option[value=""]');
      if (both) both.textContent = cfg.unicameral ? "All members" : "Both chambers";
    }
    if (els.zoomExtent) els.zoomExtent.textContent = cfg.zoomExtent;
    if (els.zoomMetro) {
      els.zoomMetro.textContent = cfg.zoomMetro;
      els.zoomMetro.hidden = !cfg.showMetro;
    }
    if (els.footerFacts) els.footerFacts.innerHTML = cfg.footerFactsHtml;
    if (els.footerBoundaries) els.footerBoundaries.innerHTML = cfg.footerBoundariesHtml;
    if (els.seatLabel) els.seatLabel.textContent = cfg.seatFilterLabel;
    if (els.seatAllOpt) els.seatAllOpt.textContent = cfg.seatAllLabel;
    if (els.mapDesc) els.mapDesc.textContent = cfg.mapDesc;
  }

  var pendingFocus = null; // { seat: string, chamber: "lower"|"upper"|"" }

  function applyPendingFocus() {
    if (!pendingFocus) return;
    var want = pendingFocus;
    pendingFocus = null;
    if (typeof setView === "function") setView("list", false);
    if (want.chamber) {
      els.chamber.value = want.chamber;
      syncSeatGroups();
    }
    if (want.seat) {
      var options = Array.prototype.slice.call(els.seat.options);
      var match = null;
      for (var i = 0; i < options.length; i++) {
        if (options[i].value && options[i].value.toLowerCase() === String(want.seat).toLowerCase()) {
          match = options[i];
          break;
        }
      }
      if (match) els.seat.value = match.value;
      else els.q.value = want.seat;
    }
    render();
    var results = document.getElementById("results");
    if (results) {
      if (results.scrollIntoView) results.scrollIntoView({ behavior: "smooth", block: "start" });
      if (typeof results.focus === "function") results.focus();
    }
  }

  function focusSeat(parliament, seatName, chamber) {
    if (!PARLIAMENTS[parliament]) return;
    pendingFocus = {
      seat: seatName || "",
      chamber: chamber || "lower"
    };
    if (parliamentKey === parliament && rows.length) {
      applyPendingFocus();
      return;
    }
    loadParliament(parliament);
  }

  window.PolicyDeskAU = window.PolicyDeskAU || {};
  window.PolicyDeskAU.focusSeat = focusSeat;
  window.PolicyDeskAU.parliaments = PARLIAMENTS;

  function load(data) {
    if (!data || data.parliament !== parliamentKey) return;
    var members = (data.members || []).map(function (m) {
      return {
        id: m.id,
        name: m.name,
        party: m.party,
        chamber: m.chamber,
        seat: seatOf(m),
        url: m.official_url,
        vacant: false
      };
    }).sort(function (a, b) { return collator.compare(a.name, b.name); });

    var vacancies = (data.vacancies || []).map(function (v) {
      var chamber = cfg.vacancyChamber[v.chamber];
      return {
        name: "Vacant seat",
        party: null,
        chamber: chamber,
        seat: chamber === "lower" ? v.electorate : v.region,
        url: null,
        vacant: true
      };
    }).sort(function (a, b) { return collator.compare(a.seat, b.seat); });

    rows = members.concat(vacancies);
    lastListKey = null;

    els.dataLine.classList.remove("is-loading", "is-error");
    els.dataLine.textContent = "";
    els.dataLine.appendChild(document.createTextNode(
      "Data as of " + formatDate(data.last_updated) + ", source: "));
    var src = el("a", null, data.source || cfg.sourceDefault);
    var sourceHref = httpsUrl(data.source_url) ? data.source_url : cfg.sourceHref;
    if (httpsUrl(sourceHref)) src.href = sourceHref;
    els.dataLine.appendChild(src);
    els.dataLine.appendChild(document.createTextNode("."));

    buildFilters();
    // Enter the map only when first landing on #map. Do not call setView("map") again
    // on a parliament switch — that would reset the current zoom and seat focus.
    if (view === "map") {
      render();
    } else if (location.hash === "#map") {
      setView("map", false);
    } else {
      render();
    }
    applyPendingFocus();
  }

  function loadParliament(key) {
    if (!PARLIAMENTS[key]) key = "vic";
    parliamentKey = key;
    cfg = PARLIAMENTS[key];
    if (els.parliament && els.parliament.value !== key) els.parliament.value = key;
    try { localStorage.setItem("policydesk-parliament", key); } catch (e) { /* ignore */ }
    applyParliamentChrome();
    rows = [];
    boundaries = null;
    boundaryPromise = null;
    layerKey = null;
    selected = null;
    viewBox = null;
    lastSeatFilter = "";
    detailKey = "";
    if (view === "map" && mapMode === "detail") {
      els.mapStatus.textContent = "Loading map…";
      els.mapCredit.replaceChildren();
    }
    els.dataLine.classList.remove("is-error");
    els.dataLine.classList.add("is-loading");
    els.dataLine.textContent = "Loading data…";
    var generation = ++loadGeneration;
    fetch(cfg.membersUrl, { cache: "no-cache" })
      .then(function (r) {
        if (generation !== loadGeneration) return null;
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (data) {
        if (generation !== loadGeneration || data == null) return;
        load(data);
      })
      .catch(function () {
        if (generation !== loadGeneration) return;
        els.dataLine.classList.remove("is-loading");
        els.dataLine.classList.add("is-error");
        els.dataLine.textContent = "Sorry, the member list could not be loaded. Please try again later.";
      });
    if (view === "map" && mapMode === "detail") {
      loadBoundaries(generation).then(function () {
        if (generation !== loadGeneration) return;
        if (boundaries) render();
      });
    } else if (view === "map" && mapMode === "overview") {
      render();
    }
  }


  /* ---------- Map view ---------- */
  var view = "list";
  var mapMode = "overview";   // "overview" (Australia) | "detail" (current parliament)
  var boundaries = null;      // parliament layers, e.g. { districts: doc, regions: doc }
  var boundaryPromise = null;
  var overviewDoc = null;     // national state/territory outlines
  var overviewPromise = null;
  var layerKey = null;        // "districts" | "regions" | …
  var selected = null;        // seat name
  var viewBox = null;         // [x, y, w, h]
  var lastShown = [];
  var lastSeatFilter = "";
  var detailKey = "";
  var overviewDrawn = false;

  function setLayerCopy(main, note) {
    if (!els.mapLayer) return;
    els.mapLayer.replaceChildren(document.createTextNode(main || ""));
    if (note) els.mapLayer.appendChild(el("span", "map-note", note));
  }

  function setMapCredit(d) {
    function link(text, href) {
      if (!httpsUrl(href)) return document.createTextNode(text);
      var a = el("a", null, text);
      a.href = href;
      return a;
    }
    function txt(t) { return document.createTextNode(t); }
    els.mapCredit.replaceChildren(
      txt(d.credit || ("Electoral boundaries: " + (d.source || "") + ". ")),
      txt(" "), link(d.licence || "Licence", d.licence_url),
      txt(". " + (d.boundary_version || "")));
  }

  function loadOverview() {
    if (!overviewPromise) {
      overviewPromise = fetch(OVERVIEW_URL, { cache: "no-cache" }).then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      }).then(function (doc) {
        overviewDoc = doc;
        els.mapStatus.textContent = "";
        return doc;
      }).catch(function () {
        overviewPromise = null;
        overviewDoc = null;
        els.mapStatus.textContent = "Sorry, the map could not be loaded. The list view still works.";
        if (els.mapHint) els.mapHint.hidden = true;
      });
    }
    return overviewPromise;
  }

  function loadBoundaries(generation) {
    if (!boundaryPromise) {
      var files = cfg.boundaryFiles;
      var keys = Object.keys(files);
      boundaryPromise = Promise.all(keys.map(function (k) {
        return fetch(files[k], { cache: "no-cache" }).then(function (r) {
          if (generation !== loadGeneration) return null;
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.json();
        });
      })).then(function (docs) {
        if (generation !== loadGeneration) return;
        if (!docs || docs.some(function (d) { return !d; })) return;
        boundaries = {};
        keys.forEach(function (k, i) { boundaries[k] = docs[i]; });
        setMapCredit(docs[0]);
        els.mapStatus.textContent = "";
      }).catch(function () {
        if (generation !== loadGeneration) return;
        boundaryPromise = null;
        els.mapStatus.textContent = "Sorry, the map could not be loaded. The list view still works.";
        if (els.mapHint) els.mapHint.hidden = true;
      });
    }
    return boundaryPromise;
  }

  function lowerLayer() { return cfg.layers.lower; }
  function upperLayer() { return cfg.layers.upper || null; }
  function extentDoc() { return boundaries[lowerLayer()]; }
  function mapReady() { return mapMode === "overview" ? !!overviewDoc : !!boundaries; }
  function activeFullBox() {
    if (mapMode === "overview") return overviewDoc && overviewDoc.viewBox;
    return boundaries && extentDoc() && extentDoc().viewBox;
  }

  function syncMapChrome() {
    var onOverview = mapMode === "overview";
    if (els.zoomAustralia) els.zoomAustralia.setAttribute("aria-current", String(onOverview));
    if (els.zoomExtent) els.zoomExtent.hidden = onOverview;
    if (els.zoomMetro) els.zoomMetro.hidden = onOverview || !cfg.showMetro;
    if (els.mapHint) {
      els.mapHint.hidden = false;
      els.mapHint.textContent = onOverview ? OVERVIEW_HINT : DETAIL_HINT;
    }
    if (els.mapDesc) els.mapDesc.textContent = onOverview ? OVERVIEW_DESC : cfg.mapDesc;
  }

  function enterOverview() {
    mapMode = "overview";
    selected = null;
    layerKey = null;
    overviewDrawn = false;
    detailKey = "";
    viewBox = null;
    syncMapChrome();
    loadOverview().then(function () {
      if (view !== "map" || mapMode !== "overview" || !overviewDoc) return;
      setMapCredit(overviewDoc);
      setViewBox(overviewDoc.viewBox);
      render();
    });
  }

  function focusParliamentFromMap(key) {
    if (!PARLIAMENTS[key]) return;
    mapMode = "detail";
    overviewDrawn = false;
    syncMapChrome();
    if (key === parliamentKey && boundaries) {
      selected = null;
      layerKey = null;
      viewBox = null;
      lastSeatFilter = "";
      detailKey = "";
      setMapCredit(boundaries[lowerLayer()]);
      setViewBox(extentDoc().viewBox);
      render();
      return;
    }
    loadParliament(key);
  }

  function syncSkipLink() {
    if (!els.skip) return;
    els.skip.href = view === "map" ? "#map-view" : "#results";
  }

  function setMapDetailMessage(text) {
    detailKey = "message";
    els.mapDetail.replaceChildren();
    els.mapDetail.appendChild(el("p", "meta", text));
  }

  function clearMapDrawing() {
    var title = els.map.querySelector("title");
    els.map.replaceChildren(title);
    els.map.classList.remove("is-zoomed");
  }

  /* Map opens the parliament already chosen. Australia is only the Australia button. */
  function enterParliamentMap() {
    mapMode = "detail";
    selected = null;
    layerKey = null;
    overviewDrawn = false;
    viewBox = null;
    lastSeatFilter = "";
    detailKey = "";
    syncMapChrome();
    if (boundaries) {
      setMapCredit(boundaries[lowerLayer()]);
    } else {
      els.mapStatus.textContent = "Loading map…";
      els.mapLayer.textContent = "";
      els.seatButtons.replaceChildren();
      els.seatCount.textContent = "0";
      if (els.seatListLabel) els.seatListLabel.textContent = "Text list of seats on this map";
      els.mapCredit.replaceChildren();
      clearMapDrawing();
      setMapDetailMessage("Loading map…");
    }
    var generation = loadGeneration;
    loadBoundaries(generation).then(function () {
      if (view !== "map" || mapMode !== "detail" || generation !== loadGeneration) return;
      if (boundaries) {
        setMapCredit(boundaries[lowerLayer()]);
        render();
        return;
      }
      els.mapStatus.textContent = "Sorry, the map could not be loaded. The list view still works.";
      clearMapDrawing();
      setMapDetailMessage("Sorry, the map could not be loaded. The list view still works.");
      if (els.mapHint) els.mapHint.hidden = true;
    });
  }

  function setView(v, focus) {
    var openParliament = v === "map" && (view !== "map" || mapMode !== "detail");
    view = v;
    els.viewList.setAttribute("aria-pressed", String(v === "list"));
    els.viewMap.setAttribute("aria-pressed", String(v === "map"));
    els.results.hidden = v !== "list";
    els.mapView.hidden = v !== "map";
    syncSkipLink();
    try { history.replaceState(null, "", v === "map" ? "#map" : location.pathname + location.search); } catch (e) { /* ignore */ }
    if (openParliament) enterParliamentMap();
    render();
    if (focus) (v === "map" ? els.mapView : els.results).focus();
  }

  function setViewBox(b) {
    var full = activeFullBox();
    if (!full) return;
    // Match the active layer's own aspect (portrait QLD ~1.4, landscape Vic ~0.72)
    // so Whole state is not clipped by a fixed landscape ratio.
    var ratio = Math.max(full[3] / Math.max(full[2], 1), 0.5);
    var w = Math.max(b[2], 40), h = Math.max(b[3], 40);
    if (h / w > ratio) w = h / ratio; else h = w * ratio;
    var maxW = full[2] * 1.02, maxH = full[3] * 1.02;
    if (w > maxW || h > maxH) {
      var scale = Math.min(maxW / w, maxH / h);
      w *= scale;
      h *= scale;
    }
    var cx = b[0] + b[2] / 2, cy = b[1] + b[3] / 2;
    // keep the map in view: clamp the centre so we never drift off the extent
    cx = w >= full[2] ? full[2] / 2 : Math.min(Math.max(cx, w / 2), full[2] - w / 2);
    cy = h >= full[3] ? full[3] / 2 : Math.min(Math.max(cy, h / 2), full[3] - h / 2);
    viewBox = [cx - w / 2, cy - h / 2, w, h];
    els.map.classList.toggle(
      "is-zoomed",
      w < full[2] * 0.98 || h < full[3] * 0.98
    );
    els.map.setAttribute("viewBox", viewBox.map(function (n) { return Math.round(n); }).join(" "));
    // Match the SVG box to the active viewBox so portrait states (QLD) are not
    // letterboxed/clipped by the default landscape CSS aspect-ratio.
    els.map.style.aspectRatio = Math.round(w) + " / " + Math.round(h);
  }

  function bboxOf(names) {
    var feats = boundaries[layerKey].features.filter(function (f) { return names.indexOf(f.name) !== -1; });
    if (!feats.length) return null;
    var b = [Infinity, Infinity, -Infinity, -Infinity];
    feats.forEach(function (f) {
      b[0] = Math.min(b[0], f.bbox[0]); b[1] = Math.min(b[1], f.bbox[1]);
      b[2] = Math.max(b[2], f.bbox[2]); b[3] = Math.max(b[3], f.bbox[3]);
    });
    return [b[0], b[1], b[2] - b[0], b[3] - b[1]];
  }

  function zoomTo(kind) {
    if (kind === "australia") return enterOverview();
    if (!mapReady()) return;
    var full = activeFullBox();
    if (!full) return;
    if (kind === "state") return setViewBox(full);
    if (kind === "melbourne") {
      if (mapMode === "overview") return setViewBox(full);
      if (parliamentKey === "federal") {
        // Rough south-east Australia crop of the national viewBox.
        return setViewBox([full[0] + full[2] * 0.55, full[1] + full[3] * 0.45, full[2] * 0.4, full[3] * 0.45]);
      }
      if (parliamentKey === "nsw") {
        // Rough Sydney / coastal crop of the statewide viewBox.
        return setViewBox([full[0] + full[2] * 0.55, full[1] + full[3] * 0.55, full[2] * 0.4, full[3] * 0.4]);
      }
      if (parliamentKey === "qld") {
        // Rough south-east Queensland / Brisbane crop.
        return setViewBox([full[0] + full[2] * 0.55, full[1] + full[3] * 0.55, full[2] * 0.4, full[3] * 0.4]);
      }
      if (parliamentKey === "wa") {
        // Perth metro is south-west of the statewide viewBox (not SE like NSW/QLD).
        // District union ~[1572,12204]–[2173,12886] of viewBox [0,0,10000,14754].
        return setViewBox([
          full[0] + full[2] * 0.12,
          full[1] + full[3] * 0.80,
          full[2] * 0.15,
          full[3] * 0.12
        ]);
      }
      if (parliamentKey === "sa") {
        // Adelaide metro is east / south-east of the statewide viewBox (not SE like NSW/QLD).
        // Metro district union ~[7885,8252]–[8152,8876] of viewBox [0,0,10000,11609].
        return setViewBox([
          full[0] + full[2] * 0.72,
          full[1] + full[3] * 0.65,
          full[2] * 0.18,
          full[3] * 0.20
        ]);
      }
      if (parliamentKey === "tas") {
        // Hobart / south-east crop of the statewide viewBox.
        return setViewBox([
          full[0] + full[2] * 0.55,
          full[1] + full[3] * 0.55,
          full[2] * 0.40,
          full[3] * 0.40
        ]);
      }
      if (parliamentKey === "act") {
        // Canberra urban area — central crop of the territory viewBox.
        return setViewBox([
          full[0] + full[2] * 0.25,
          full[1] + full[3] * 0.20,
          full[2] * 0.55,
          full[3] * 0.55
        ]);
      }
      if (parliamentKey === "nt") {
        // Darwin / Palmerston urban divisions sit in the north of a tall territory.
        // Union of those divisions ~[2014,1732]–[2238,1995] of viewBox [0,0,10000,17853].
        return setViewBox([
          full[0] + full[2] * 0.19,
          full[1] + full[3] * 0.09,
          full[2] * 0.04,
          full[3] * 0.03
        ]);
      }
      var upper = upperLayer();
      if (!upper || !boundaries[upper]) return setViewBox(full);
      var metro = boundaries[upper].features.filter(function (f) { return METRO.test(f.name); });
      var b = [Infinity, Infinity, -Infinity, -Infinity];
      metro.forEach(function (f) {
        b[0] = Math.min(b[0], f.bbox[0]); b[1] = Math.min(b[1], f.bbox[1]);
        b[2] = Math.max(b[2], f.bbox[2]); b[3] = Math.max(b[3], f.bbox[3]);
      });
      return setViewBox([b[0], b[1], b[2] - b[0], b[3] - b[1]]);
    }
    if (!viewBox) setViewBox(full);
    var f = kind === "in" ? 0.5 : 2;
    setViewBox([viewBox[0] + viewBox[2] * (1 - f) / 2, viewBox[1] + viewBox[3] * (1 - f) / 2, viewBox[2] * f, viewBox[3] * f]);
  }

  function select(name, zoom) {
    selected = name;
    if (zoom) {
      var b = bboxOf([name]);
      if (b) setViewBox([b[0] - b[2] * 0.4, b[1] - b[3] * 0.4, b[2] * 1.8, b[3] * 1.8]);
    }
    renderMap(lastShown);
  }

  function renderOverviewDetail() {
    var key = "overview|" + parliamentKey;
    if (key === detailKey) return;
    detailKey = key;
    els.mapDetail.replaceChildren();
    var current = PARLIAMENTS[parliamentKey];
    var where = current ? current.label : "the menu";
    els.mapDetail.appendChild(el("p", "meta",
      "The Parliament menu is on " + where + ". Tap a live state or territory, or choose a place from the list. The member list updates to match."));
  }

  function renderDetail(shown) {
    if (mapMode === "overview") return renderOverviewDetail();
    var chamberKey = layerKey === upperLayer() ? "upper" : "lower";
    var key = layerKey + "|" + selected + "|" + shown.filter(function (r) {
      return r.seat === selected && r.chamber === chamberKey;
    }).map(function (r) { return r.name; }).join(",");
    if (key === detailKey) return;
    detailKey = key;
    els.mapDetail.replaceChildren();
    if (!selected) {
      els.mapDetail.appendChild(el("p", "meta", "Tap or click an area on the map, or pick a seat from the list below. Use Australia to return to the national map."));
      return;
    }
    var chamber = chamberKey;
    var label = cfg.seatLabel[chamber];
    els.mapDetail.appendChild(el("h2", null, selected + label));
    var inSeat = rows.filter(function (r) { return r.seat === selected && r.chamber === chamber; });
    var matching = shown.filter(function (r) { return r.seat === selected && r.chamber === chamber; });
    var list = el("ul", "cards");
    (matching.length ? matching : inSeat).forEach(function (r) { list.appendChild(card(r)); });
    if (!inSeat.length) els.mapDetail.appendChild(el("p", "meta", "No member data for this seat."));
    if (inSeat.length && !matching.length) {
      els.mapDetail.appendChild(el("p", "meta", "No members here match your filters. Showing everyone for this seat."));
    }
    els.mapDetail.appendChild(list);
  }

  function renderOverview() {
    syncMapChrome();
    if (!overviewDoc) return;
    if (!overviewDrawn) {
      overviewDrawn = true;
      var g = document.createElementNS(SVG_NS, "g");
      overviewDoc.features.forEach(function (f) {
        var p = document.createElementNS(SVG_NS, "path");
        var liveKey = STATE_TO_PARLIAMENT[f.name];
        p.setAttribute("d", f.d);
        p.setAttribute("class", "jurisdiction " + (liveKey ? "is-live" : "is-soon"));
        p.dataset.name = f.name;
        if (liveKey) p.dataset.parliament = liveKey;
        var t = document.createElementNS(SVG_NS, "title");
        t.textContent = liveKey
          ? f.name + " — open state parliament map"
          : f.name + " — not listed on this site yet";
        p.appendChild(t);
        g.appendChild(p);
      });
      els.map.replaceChildren(els.map.querySelector("title"), g);
      if (!viewBox) setViewBox(overviewDoc.viewBox);
      setMapCredit(overviewDoc);
    }
    els.map.querySelectorAll("path.jurisdiction").forEach(function (p) {
      var liveKey = p.dataset.parliament;
      var current = false;
      if (parliamentKey === "federal") current = false;
      else if (liveKey) current = liveKey === parliamentKey;
      p.classList.toggle("is-current", current);
    });
    els.mapLayer.textContent =
      "Showing Australia. Live jurisdictions: Federal, Victoria, New South Wales, Queensland, Western Australia, South Australia, Tasmania, Australian Capital Territory, and Northern Territory.";

    var items = OVERVIEW_LIVE.slice();
    overviewDoc.features.forEach(function (f) {
      if (!STATE_TO_PARLIAMENT[f.name]) items.push({ key: null, label: f.name, soon: true });
    });
    els.seatCount.textContent = String(items.length);
    if (els.seatListLabel) els.seatListLabel.textContent = "Text list of places on this map";
    var frag = document.createDocumentFragment();
    items.forEach(function (item) {
      var li = document.createElement("li");
      if (item.soon) {
        var span = el("span", "seat-btn is-soon-label", item.label + " (not listed yet)");
        span.setAttribute("aria-disabled", "true");
        li.appendChild(span);
      } else {
        var b = el("button", "seat-btn", item.label);
        b.type = "button";
        if (item.key === parliamentKey) b.setAttribute("aria-current", "true");
        b.dataset.parliament = item.key;
        b.addEventListener("click", function () {
          focusParliamentFromMap(item.key);
          var again = els.seatButtons.querySelector('[data-parliament="' + CSS.escape(item.key) + '"]');
          if (again) again.focus();
        });
        li.appendChild(b);
      }
      frag.appendChild(li);
    });
    els.seatButtons.replaceChildren(frag);
    renderOverviewDetail();
  }

  function renderMap(shown) {
    lastShown = shown;
    if (mapMode === "overview") {
      renderOverview();
      return;
    }
    if (!boundaries) return;
    syncMapChrome();
    var seat = els.seat.value;
    var upperKey = upperLayer();
    var upperFeats = (upperKey && boundaries[upperKey]) ? boundaries[upperKey].features : [];
    var seatIsUpper = !!seat && upperFeats.some(function (f) { return f.name === seat; });
    var newLayer = (!cfg.unicameral && (els.chamber.value === "upper" || seatIsUpper) && upperKey)
      ? upperKey
      : lowerLayer();
    if (newLayer !== layerKey) {
      layerKey = newLayer;
      selected = null;
      els.map.querySelectorAll("path").forEach(function (p) { p.remove(); });
      var g = document.createElementNS(SVG_NS, "g");
      boundaries[layerKey].features.forEach(function (f) {
        var p = document.createElementNS(SVG_NS, "path");
        p.setAttribute("d", f.d);
        p.setAttribute("class", "seat");
        p.dataset.name = f.name;
        var t = document.createElementNS(SVG_NS, "title");
        t.textContent = f.name;
        p.appendChild(t);
        g.appendChild(p);
      });
      els.map.replaceChildren(els.map.querySelector("title"), g);
      if (!viewBox) setViewBox(extentDoc().viewBox);
    }
    var seatChanged = seat !== lastSeatFilter;
    lastSeatFilter = seat;
    if (seat && seatChanged && boundaries[layerKey].features.some(function (f) { return f.name === seat; })) {
      selected = seat;
      var b = bboxOf([seat]);
      if (b) setViewBox([b[0] - b[2] * 0.4, b[1] - b[3] * 0.4, b[2] * 1.8, b[3] * 1.8]);
    }

    var chamber = layerKey === upperLayer() ? "upper" : "lower";
    var matchSeats = {};
    shown.forEach(function (r) { if (r.chamber === chamber) matchSeats[r.seat] = true; });

    var filtering = !!(els.q.value.trim() || els.party.value || els.seat.value);
    els.map.querySelectorAll("path.seat").forEach(function (p) {
      var n = p.dataset.name;
      p.classList.toggle("is-match", filtering && !!matchSeats[n]);
      p.classList.toggle("is-dim", filtering && !matchSeats[n]);
      p.classList.toggle("is-selected", n === selected);
    });
    var sel = els.map.querySelector("path.is-selected");
    if (sel) sel.parentNode.appendChild(sel);  // draw selected outline on top

    var upperMatches = shown.filter(function (r) { return r.chamber === "upper"; }).length;
    var layerMain = (chamber === "upper" ? cfg.mapUpper : cfg.mapLower) +
      (filtering ? " Highlighted areas match your filters." : "");
    var layerNote = "";
    if (chamber !== "upper" && !els.chamber.value) {
      layerNote = (filtering && upperMatches)
        ? upperMatches + " matching " + chamberLabel("upper") + " member" +
          (upperMatches > 1 ? "s are" : " is") + " not shown here:" + cfg.mapOtherHint
        : (cfg.mapOtherHint || "").replace(/^\s+/, "");
    }
    setLayerCopy(layerMain, layerNote);

    var names = boundaries[layerKey].features.map(function (f) { return f.name; })
      .filter(function (n) { return matchSeats[n]; });
    els.seatCount.textContent = String(names.length);
    if (els.seatListLabel) els.seatListLabel.textContent = "Text list of seats on this map";
    var frag = document.createDocumentFragment();
    names.forEach(function (n) {
      var li = document.createElement("li");
      var btn = el("button", "seat-btn", n);
      btn.type = "button";
      if (n === selected) btn.setAttribute("aria-current", "true");
      btn.dataset.name = n;
      btn.addEventListener("click", function () {
        select(n, true);
        var again = els.seatButtons.querySelector('[data-name="' + CSS.escape(n) + '"]');
        if (again) again.focus();
      });
      li.appendChild(btn);
      frag.appendChild(li);
    });
    els.seatButtons.replaceChildren(frag);
    renderDetail(shown);
  }

  /* Drag to move, pinch (or ctrl + scroll / trackpad pinch) to zoom. */
  var pointers = {};       // pointerId -> {x, y}
  var gesture = null;      // {vb, x, y, dist, moved}
  var suppressClick = false;
  var lastTouchSelect = 0;  // touch taps select on pointerup; ignore the click that may follow

  function selectAt(x, y) {
    var hit = document.elementFromPoint(x, y);
    if (mapMode === "overview") {
      var j = hit && hit.closest && hit.closest("path.jurisdiction.is-live");
      if (j && j.dataset.parliament) focusParliamentFromMap(j.dataset.parliament);
      return;
    }
    var p = hit && hit.closest && hit.closest("path.seat");
    if (p) select(p.dataset.name, false);
  }

  function unitsPerPx() {
    var r = els.map.getBoundingClientRect();
    return Math.max(viewBox[2] / r.width, viewBox[3] / r.height);  // "meet" scaling
  }
  function toMap(clientX, clientY) {
    var r = els.map.getBoundingClientRect(), k = unitsPerPx();
    return [
      viewBox[0] + viewBox[2] / 2 + (clientX - (r.left + r.width / 2)) * k,
      viewBox[1] + viewBox[3] / 2 + (clientY - (r.top + r.height / 2)) * k
    ];
  }
  function zoomAround(clientX, clientY, factor) {
    var pt = toMap(clientX, clientY);
    var w = viewBox[2] * factor, h = viewBox[3] * factor;
    var fx = (pt[0] - viewBox[0]) / viewBox[2], fy = (pt[1] - viewBox[1]) / viewBox[3];
    setViewBox([pt[0] - fx * w, pt[1] - fy * h, w, h]);
  }
  function pointerList() { return Object.keys(pointers).map(function (k) { return pointers[k]; }); }
  function startGesture() {
    var ps = pointerList();
    if (!ps.length) { gesture = null; return; }
    var cx = ps.reduce(function (a, p) { return a + p.x; }, 0) / ps.length;
    var cy = ps.reduce(function (a, p) { return a + p.y; }, 0) / ps.length;
    var dist = ps.length > 1 ? Math.hypot(ps[0].x - ps[1].x, ps[0].y - ps[1].y) : 0;
    gesture = { vb: viewBox.slice(), x: cx, y: cy, dist: dist, k: unitsPerPx(),
      moved: gesture ? gesture.moved : false, multi: (gesture && gesture.multi) || ps.length > 1 };
  }

  els.map.addEventListener("pointerdown", function (e) {
    if (!mapReady() || !viewBox || (e.pointerType === "mouse" && e.button !== 0)) return;
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
    try { els.map.setPointerCapture(e.pointerId); } catch (err) { /* ignore */ }
    if (Object.keys(pointers).length === 1) { gesture = null; suppressClick = false; }
    startGesture();
  });
  els.map.addEventListener("pointermove", function (e) {
    if (!gesture || !pointers[e.pointerId]) return;
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
    var ps = pointerList();
    var cx = ps.reduce(function (a, p) { return a + p.x; }, 0) / ps.length;
    var cy = ps.reduce(function (a, p) { return a + p.y; }, 0) / ps.length;
    if (!gesture.moved && Math.hypot(cx - gesture.x, cy - gesture.y) < 6 && ps.length < 2) return;
    gesture.moved = true;
    var scale = ps.length > 1 && gesture.dist > 0
      ? gesture.dist / Math.hypot(ps[0].x - ps[1].x, ps[0].y - ps[1].y) : 1;
    var vb = gesture.vb;
    // point under the gesture start stays under the fingers
    var r = els.map.getBoundingClientRect();
    var ax = vb[0] + vb[2] / 2 + (gesture.x - (r.left + r.width / 2)) * gesture.k;
    var ay = vb[1] + vb[3] / 2 + (gesture.y - (r.top + r.height / 2)) * gesture.k;
    var w = vb[2] * scale, h = vb[3] * scale, k = gesture.k * scale;
    var ncx = ax - (cx - (r.left + r.width / 2)) * k;
    var ncy = ay - (cy - (r.top + r.height / 2)) * k;
    setViewBox([ncx - w / 2, ncy - h / 2, w, h]);
  });
  function endPointer(e) {
    if (!pointers[e.pointerId]) return;
    delete pointers[e.pointerId];
    // a mouse drag is followed by a click we must ignore; touch drags fire no click
    if (e.type === "pointerup" && e.pointerType === "mouse" && gesture && gesture.moved) suppressClick = true;
    if (e.type === "pointerup" && e.pointerType !== "mouse" && gesture && !gesture.moved && !gesture.multi &&
        !Object.keys(pointers).length) {
      lastTouchSelect = Date.now();
      selectAt(e.clientX, e.clientY);
    }
    if (Object.keys(pointers).length) startGesture(); else gesture = null;
  }
  els.map.addEventListener("pointerup", endPointer);
  els.map.addEventListener("pointercancel", endPointer);
  els.map.addEventListener("wheel", function (e) {
    if (!mapReady() || !viewBox || !e.ctrlKey) return;  // plain scroll keeps scrolling the page
    e.preventDefault();
    var dy = e.deltaMode === 1 ? e.deltaY * 33 : e.deltaY;          // lines -> pixels
    var step = Math.max(-0.35, Math.min(0.35, dy * 0.005));       // at most ~1.4x per event
    zoomAround(e.clientX, e.clientY, Math.exp(step));
  }, { passive: false });

  els.map.addEventListener("click", function (e) {
    if (suppressClick) { suppressClick = false; return; }
    if (Date.now() - lastTouchSelect < 800) return;  // already handled on pointerup
    // pointer capture makes the SVG the click target, so find the area under the pointer
    selectAt(e.clientX, e.clientY);
  });
  els.mapView.querySelectorAll("[data-zoom]").forEach(function (b) {
    b.addEventListener("click", function () { zoomTo(b.dataset.zoom); });
  });
  els.viewList.addEventListener("click", function () { setView("list", false); });
  els.viewMap.addEventListener("click", function () { setView("map", false); });
  if (els.skip) {
    els.skip.addEventListener("click", function (e) {
      var target = view === "map" ? els.mapView : els.results;
      if (!target) return;
      // Leave the #map hash alone. Following #map-view would be read as leaving the map.
      e.preventDefault();
      target.focus();
    });
  }

  els.form.addEventListener("input", function (e) {
    if (e.target && e.target.id === "parliament") return;
    render();
  });
  els.form.addEventListener("change", function (e) {
    if (e.target && e.target.id === "parliament") {
      mapMode = "detail";
      overviewDrawn = false;
      syncMapChrome();
      loadParliament(els.parliament.value);
      return;
    }
    render();
  });
  els.form.addEventListener("submit", function (e) { e.preventDefault(); });
  els.form.addEventListener("reset", function () {
    selected = null;
    setTimeout(function () {
      // Keep the chosen parliament on clear; only clear search filters.
      if (els.parliament) els.parliament.value = parliamentKey;
      if (mapMode === "detail" && boundaries) setViewBox(extentDoc().viewBox);
      else if (mapMode === "overview" && overviewDoc) setViewBox(overviewDoc.viewBox);
      render();
    }, 0);
  });
  window.addEventListener("hashchange", function () {
    if (!rows.length) return;
    // The skip link’s map target. It is not a request to show the list.
    if (location.hash === "#map-view") {
      if (view !== "map") setView("map", true);
      else if (els.mapView) els.mapView.focus();
      try { history.replaceState(null, "", "#map"); } catch (e) { /* ignore */ }
      return;
    }
    var want = location.hash === "#map" ? "map" : "list";
    if (want !== view) setView(want, false);
  });

  fetch("data/news/index.json", { cache: "no-cache" })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (idx) {
      if (!idx) return;
      newsIndex = idx;
      var c = document.getElementById("news-credit");
      if (c && httpsUrl(idx.source_url) && httpsUrl(idx.licence_url)) {
        var src = el("a", null, idx.source); src.href = idx.source_url;
        var lic = el("a", null, idx.licence); lic.href = idx.licence_url;
        c.replaceChildren(document.createTextNode("Headlines from "), src, document.createTextNode(" ("), lic,
          document.createTextNode("), matched by exact full name in the headline or with the member's electorate, and checked daily. " +
            "We show the headline, date and link only."));
      }
      if (rows.length) render();
    })
    .catch(function () { /* news is optional */ });

  [["data/photos.json", function (d) { photos = d.photos || {}; }],
   ["data/socials.json", function (d) { socials = d.socials || {}; }]].forEach(function (x) {
    fetch(x[0], { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (!d) return; x[1](d); extrasVersion++; if (rows.length) render(); })
      .catch(function () { /* optional */ });
  });

  var start = "vic";
  try {
    var saved = localStorage.getItem("policydesk-parliament");
    if (saved && PARLIAMENTS[saved]) start = saved;
  } catch (e) { /* ignore */ }
  var params = new URLSearchParams(location.search);
  if (params.get("parliament") && PARLIAMENTS[params.get("parliament")]) {
    start = params.get("parliament");
  }
  loadParliament(start);
})();
