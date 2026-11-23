/* The Policy Desk AU: member list view. Vanilla JS, no build step. AGPL-3.0. */
(function () {
  "use strict";

  var CHAMBER = { lower: "Legislative Assembly", upper: "Legislative Council" };
  var VACANCY_CHAMBER = { Assembly: "lower", Council: "upper", lower: "lower", upper: "upper" };

  var els = {
    form: document.getElementById("filters"),
    q: document.getElementById("q"),
    chamber: document.getElementById("chamber"),
    party: document.getElementById("party"),
    seat: document.getElementById("seat"),
    list: document.getElementById("list"),
    count: document.getElementById("count"),
    dataLine: document.getElementById("data-line")
  };

  var collator = new Intl.Collator("en-AU", { sensitivity: "base" });
  var rows = [];

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
    var parties = {};
    var seats = { lower: {}, upper: {} };
    rows.forEach(function (r) {
      if (r.party) parties[r.party] = true;
      if (r.seat) seats[r.chamber][r.seat] = true;
    });
    addOptions(els.party, Object.keys(parties).sort(collator.compare));

    ["lower", "upper"].forEach(function (c) {
      var group = document.createElement("optgroup");
      group.label = CHAMBER[c];
      addOptions(group, Object.keys(seats[c]).sort(collator.compare));
      els.seat.appendChild(group);
    });
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
    var avatar = el("span", "avatar", r.vacant ? "–" : initials(r.name));
    avatar.setAttribute("aria-hidden", "true");
    li.appendChild(avatar);

    var body = el("div", "card-body");
    body.appendChild(el("h2", null, r.vacant ? "Vacant seat" : r.name));
    if (!r.vacant) body.appendChild(el("p", null, r.party));
    body.appendChild(el("p", "meta", r.seat + " · " + CHAMBER[r.chamber]));
    if (r.vacant) body.appendChild(el("p", "meta", "Vacancy recorded by The Policy Desk AU; official source not yet linked."));

    if (r.url && /^https:\/\//.test(r.url)) {
      var a = el("a", "profile", "Official profile");
      a.href = r.url;
      var sr = el("span", "visually-hidden", " for " + r.name + " on the Parliament of Victoria website");
      a.appendChild(sr);
      body.appendChild(a);
    }
    li.appendChild(body);
    return li;
  }

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

    var frag = document.createDocumentFragment();
    shown.forEach(function (r) { frag.appendChild(card(r)); });
    els.list.replaceChildren(frag);

    if (!shown.length) {
      els.list.appendChild(el("li", "empty", "No members match these filters."));
    }
    var vacant = shown.filter(function (r) { return r.vacant; }).length;
    var text = "Showing " + (shown.length - vacant) + " of " +
      rows.filter(function (r) { return !r.vacant; }).length + " members";
    if (vacant) text += " and " + vacant + " vacant seat" + (vacant > 1 ? "s" : "");
    els.count.textContent = text + ".";
  }

  function load(data) {
    var members = (data.members || []).map(function (m) {
      return {
        name: m.name,
        party: m.party,
        chamber: m.chamber,
        seat: seatOf(m),
        url: m.official_url,
        vacant: false
      };
    }).sort(function (a, b) { return collator.compare(a.name, b.name); });

    var vacancies = (data.vacancies || []).map(function (v) {
      var chamber = VACANCY_CHAMBER[v.chamber];
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

    els.dataLine.textContent = "";
    els.dataLine.appendChild(document.createTextNode(
      "Data as of " + formatDate(data.last_updated) + ", source: "));
    var src = el("a", null, data.source || "Parliament of Victoria");
    src.href = "https://www.parliament.vic.gov.au/members/";
    els.dataLine.appendChild(src);
    els.dataLine.appendChild(document.createTextNode("."));

    buildFilters();
    render();
  }

  els.form.addEventListener("input", render);
  els.form.addEventListener("change", render);
  els.form.addEventListener("submit", function (e) { e.preventDefault(); });
  els.form.addEventListener("reset", function () { setTimeout(render, 0); });

  fetch("data/members.json", { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(load)
    .catch(function () {
      els.dataLine.textContent = "Sorry, the member list could not be loaded. Please try again later.";
    });
})();
