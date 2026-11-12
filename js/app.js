(function () {
  "use strict";

  var app = document.getElementById("app");
  var btnMap = document.getElementById("btn-map");
  var btnList = document.getElementById("btn-list");

  var members = [];
  var vacancies = [];
  var boundaries = null;
  var lastUpdated = "";
  var ready = false;

  var view = "map";
  var query = "";
  var chamber = "all";
  var party = "";
  var mapScope = "vic";
  var selectedKey = "";
  var focusDetail = false;
  var focusId = "";

  var memberById = {};
  var memberByElectorate = {};
  var membersByRegion = {};
  var vacancyByKey = {};
  var vacancyByElectorate = {};
  var regionByElectorate = {};
  var regionNameByKey = {};
  var partyFull = {};

  var PARTY_ORDER = ["ALP", "LIB", "NAT", "GRN", "LCV", "AJP", "SFF", "FFV", "ONP", "LIB-TARIAN", "IND", "OTH"];
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function slug(value) {
    return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  function keyForRegion(name) {
    return "region-" + slug(name);
  }

  function keyForVacancy(v) {
    return "vacant-" + slug(v.electorate || v.region || "seat");
  }

  function safeUrl(url) {
    if (typeof url !== "string" || url.indexOf("https://") !== 0 || url.indexOf(" ") !== -1) return "";
    return url;
  }

  function formatDate(iso) {
    if (!iso || String(iso).length < 10) return iso || "";
    var parts = String(iso).slice(0, 10).split("-");
    var month = MONTHS[Number(parts[1]) - 1];
    if (!month || !parts[0] || !parts[2]) return String(iso);
    return Number(parts[2]) + " " + month + " " + parts[0];
  }

  function partyRank(code) {
    if (code === "VAC") return 80;
    if (code === "REGION") return 90;
    var index = PARTY_ORDER.indexOf(code);
    return index === -1 ? 50 : index;
  }

  function chamberLabel(value) {
    if (value === "lower" || value === "Assembly") return "Legislative Assembly";
    if (value === "upper" || value === "Council") return "Legislative Council";
    return value || "";
  }

  function matchesQuery(blob) {
    var q = query.trim().toLowerCase();
    if (!q) return true;
    return String(blob || "").toLowerCase().indexOf(q) !== -1;
  }

  function memberBlob(m) {
    var house = m.chamber === "lower" ? "assembly lower" : "council upper";
    return [m.name, m.electorate, m.region, m.party, m.party_short, house].join(" ");
  }

  function memberMatches(m) {
    if (chamber === "lower" && m.chamber !== "lower") return false;
    if (chamber === "upper" && m.chamber !== "upper") return false;
    if (party && m.party_short !== party) return false;
    return matchesQuery(memberBlob(m));
  }

  function vacancyBlob(v) {
    return [v.electorate, v.region, v.reason, v.chamber, "vacant vacancy"].join(" ");
  }

  function vacancyIsLower(v) {
    return v.chamber === "Assembly" || v.chamber === "lower";
  }

  function vacancyMatches(v) {
    if (party) return false;
    if (chamber === "lower" && !vacancyIsLower(v)) return false;
    if (chamber === "upper" && vacancyIsLower(v)) return false;
    return matchesQuery(vacancyBlob(v));
  }

  function filtersActive() {
    return !!(query.trim() || party || chamber !== "all");
  }

  function byName(a, b) {
    return a.name.localeCompare(b.name, "en");
  }

  function filteredMembers() {
    return members.filter(memberMatches).sort(byName);
  }

  function filteredVacancies() {
    return vacancies.filter(vacancyMatches);
  }

  function countText(matchedMembers, matchedVacancies) {
    var text = matchedMembers.length + " member" + (matchedMembers.length === 1 ? "" : "s");
    if (matchedVacancies.length) {
      text += " · " + matchedVacancies.length + " vacant";
    }
    return filtersActive() ? text + " match" : "Showing " + text;
  }

  function mapLayer() {
    return chamber === "upper" ? "council" : "assembly";
  }

  function eachRing(geom, fn) {
    if (!geom || !geom.coordinates) return;
    var coords = geom.coordinates;
    var p, r;
    if (geom.type === "Polygon") {
      for (r = 0; r < coords.length; r++) fn(coords[r]);
    } else if (geom.type === "MultiPolygon") {
      for (p = 0; p < coords.length; p++) {
        for (r = 0; r < coords[p].length; r++) fn(coords[p][r]);
      }
    }
  }

  function buildIndexes() {
    memberById = {};
    memberByElectorate = {};
    membersByRegion = {};
    vacancyByKey = {};
    vacancyByElectorate = {};
    regionByElectorate = {};
    regionNameByKey = {};
    partyFull = {};

    members.forEach(function (m) {
      memberById[m.id] = m;
      if (m.electorate) memberByElectorate[m.electorate] = m;
      if (m.region) {
        if (!membersByRegion[m.region]) membersByRegion[m.region] = [];
        membersByRegion[m.region].push(m);
        regionNameByKey[keyForRegion(m.region)] = m.region;
      }
      if (m.party_short && !partyFull[m.party_short]) partyFull[m.party_short] = m.party;
    });

    vacancies.forEach(function (v) {
      var key = keyForVacancy(v);
      vacancyByKey[key] = v;
      if (v.electorate) vacancyByElectorate[v.electorate] = v;
    });

    var assembly = boundaries && boundaries.assembly ? boundaries.assembly.features || [] : [];
    assembly.forEach(function (f) {
      var name = f.properties && f.properties.name;
      var region = f.properties && f.properties.region;
      if (name && region) regionByElectorate[name] = region;
      if (region) regionNameByKey[keyForRegion(region)] = region;
    });

    var council = boundaries && boundaries.council ? boundaries.council.features || [] : [];
    council.forEach(function (f) {
      var name = f.properties && f.properties.name;
      if (name) regionNameByKey[keyForRegion(name)] = name;
    });
  }

  function currentHashKey() {
    var raw = location.hash.replace(/^#/, "");
    if (!raw) return "";
    try {
      return decodeURIComponent(raw);
    } catch (err) {
      return raw;
    }
  }

  function isKnown(key) {
    return !!(memberById[key] || vacancyByKey[key] || regionNameByKey[key]);
  }

  function syncHash() {
    var current = currentHashKey();
    if (selectedKey) {
      if (current !== selectedKey) {
        history.replaceState(null, "", "#" + encodeURIComponent(selectedKey));
      }
    } else if (location.hash) {
      history.replaceState(null, "", location.pathname + location.search);
    }
  }

  function updateTitle() {
    var member = memberById[selectedKey];
    var vacancy = vacancyByKey[selectedKey];
    var region = regionNameByKey[selectedKey];
    if (member) document.title = member.name + " · Policy Desk AU";
    else if (vacancy) document.title = (vacancy.electorate || vacancy.region || "Vacant seat") + " · Policy Desk AU";
    else if (region) document.title = region + " · Policy Desk AU";
    else document.title = "Policy Desk AU";
  }

  function featureKey(feature, layer) {
    var name = feature.properties.name;
    if (layer === "council") return keyForRegion(name);
    if (memberByElectorate[name]) return memberByElectorate[name].id;
    if (vacancyByElectorate[name]) return keyForVacancy(vacancyByElectorate[name]);
    return "";
  }

  function featureLabel(feature, layer) {
    var name = feature.properties.name;
    if (layer === "council") {
      var people = membersByRegion[name] || [];
      return name + ", " + people.length + " Council members";
    }
    var member = memberByElectorate[name];
    if (member) return name + ", " + member.name + ", " + member.party;
    if (vacancyByElectorate[name]) return name + ", vacant";
    return name;
  }

  function featureMatches(feature, layer) {
    if (layer === "council") {
      var people = membersByRegion[feature.properties.name] || [];
      for (var i = 0; i < people.length; i++) {
        if (memberMatches(people[i])) return true;
      }
      return false;
    }
    var name = feature.properties.name;
    if (memberByElectorate[name]) return memberMatches(memberByElectorate[name]);
    if (vacancyByElectorate[name]) return vacancyMatches(vacancyByElectorate[name]);
    return false;
  }

  function featureSelected(feature, layer) {
    var key = featureKey(feature, layer);
    if (key && key === selectedKey) return true;
    var member = memberById[selectedKey];
    if (layer === "council" && member && member.region === feature.properties.name) return true;
    if (layer === "assembly" && regionNameByKey[selectedKey] && feature.properties.region === regionNameByKey[selectedKey]) {
      return true;
    }
    return false;
  }

  function isMetro(feature) {
    var region = (feature.properties && (feature.properties.region || feature.properties.name)) || "";
    return region.indexOf("Metropolitan") !== -1;
  }

  function boundsOf(features) {
    var bounds = { minLon: 180, maxLon: -180, minLat: 90, maxLat: -90 };
    var any = false;
    features.forEach(function (feature) {
      eachRing(feature.geometry, function (ring) {
        for (var i = 0; i < ring.length; i++) {
          var x = Number(ring[i][0]);
          var y = Number(ring[i][1]);
          if (x !== x || y !== y) continue;
          if (x < bounds.minLon) bounds.minLon = x;
          if (x > bounds.maxLon) bounds.maxLon = x;
          if (y < bounds.minLat) bounds.minLat = y;
          if (y > bounds.maxLat) bounds.maxLat = y;
          any = true;
        }
      });
    });
    if (!any) return null;
    var dx = (bounds.maxLon - bounds.minLon) * 0.04 || 0.1;
    var dy = (bounds.maxLat - bounds.minLat) * 0.04 || 0.1;
    return {
      minLon: bounds.minLon - dx,
      maxLon: bounds.maxLon + dx,
      minLat: bounds.minLat - dy,
      maxLat: bounds.maxLat + dy
    };
  }

  function makeProjector(bounds) {
    var mid = ((bounds.minLat + bounds.maxLat) / 2) * Math.PI / 180;
    var cos = Math.cos(mid) || 1;
    var x0 = bounds.minLon * cos;
    var geoW = (bounds.maxLon - bounds.minLon) * cos || 1;
    var geoH = bounds.maxLat - bounds.minLat || 1;
    var width = 1000;
    var pad = 14;
    var usable = width - pad * 2;
    var scale = usable / geoW;
    var height = Math.round(pad * 2 + geoH * scale);
    return {
      width: width,
      height: height,
      project: function (lon, lat) {
        return [pad + (lon * cos - x0) * scale, pad + (bounds.maxLat - lat) * scale];
      }
    };
  }

  function ringPath(ring, project) {
    var cmds = [];
    for (var i = 0; i < ring.length; i++) {
      var point = project(Number(ring[i][0]), Number(ring[i][1]));
      var x = Math.round(point[0] * 10) / 10;
      var y = Math.round(point[1] * 10) / 10;
      if (x !== x || y !== y) continue;
      cmds.push((cmds.length ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1));
    }
    if (!cmds.length) return "";
    cmds.push("Z");
    return cmds.join("");
  }

  function geometryPath(geom, project) {
    var parts = [];
    eachRing(geom, function (ring) {
      var path = ringPath(ring, project);
      if (path) parts.push(path);
    });
    return parts.join("");
  }

  function emptyDetail() {
    var lower = members.filter(function (m) { return m.chamber === "lower"; }).length;
    var upper = members.length - lower;
    var vacant = vacancies.length;
    return (
      '<article class="detail detail-empty">' +
      '<h2 id="detail-title">Victorian directory</h2>' +
      '<p class="muted">Search by name, seat or party. On the map, choose a district. Profiles link to parliament.vic.gov.au.</p>' +
      '<p class="muted">' + lower + " Assembly members, " + upper + " Council members" +
      (vacant ? ", " + vacant + " vacant Assembly seat" : "") + ".</p>" +
      "</article>"
    );
  }

  function memberDetail(m) {
    var seat = m.chamber === "lower" ? m.electorate : m.region;
    var seatLabel = m.chamber === "lower" ? "Electorate" : "Region";
    var region = m.chamber === "lower" ? regionByElectorate[m.electorate] : "";
    var url = safeUrl(m.official_url);
    var html = '<article class="detail">';
    html += '<p class="kicker">' + esc(chamberLabel(m.chamber)) + "</p>";
    html += '<h2 id="detail-title">' + esc(m.name) + "</h2>";
    html += '<p class="party-line"><span class="swatch" data-party="' + esc(m.party_short) + '"></span>' + esc(m.party) + "</p>";
    html += "<dl>";
    html += "<div><dt>" + seatLabel + "</dt><dd>";
    if (m.chamber === "upper" && m.region) {
      html += '<button type="button" class="text-btn" data-key="' + esc(keyForRegion(m.region)) + '">' + esc(m.region) + "</button>";
    } else {
      html += esc(seat || "");
    }
    html += "</dd></div>";
    if (region) {
      html += '<div><dt>Council region</dt><dd><button type="button" class="text-btn" data-key="' + esc(keyForRegion(region)) + '">' + esc(region) + "</button></dd></div>";
    }
    html += "<div><dt>Updated</dt><dd>" + esc(formatDate(m.last_updated)) + "</dd></div>";
    html += "</dl>";
    if (url) {
      html += '<p class="detail-link"><a class="official" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">Official profile<span class="visually-hidden"> (opens in a new tab)</span></a></p>';
    }
    html += '<p class="source">Source: ' + esc(m.source || "Parliament of Victoria") + "</p>";
    html += "</article>";
    return html;
  }

  function vacancyDetail(v) {
    var name = v.electorate || v.region || "Vacant seat";
    var region = v.electorate ? regionByElectorate[v.electorate] : "";
    var html = '<article class="detail">';
    html += '<p class="kicker">' + esc(chamberLabel(v.chamber)) + "</p>";
    html += '<h2 id="detail-title">' + esc(name) + "</h2>";
    html += '<p class="party-line"><span class="swatch" data-party="VAC"></span>Vacant</p>';
    html += "<dl>";
    html += "<div><dt>Status</dt><dd>" + esc(v.reason || "Vacant") + "</dd></div>";
    if (region) {
      html += '<div><dt>Council region</dt><dd><button type="button" class="text-btn" data-key="' + esc(keyForRegion(region)) + '">' + esc(region) + "</button></dd></div>";
    }
    html += "</dl>";
    html += '<p class="source">No current member is listed by the Parliament of Victoria.</p>';
    html += "</article>";
    return html;
  }

  function regionDetail(name) {
    var people = (membersByRegion[name] || []).slice().sort(byName);
    var html = '<article class="detail">';
    html += '<p class="kicker">Legislative Council</p>';
    html += '<h2 id="detail-title">' + esc(name) + "</h2>";
    html += '<p class="muted">' + people.length + (people.length === 1 ? " member" : " members") + " share this region.</p>";
    html += '<ul class="region-members">';
    people.forEach(function (m) {
      var dim = filtersActive() && !memberMatches(m) ? " dim" : "";
      var current = m.id === selectedKey ? " selected" : "";
      html += '<li><button type="button" class="member-row' + dim + current + '" data-key="' + esc(m.id) + '" data-party="' + esc(m.party_short) + '">';
      html += '<span class="swatch" data-party="' + esc(m.party_short) + '"></span>';
      html += '<span class="member-name">' + esc(m.name) + "</span>";
      html += '<span class="member-meta">' + esc(m.party_short) + "</span>";
      html += "</button></li>";
    });
    html += "</ul></article>";
    return html;
  }

  function detailHtml() {
    if (memberById[selectedKey]) return memberDetail(memberById[selectedKey]);
    if (vacancyByKey[selectedKey]) return vacancyDetail(vacancyByKey[selectedKey]);
    if (regionNameByKey[selectedKey]) return regionDetail(regionNameByKey[selectedKey]);
    return emptyDetail();
  }

  function rowHtml(key, partyCode, name, meta, selected) {
    return (
      '<li><button type="button" class="member-row' + (selected ? " selected" : "") + '" data-key="' + esc(key) + '" data-party="' + esc(partyCode) + '"' +
      (selected ? ' aria-current="true"' : "") + ">" +
      '<span class="swatch" data-party="' + esc(partyCode) + '"></span>' +
      '<span class="member-name">' + esc(name) + "</span>" +
      '<span class="member-meta">' + esc(meta) + "</span>" +
      "</button></li>"
    );
  }

  function listHtml(matchedMembers, matchedVacancies) {
    if (!matchedMembers.length && !matchedVacancies.length) {
      return '<div class="list-wrap"><p class="empty">No members match that search.</p></div>';
    }
    var html = '<div class="list-wrap"><ul class="member-list">';
    matchedVacancies.forEach(function (v) {
      var key = keyForVacancy(v);
      var name = v.electorate || v.region || "Vacant seat";
      html += rowHtml(key, "VAC", name, "Vacant · " + chamberLabel(v.chamber), key === selectedKey);
    });
    matchedMembers.forEach(function (m) {
      var seat = m.chamber === "lower" ? m.electorate : m.region;
      html += rowHtml(m.id, m.party_short, m.name, (seat || "") + " · " + m.party_short, m.id === selectedKey);
    });
    html += "</ul></div>";
    return html;
  }

  function banner(message, nextChamber, label) {
    return (
      '<p class="map-banner">' + esc(message) +
      ' <button type="button" class="text-btn" data-set-chamber="' + esc(nextChamber) + '">' + esc(label) + "</button></p>"
    );
  }

  function selectionBanner() {
    if (view !== "map" || !boundaries) return "";
    var member = memberById[selectedKey];
    if (!member) return "";
    if (mapLayer() === "assembly" && member.chamber === "upper") {
      return banner(member.name + " sits in the Legislative Council.", "upper", "Show Council regions");
    }
    if (mapLayer() === "council" && member.chamber === "lower") {
      return banner(member.name + " sits in the Legislative Assembly.", "all", "Show Assembly districts");
    }
    return "";
  }

  function hiddenBanner() {
    if (view !== "map" || !boundaries || !(query.trim() || party)) return "";
    var layer = mapLayer();
    var hiddenMembers = 0;
    members.forEach(function (m) {
      if (party && m.party_short !== party) return;
      if (!matchesQuery(memberBlob(m))) return;
      if (layer === "assembly" && m.chamber === "upper") hiddenMembers++;
      if (layer === "council" && m.chamber === "lower") hiddenMembers++;
    });
    var hiddenVacant = 0;
    if (layer === "council") {
      vacancies.forEach(function (v) {
        if (!party && matchesQuery(vacancyBlob(v))) hiddenVacant++;
      });
    }
    var hidden = hiddenMembers + hiddenVacant;
    if (!hidden) return "";
    if (layer === "assembly") {
      return banner(
        hidden + " Council member" + (hidden === 1 ? "" : "s") + " also match.",
        "upper",
        "Show Council regions"
      );
    }
    return banner(
      hidden + " Assembly result" + (hidden === 1 ? "" : "s") + " also match.",
      "all",
      "Show Assembly districts"
    );
  }

  function legendHtml(features, layer) {
    var html = '<ul class="legend">';
    if (layer === "council") {
      html += '<li><span class="swatch" data-party="REGION"></span>Council region</li></ul>';
      return html;
    }
    var seen = {};
    var codes = [];
    features.forEach(function (feature) {
      var key = featureKey(feature, layer);
      var code = "";
      if (memberById[key]) code = memberById[key].party_short;
      else if (vacancyByKey[key]) code = "VAC";
      if (!code || seen[code]) return;
      seen[code] = true;
      codes.push(code);
    });
    codes.sort(function (a, b) { return partyRank(a) - partyRank(b); });
    codes.forEach(function (code) {
      var name = code === "VAC" ? "Vacant" : (partyFull[code] || code);
      var shortLabel = code === "VAC" ? "Vacant" : code;
      html += '<li title="' + esc(name) + '"><span class="swatch" data-party="' + esc(code) + '"></span><span>' + esc(shortLabel) + "</span>";
      if (name !== shortLabel) html += '<span class="legend-full">' + esc(name) + "</span>";
      html += "</li>";
    });
    html += "</ul>";
    return html;
  }

  function mapHtml() {
    if (!boundaries) {
      return '<div class="map-card"><p class="muted">The electorate map is unavailable. The list still has every current member.</p></div>';
    }
    var layer = mapLayer();
    var all = layer === "council"
      ? (boundaries.council.features || [])
      : (boundaries.assembly.features || []);
    var framed = all;
    if (mapScope === "melbourne") {
      framed = all.filter(isMetro);
      if (!framed.length) framed = all;
    }
    var bounds = boundsOf(framed);
    if (!bounds) {
      return '<div class="map-card"><p class="muted">The electorate map could not be drawn.</p></div>';
    }
    var projector = makeProjector(bounds);
    var paths = "";
    var drawn = [];
    all.forEach(function (feature) {
      if (mapScope === "melbourne" && !isMetro(feature)) return;
      if (!overlapsFrame(feature, bounds)) return;
      var d = geometryPath(feature.geometry, projector.project);
      if (!d) return;
      var key = featureKey(feature, layer);
      var code = "OTH";
      if (layer === "council") code = "REGION";
      else if (memberById[key]) code = memberById[key].party_short || "OTH";
      else if (vacancyByKey[key]) code = "VAC";
      var classes = "district";
      if (featureSelected(feature, layer)) classes += " selected";
      if (filtersActive() && !featureMatches(feature, layer)) classes += " dim";
      paths += '<path class="' + classes + '" data-party="' + esc(code) + '" data-key="' + esc(key) + '" tabindex="0" role="button" aria-label="' + esc(featureLabel(feature, layer)) + '" d="' + d + '"><title>' + esc(featureLabel(feature, layer)) + "</title></path>";
      drawn.push(feature);
    });

    var caption = layer === "council" ? "Legislative Council regions" : "Legislative Assembly districts";
    var hint = mapScope === "vic" && layer === "assembly"
      ? '<p class="map-hint muted">City districts are easier to open on the Melbourne view.</p>'
      : "";
    var creditUrl = safeUrl(boundaries.source_url);
    var credit = esc(boundaries.attribution || "State of Victoria (Victorian Electoral Commission), CC BY 4.0.");
    if (creditUrl) {
      credit = '<a href="' + esc(creditUrl) + '">' + credit + "</a>";
    }

    return (
      '<div class="map-card">' +
      '<div class="map-toolbar">' +
      '<p class="map-caption">' + caption + "</p>" +
      '<div class="scope-toggle" role="group" aria-label="Map area">' +
      '<button type="button" id="scope-vic" data-scope="vic" aria-pressed="' + (mapScope === "vic" ? "true" : "false") + '">Victoria</button>' +
      '<button type="button" id="scope-melbourne" data-scope="melbourne" aria-pressed="' + (mapScope === "melbourne" ? "true" : "false") + '">Melbourne</button>' +
      "</div></div>" +
      hint +
      (selectionBanner() || hiddenBanner()) +
      '<svg class="map-svg" viewBox="0 0 ' + projector.width + " " + projector.height + '" role="group" aria-label="' + caption + '">' +
      "<defs><pattern id=\"vacant-fill\" width=\"8\" height=\"8\" patternUnits=\"userSpaceOnUse\">" +
      '<rect width="8" height="8" fill="#f4a300"/>' +
      '<path d="M-2 2 L2 -2 M0 8 L8 0 M6 10 L10 6" stroke="#14213d" stroke-width="1.2"/>' +
      "</pattern></defs>" +
      paths +
      "</svg>" +
      legendHtml(drawn, layer) +
      '<p class="map-credit">Boundaries: ' + credit + " CC BY 4.0.</p>" +
      "</div>"
    );
  }

  function renderResults() {
    var listEl = document.querySelector(".list-wrap");
    var listScroll = listEl ? listEl.scrollTop : 0;
    var matchedMembers = filteredMembers();
    var matchedVacancies = filteredVacancies();
    var count = document.getElementById("count");
    if (count) count.textContent = countText(matchedMembers, matchedVacancies);
    var workspace = document.getElementById("workspace");
    if (!workspace) return;
    workspace.className = "workspace " + (view === "map" ? "map-view" : "list-view");
    workspace.innerHTML = view === "map"
      ? mapHtml() + detailHtml()
      : detailHtml() + listHtml(matchedMembers, matchedVacancies);
    var nextList = document.querySelector(".list-wrap");
    if (nextList) nextList.scrollTop = listScroll;
    bindWorkspace(workspace);
    updateTitle();
    if (focusDetail) {
      var title = document.getElementById("detail-title");
      if (title) {
        title.setAttribute("tabindex", "-1");
        title.focus();
      }
      focusDetail = false;
      focusId = "";
    } else if (focusId) {
      var el = document.getElementById(focusId);
      if (el) el.focus();
      focusId = "";
    }
  }

  function bindWorkspace(workspace) {
    var keyed = workspace.querySelectorAll("[data-key]");
    for (var i = 0; i < keyed.length; i++) {
      keyed[i].addEventListener("click", onPick);
      if (keyed[i].tagName.toLowerCase() === "path") {
        keyed[i].addEventListener("keydown", onPathKey);
      }
    }
    var scopes = workspace.querySelectorAll("[data-scope]");
    for (var s = 0; s < scopes.length; s++) {
      scopes[s].addEventListener("click", onScope);
    }
    var chambers = workspace.querySelectorAll("[data-set-chamber]");
    for (var c = 0; c < chambers.length; c++) {
      chambers[c].addEventListener("click", onSetChamber);
    }
  }

  function onPick(event) {
    var key = event.currentTarget.getAttribute("data-key");
    if (!key) return;
    selectedKey = key;
    if (view === "map" && regionNameByKey[key] && !memberById[key] && !vacancyByKey[key]) {
      chamber = "upper";
      var select = document.getElementById("chamber");
      if (select) select.value = chamber;
    }
    if (!selectionIsMetro(key)) mapScope = "vic";
    focusDetail = true;
    syncHash();
    renderResults();
  }

  function selectionIsMetro(key) {
    var member = memberById[key];
    var vacancy = vacancyByKey[key];
    var seat = "";
    if (member && member.chamber === "lower") seat = member.electorate || "";
    else if (vacancy && vacancy.electorate) seat = vacancy.electorate;
    if (seat) return (regionByElectorate[seat] || "").indexOf("Metropolitan") !== -1;
    if (regionNameByKey[key]) return regionNameByKey[key].indexOf("Metropolitan") !== -1;
    if (member && member.region) return member.region.indexOf("Metropolitan") !== -1;
    return true;
  }

  function overlapsFrame(feature, bounds) {
    var minLon = 180;
    var maxLon = -180;
    var minLat = 90;
    var maxLat = -90;
    var any = false;
    eachRing(feature.geometry, function (ring) {
      for (var i = 0; i < ring.length; i++) {
        var x = Number(ring[i][0]);
        var y = Number(ring[i][1]);
        if (x !== x || y !== y) continue;
        any = true;
        if (x < minLon) minLon = x;
        if (x > maxLon) maxLon = x;
        if (y < minLat) minLat = y;
        if (y > maxLat) maxLat = y;
      }
    });
    if (!any) return false;
    return !(maxLon < bounds.minLon || minLon > bounds.maxLon || maxLat < bounds.minLat || minLat > bounds.maxLat);
  }

  function onPathKey(event) {
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    event.currentTarget.click();
  }

  function onScope(event) {
    mapScope = event.currentTarget.getAttribute("data-scope") || "vic";
    focusId = mapScope === "melbourne" ? "scope-melbourne" : "scope-vic";
    renderResults();
  }

  function onSetChamber(event) {
    chamber = event.currentTarget.getAttribute("data-set-chamber") || "all";
    var select = document.getElementById("chamber");
    if (select) select.value = chamber;
    focusId = "chamber";
    renderResults();
  }

  function setView(next) {
    view = next;
    btnMap.classList.toggle("active", view === "map");
    btnList.classList.toggle("active", view === "list");
    btnMap.setAttribute("aria-pressed", view === "map" ? "true" : "false");
    btnList.setAttribute("aria-pressed", view === "list" ? "true" : "false");
    if (ready) renderResults();
  }

  function partyOptions() {
    var codes = Object.keys(partyFull);
    codes.sort(function (a, b) {
      var rank = partyRank(a) - partyRank(b);
      return rank || a.localeCompare(b);
    });
    var html = '<option value="">All parties</option>';
    codes.forEach(function (code) {
      var total = members.filter(function (m) { return m.party_short === code; }).length;
      html += '<option value="' + esc(code) + '">' + esc(partyFull[code]) + " (" + total + ")</option>";
    });
    return html;
  }

  function renderShell() {
    var updated = lastUpdated ? " · updated " + formatDate(lastUpdated) : "";
    app.innerHTML =
      '<section class="directory">' +
      '<h2 class="visually-hidden">Victorian members</h2>' +
      '<p class="scope-line">Victoria · current parliament' + esc(updated) + "</p>" +
      '<div class="toolbar">' +
      '<label class="field search" for="q">Search' +
      '<input id="q" type="search" placeholder="Name, seat or party" autocomplete="off">' +
      "</label>" +
      '<label class="field" for="chamber">Chamber' +
      '<select id="chamber">' +
      '<option value="all"' + (chamber === "all" ? " selected" : "") + ">All</option>" +
      '<option value="lower"' + (chamber === "lower" ? " selected" : "") + ">Assembly</option>" +
      '<option value="upper"' + (chamber === "upper" ? " selected" : "") + ">Council</option>" +
      "</select></label>" +
      '<label class="field" for="party">Party' +
      '<select id="party">' + partyOptions() + "</select></label>" +
      '<p class="count" id="count" aria-live="polite"></p>' +
      "</div>" +
      '<div id="workspace"></div>' +
      "</section>";

    document.getElementById("q").addEventListener("input", function (event) {
      query = event.target.value;
      renderResults();
    });
    document.getElementById("q").addEventListener("keydown", function (event) {
      if (event.key !== "Enter") return;
      var foundMembers = filteredMembers();
      var foundVacancies = filteredVacancies();
      if (foundMembers.length + foundVacancies.length !== 1) return;
      event.preventDefault();
      selectedKey = foundMembers.length ? foundMembers[0].id : keyForVacancy(foundVacancies[0]);
      if (!selectionIsMetro(selectedKey)) mapScope = "vic";
      focusDetail = true;
      syncHash();
      renderResults();
    });
    document.getElementById("chamber").addEventListener("change", function (event) {
      chamber = event.target.value;
      renderResults();
    });
    document.getElementById("party").addEventListener("change", function (event) {
      party = event.target.value;
      renderResults();
    });
    renderResults();
  }

  function vacancyNote() {
    if (!vacancies.length) return "";
    return (
      '<ul class="vacancy-list">' +
      vacancies.map(function (v) {
        var seat = v.electorate || v.region || "Unknown seat";
        return "<li class=\"muted\">Vacant: " + esc(seat) + " — " + esc(v.reason || "Vacancy") + "</li>";
      }).join("") +
      "</ul>"
    );
  }

  function showComingSoon() {
    app.innerHTML =
      '<section class="notice">' +
      "<h2>Victorian MP directory: coming soon</h2>" +
      '<p class="muted">The map and member list launch before the 28 November 2026 election. ' +
      "Every entry will link to official government sources.</p>" +
      vacancyNote() +
      "</section>";
  }

  function showLoadError() {
    app.innerHTML =
      '<section class="notice"><h2>Could not load the directory</h2>' +
      '<p class="muted">Refresh the page to try again.</p></section>';
  }

  function start() {
    buildIndexes();
    var hashKey = currentHashKey();
    if (hashKey && isKnown(hashKey)) {
      selectedKey = hashKey;
      if (memberById[hashKey] && memberById[hashKey].chamber === "upper") chamber = "upper";
      if (regionNameByKey[hashKey] && !memberById[hashKey]) chamber = "upper";
    }
    ready = true;
    if (!members.length) {
      showComingSoon();
      return;
    }
    renderShell();
  }

  btnMap.addEventListener("click", function () { setView("map"); });
  btnList.addEventListener("click", function () { setView("list"); });
  window.addEventListener("hashchange", function () {
    if (!ready) return;
    var key = currentHashKey();
    if (key === selectedKey) return;
    if (key && !isKnown(key)) return;
    selectedKey = key;
    focusDetail = !!key;
    renderResults();
  });

  Promise.all([
    fetch("data/members.json").then(function (r) {
      if (!r.ok) throw new Error("members");
      return r.json();
    }),
    fetch("data/vic_boundaries.json").then(function (r) {
      if (!r.ok) throw new Error("boundaries");
      return r.json();
    }).catch(function (err) {
      console.error("Could not load vic_boundaries.json", err);
      return null;
    })
  ]).then(function (results) {
    var data = results[0];
    boundaries = results[1];
    if (Array.isArray(data)) {
      members = data;
      vacancies = [];
      lastUpdated = "";
    } else if (data && typeof data === "object") {
      members = Array.isArray(data.members) ? data.members : [];
      vacancies = Array.isArray(data.vacancies) ? data.vacancies : [];
      lastUpdated = data.last_updated || "";
    }
    console.log("Loaded members:", members.length, "vacancies:", vacancies.length);
    start();
  }).catch(function (err) {
    console.error("Could not load members.json", err);
    showLoadError();
  });
})();
