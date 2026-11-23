/* The Policy Desk AU: member list and map views. Vanilla JS, no build step. AGPL-3.0. */
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
    dataLine: document.getElementById("data-line"),
    results: document.getElementById("results"),
    viewList: document.getElementById("view-list"),
    viewMap: document.getElementById("view-map"),
    mapView: document.getElementById("map-view"),
    map: document.getElementById("map"),
    mapStatus: document.getElementById("map-status"),
    mapLayer: document.getElementById("map-layer"),
    mapDetail: document.getElementById("map-detail"),
    seatButtons: document.getElementById("seat-buttons"),
    seatCount: document.getElementById("seat-count"),
    mapCredit: document.getElementById("map-credit")
  };
  var SVG_NS = "http://www.w3.org/2000/svg";
  var METRO = /Metropolitan$/;

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
    if (view === "map") renderMap(shown);
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
    if (location.hash === "#map") setView("map", false); else render();
  }


  /* ---------- Map view ---------- */
  var view = "list";
  var boundaries = null;      // { districts: doc, regions: doc }
  var boundaryPromise = null;
  var layerKey = null;        // "districts" | "regions"
  var selected = null;        // seat name
  var viewBox = null;         // [x, y, w, h]
  var lastShown = [];
  var lastSeatFilter = "";
  var detailKey = "";

  function loadBoundaries() {
    if (!boundaryPromise) {
      boundaryPromise = Promise.all(["districts", "regions"].map(function (k) {
        return fetch("data/boundaries/vic_" + k + ".json").then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.json();
        });
      })).then(function (docs) {
        boundaries = { districts: docs[0], regions: docs[1] };
        var d = docs[0];
        var r = docs[1];
        function link(text, href) { var a = el("a", null, text); a.href = href; return a; }
        function txt(t) { return document.createTextNode(t); }
        els.mapCredit.replaceChildren(
          txt("Electoral boundaries: Victorian Electoral Commission, via DataVic ("),
          link("districts", d.dataset_url), txt(", "), link("regions", r.dataset_url),
          txt("), licensed under "), link("CC BY 4.0", d.licence_url),
          txt(". Simplified by The Policy Desk AU. " + d.boundary_version + "."));
        els.mapStatus.textContent = "";
      }).catch(function () {
        boundaryPromise = null;
        els.mapStatus.textContent = "Sorry, the map could not be loaded. The list view still works.";
      });
    }
    return boundaryPromise;
  }

  function setView(v, focus) {
    view = v;
    els.viewList.setAttribute("aria-pressed", String(v === "list"));
    els.viewMap.setAttribute("aria-pressed", String(v === "map"));
    els.results.hidden = v !== "list";
    els.mapView.hidden = v !== "map";
    try { history.replaceState(null, "", v === "map" ? "#map" : location.pathname + location.search); } catch (e) { /* ignore */ }
    if (v === "map") {
      loadBoundaries().then(function () { if (boundaries) render(); });
    }
    render();
    if (focus) (v === "map" ? els.mapView : els.results).focus();
  }

  function setViewBox(b) {
    var ratio = 0.72;  // keep a sensible aspect
    var full = boundaries.districts.viewBox;
    var w = Math.max(b[2], 40), h = Math.max(b[3], 40);
    if (h / w > ratio) w = h / ratio; else h = w * ratio;
    var maxW = full[2] * 1.02, maxH = full[2] * 1.02 * ratio;
    if (w > maxW) { w = maxW; h = maxH; }
    var cx = b[0] + b[2] / 2, cy = b[1] + b[3] / 2;
    // keep the map in view: clamp the centre so we never drift off the state
    cx = w >= full[2] ? full[2] / 2 : Math.min(Math.max(cx, w / 2), full[2] - w / 2);
    cy = h >= full[3] ? full[3] / 2 : Math.min(Math.max(cy, h / 2), full[3] - h / 2);
    viewBox = [cx - w / 2, cy - h / 2, w, h];
    els.map.setAttribute("viewBox", viewBox.map(function (n) { return Math.round(n); }).join(" "));
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
    if (!boundaries) return;
    var full = boundaries.districts.viewBox;
    if (kind === "state") return setViewBox(full);
    if (kind === "melbourne") {
      var metro = boundaries.regions.features.filter(function (f) { return METRO.test(f.name); });
      var b = [Infinity, Infinity, -Infinity, -Infinity];
      metro.forEach(function (f) {
        b[0] = Math.min(b[0], f.bbox[0]); b[1] = Math.min(b[1], f.bbox[1]);
        b[2] = Math.max(b[2], f.bbox[2]); b[3] = Math.max(b[3], f.bbox[3]);
      });
      return setViewBox([b[0], b[1], b[2] - b[0], b[3] - b[1]]);
    }
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

  function renderDetail(shown) {
    var chamberKey = layerKey === "regions" ? "upper" : "lower";
    var key = layerKey + "|" + selected + "|" + shown.filter(function (r) {
      return r.seat === selected && r.chamber === chamberKey;
    }).map(function (r) { return r.name; }).join(",");
    if (key === detailKey) return;
    detailKey = key;
    els.mapDetail.replaceChildren();
    if (!selected) {
      els.mapDetail.appendChild(el("p", "meta", "Tap or click an area on the map, or pick a seat from the list below."));
      return;
    }
    var chamber = layerKey === "regions" ? "upper" : "lower";
    var label = chamber === "upper" ? " Region" : " District";
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

  function renderMap(shown) {
    lastShown = shown;
    if (!boundaries) return;
    var seat = els.seat.value;
    var seatIsRegion = !!seat && boundaries.regions.features.some(function (f) { return f.name === seat; });
    var newLayer = els.chamber.value === "upper" || seatIsRegion ? "regions" : "districts";
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
      if (!viewBox) setViewBox(boundaries.districts.viewBox);
    }
    var seatChanged = seat !== lastSeatFilter;
    lastSeatFilter = seat;
    if (seat && seatChanged && boundaries[layerKey].features.some(function (f) { return f.name === seat; })) {
      selected = seat;
      var b = bboxOf([seat]);
      if (b) setViewBox([b[0] - b[2] * 0.4, b[1] - b[3] * 0.4, b[2] * 1.8, b[3] * 1.8]);
    }

    var chamber = layerKey === "regions" ? "upper" : "lower";
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

    var councilMatches = shown.filter(function (r) { return r.chamber === "upper"; }).length;
    els.mapLayer.textContent = chamber === "upper"
      ? "Showing the 8 Legislative Council regions. Each region elects 5 members." +
        (filtering ? " Highlighted regions match your filters." : "")
      : "Showing the 88 Legislative Assembly districts." +
        (filtering ? " Highlighted districts match your filters." : "") +
        (els.chamber.value ? "" : (filtering && councilMatches
          ? " " + councilMatches + " matching Legislative Council member" + (councilMatches > 1 ? "s are" : " is") +
            " not shown here: choose Legislative Council under Chamber to see regions."
          : " Choose Legislative Council under Chamber to see regions."));

    var names = boundaries[layerKey].features.map(function (f) { return f.name; })
      .filter(function (n) { return matchSeats[n]; });
    els.seatCount.textContent = String(names.length);
    var frag = document.createDocumentFragment();
    names.forEach(function (n) {
      var li = document.createElement("li");
      var b = el("button", "seat-btn", n);
      b.type = "button";
      if (n === selected) b.setAttribute("aria-current", "true");
      b.dataset.name = n;
      b.addEventListener("click", function () {
        select(n, true);
        var again = els.seatButtons.querySelector('[data-name="' + CSS.escape(n) + '"]');
        if (again) again.focus();
      });
      li.appendChild(b);
      frag.appendChild(li);
    });
    els.seatButtons.replaceChildren(frag);
    renderDetail(shown);
  }

  /* Drag to move, pinch (or ctrl + scroll / trackpad pinch) to zoom. */
  var pointers = {};       // pointerId -> {x, y}
  var gesture = null;      // {vb, x, y, dist, moved}
  var suppressClick = false;

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
    gesture = { vb: viewBox.slice(), x: cx, y: cy, dist: dist, k: unitsPerPx(), moved: gesture ? gesture.moved : false };
  }

  els.map.addEventListener("pointerdown", function (e) {
    if (!boundaries || (e.pointerType === "mouse" && e.button !== 0)) return;
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
    try { els.map.setPointerCapture(e.pointerId); } catch (err) { /* ignore */ }
    if (Object.keys(pointers).length === 1) gesture = null;
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
    if (gesture && gesture.moved) suppressClick = true;
    if (Object.keys(pointers).length) startGesture(); else gesture = null;
  }
  els.map.addEventListener("pointerup", endPointer);
  els.map.addEventListener("pointercancel", endPointer);
  els.map.addEventListener("wheel", function (e) {
    if (!boundaries || !e.ctrlKey) return;  // plain scroll keeps scrolling the page
    e.preventDefault();
    zoomAround(e.clientX, e.clientY, Math.exp(e.deltaY * 0.01));
  }, { passive: false });

  els.map.addEventListener("click", function (e) {
    if (suppressClick) { suppressClick = false; return; }
    // pointer capture makes the SVG the click target, so find the area under the pointer
    var hit = document.elementFromPoint(e.clientX, e.clientY);
    var p = hit && hit.closest && hit.closest("path.seat");
    if (p) select(p.dataset.name, false);
  });
  els.mapView.querySelectorAll("[data-zoom]").forEach(function (b) {
    b.addEventListener("click", function () { zoomTo(b.dataset.zoom); });
  });
  els.viewList.addEventListener("click", function () { setView("list", false); });
  els.viewMap.addEventListener("click", function () { setView("map", false); });

  els.form.addEventListener("input", render);
  els.form.addEventListener("change", render);
  els.form.addEventListener("submit", function (e) { e.preventDefault(); });
  els.form.addEventListener("reset", function () {
    selected = null;
    setTimeout(function () { if (boundaries) setViewBox(boundaries.districts.viewBox); render(); }, 0);
  });
  window.addEventListener("hashchange", function () {
    if (!rows.length) return;
    var want = location.hash === "#map" ? "map" : "list";
    if (want !== view) setView(want, false);
  });

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
