/* The Policy Desk AU: Find my seat (postcode → federal + state MPs). Vanilla JS. AGPL-3.0. */
(function () {
  "use strict";

  var INDEX_URL = "data/seat_lookup/index.json";
  var MEMBERS_URL = {
    federal: "data/federal/members.json",
    vic: "data/members.json",
    nsw: "data/nsw/members.json",
    qld: "data/qld/members.json",
    wa: "data/wa/members.json",
    sa: "data/sa/members.json",
    tas: "data/tas/members.json",
    act: "data/act/members.json",
    nt: "data/nt/members.json"
  };
  var STATE_LABEL = {
    VIC: "Victoria",
    NSW: "New South Wales",
    QLD: "Queensland",
    WA: "Western Australia",
    SA: "South Australia",
    TAS: "Tasmania",
    ACT: "Australian Capital Territory",
    NT: "Northern Territory"
  };
  var PARL_LABEL = {
    federal: "Federal",
    vic: "Victoria",
    nsw: "New South Wales",
    qld: "Queensland",
    wa: "Western Australia",
    sa: "South Australia",
    tas: "Tasmania",
    act: "Australian Capital Territory",
    nt: "Northern Territory"
  };

  var form = document.getElementById("find-seat-form");
  var postcodeInput = document.getElementById("find-postcode");
  var suburbField = document.getElementById("find-suburb-field");
  var suburbSelect = document.getElementById("find-suburb");
  var statusEl = document.getElementById("find-seat-status");
  var resultsEl = document.getElementById("find-seat-results");
  if (!form || !postcodeInput || !resultsEl) return;

  var indexPromise = null;
  var indexDoc = null;
  var suburbCache = {};
  var membersCache = {};
  var pendingPostcode = null;

  function fold(s) {
    return String(s || "")
      .toLowerCase()
      .replace(/[’`]/g, "'")
      .replace(/\s+/g, " ")
      .trim();
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function setStatus(msg, isError) {
    statusEl.textContent = msg || "";
    statusEl.classList.toggle("is-error", !!isError);
  }

  function hideResults() {
    resultsEl.hidden = true;
    resultsEl.replaceChildren();
  }

  function loadIndex() {
    if (!indexPromise) {
      indexPromise = fetch(INDEX_URL, { cache: "no-cache" })
        .then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.json();
        })
        .then(function (doc) {
          indexDoc = doc;
          return doc;
        });
    }
    return indexPromise;
  }

  function loadSuburbFile(parliament) {
    if (suburbCache[parliament]) return Promise.resolve(suburbCache[parliament]);
    var rel = indexDoc && indexDoc.suburb_files && indexDoc.suburb_files[parliament];
    if (!rel) return Promise.reject(new Error("No suburb file for " + parliament));
    return fetch(rel, { cache: "no-cache" })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (doc) {
        suburbCache[parliament] = doc;
        return doc;
      });
  }

  function loadMembers(parliament) {
    if (membersCache[parliament]) return Promise.resolve(membersCache[parliament]);
    var url = MEMBERS_URL[parliament];
    if (!url) return Promise.reject(new Error("Unknown parliament " + parliament));
    return fetch(url, { cache: "no-cache" })
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (doc) {
        membersCache[parliament] = doc;
        return doc;
      });
  }

  function membersForSeat(doc, seatName) {
    var want = fold(seatName);
    var people = (doc.members || []).filter(function (m) {
      return m.chamber === "lower" && fold(m.electorate) === want;
    });
    var vacant = (doc.vacancies || []).filter(function (v) {
      var ch = v.chamber;
      var lower = !ch || ch === "lower" || ch === "Assembly" || ch === "House";
      return lower && fold(v.electorate) === want;
    });
    return { members: people, vacancies: vacant };
  }

  function clearSuburb() {
    suburbField.hidden = true;
    suburbSelect.replaceChildren(el("option", null, "Choose a suburb"));
    suburbSelect.value = "";
    suburbSelect.required = false;
  }

  function showSuburbPicker(suburbs) {
    suburbSelect.replaceChildren(el("option", null, "Choose a suburb"));
    suburbs.forEach(function (s) {
      var label = s.name + (s.state ? " (" + s.state + ")" : "");
      var opt = el("option", null, label);
      opt.value = s.parliament + "|" + s.key;
      suburbSelect.appendChild(opt);
    });
    suburbField.hidden = false;
    suburbSelect.required = true;
  }

  function renderLevel(title, parliament, seats, memberDocs) {
    var section = el("section", "find-seat-level");
    section.appendChild(el("h3", null, title));
    if (!seats || !seats.length) {
      section.appendChild(el("p", "find-seat-empty", "Not found for this address."));
      return section;
    }
    seats.forEach(function (seat) {
      var block = el("div", "find-seat-block");
      var heading = el("h4", null, seat.name);
      block.appendChild(heading);
      if (seat.pct != null && seat.pct < 100) {
        block.appendChild(
          el("p", "find-seat-share", "About " + seat.pct + "% of this postcode or suburb (approximate).")
        );
      }
      var found = membersForSeat(memberDocs[parliament], seat.name);
      if (found.vacancies.length && !found.members.length) {
        found.vacancies.forEach(function (v) {
          var p = el("p", "find-seat-member");
          p.appendChild(document.createTextNode("Vacant seat"));
          if (v.reason) {
            p.appendChild(document.createTextNode(" — " + v.reason));
          }
          block.appendChild(p);
        });
      } else if (!found.members.length) {
        block.appendChild(el("p", "find-seat-empty", "Sitting member not found in our directory."));
      } else {
        found.members.forEach(function (m) {
          var p = el("p", "find-seat-member");
          var strong = el("strong", null, m.name);
          p.appendChild(strong);
          if (m.party) p.appendChild(document.createTextNode(" · " + m.party));
          block.appendChild(p);
          if (m.official_url && /^https:\/\//.test(m.official_url)) {
            var a = el("a", "find-seat-profile", "Official profile");
            a.href = m.official_url;
            a.rel = "noopener noreferrer";
            block.appendChild(a);
          }
        });
      }
      var openBtn = el("button", "btn btn-small find-seat-open", "Show in directory");
      openBtn.type = "button";
      openBtn.addEventListener("click", function () {
        if (window.PolicyDeskAU && typeof window.PolicyDeskAU.focusSeat === "function") {
          window.PolicyDeskAU.focusSeat(parliament, seat.name, "lower");
        }
      });
      block.appendChild(openBtn);
      section.appendChild(block);
    });
    return section;
  }

  function renderResults(payload) {
    resultsEl.replaceChildren();
    var where = el("p", "find-seat-where");
    where.textContent = payload.whereLabel;
    resultsEl.appendChild(where);

    if (payload.multiNote) {
      resultsEl.appendChild(el("p", "find-seat-multi", payload.multiNote));
    }

    resultsEl.appendChild(
      renderLevel(
        "Federal — House of Representatives",
        "federal",
        payload.federal,
        payload.docs
      )
    );
    var stateTitle =
      "State or territory — " + (PARL_LABEL[payload.stateParliament] || payload.stateParliament);
    resultsEl.appendChild(
      renderLevel(stateTitle, payload.stateParliament, payload.state, payload.docs)
    );

    resultsEl.hidden = false;
  }

  function resolveUnambiguous(entry) {
    var federal = entry.federal || [];
    var state = entry.state || [];
    if (!federal.length || !state.length) {
      setStatus("Not found: this postcode has an incomplete seat mapping.", true);
      hideResults();
      return;
    }
    var stateParl = state[0].parliament;
    var stateCode = state[0].state;
    Promise.all([loadMembers("federal"), loadMembers(stateParl)])
      .then(function (docs) {
        var docMap = { federal: docs[0] };
        docMap[stateParl] = docs[1];
        setStatus("Found seats for postcode " + pendingPostcode + ".");
        renderResults({
          whereLabel:
            "Postcode " +
            pendingPostcode +
            (stateCode ? " · " + (STATE_LABEL[stateCode] || stateCode) : ""),
          federal: federal,
          state: state.map(function (s) {
            return { name: s.name, pct: s.pct };
          }),
          stateParliament: stateParl,
          docs: docMap,
          multiNote: null
        });
      })
      .catch(function () {
        setStatus("Sorry, member data could not be loaded.", true);
        hideResults();
      });
  }

  function resolveSuburb(parliament, key) {
    loadSuburbFile(parliament)
      .then(function (doc) {
        var rec = doc.suburbs && doc.suburbs[key];
        if (!rec) {
          setStatus("Not found: that suburb is not in the lookup file.", true);
          hideResults();
          return null;
        }
        return Promise.all([loadMembers("federal"), loadMembers(parliament)]).then(function (docs) {
          return { rec: rec, docs: docs, parliament: parliament };
        });
      })
      .then(function (pack) {
        if (!pack) return;
        var rec = pack.rec;
        var federal = rec.federal || [];
        var state = rec.state_seats || [];
        var multi =
          federal.length > 1 || state.length > 1
            ? "This suburb spans more than one seat. Each option is listed with an approximate share. Check the AEC or your state commission for an exact address."
            : null;
        var docMap = { federal: pack.docs[0] };
        docMap[pack.parliament] = pack.docs[1];
        setStatus("Found seats for " + rec.name + ".");
        renderResults({
          whereLabel:
            rec.name +
            ", " +
            (STATE_LABEL[rec.state] || rec.state) +
            " · postcode " +
            pendingPostcode,
          federal: federal,
          state: state,
          stateParliament: pack.parliament,
          docs: docMap,
          multiNote: multi
        });
      })
      .catch(function () {
        setStatus("Sorry, suburb or member data could not be loaded.", true);
        hideResults();
      });
  }

  function onSubmit(ev) {
    ev.preventDefault();
    var raw = String(postcodeInput.value || "").trim();
    if (!/^\d{4}$/.test(raw)) {
      setStatus("Enter a four-digit Australian postcode.", true);
      hideResults();
      clearSuburb();
      return;
    }
    pendingPostcode = raw;
    setStatus("Looking up…");
    hideResults();

    loadIndex()
      .then(function (doc) {
        var entry = doc.postcodes && doc.postcodes[raw];
        if (!entry) {
          clearSuburb();
          setStatus("Not found: no seat mapping for postcode " + raw + ".", true);
          return;
        }
        if (!entry.ambiguous) {
          clearSuburb();
          resolveUnambiguous(entry);
          return;
        }
        var suburbs = entry.suburbs || [];
        if (!suburbs.length) {
          clearSuburb();
          setStatus("Not found: this postcode needs a suburb, but none are listed.", true);
          return;
        }
        showSuburbPicker(suburbs);
        setStatus(
          "Postcode " +
            raw +
            " covers more than one seat. Choose a suburb or locality."
        );
        if (suburbSelect.focus) suburbSelect.focus();
        // If a suburb is already chosen (re-submit), resolve it.
        if (suburbSelect.value) {
          var parts = suburbSelect.value.split("|");
          if (parts.length === 2) resolveSuburb(parts[0], parts[1]);
        }
      })
      .catch(function () {
        clearSuburb();
        setStatus("Sorry, the seat lookup could not be loaded.", true);
      });
  }

  form.addEventListener("submit", onSubmit);
  suburbSelect.addEventListener("change", function () {
    if (!suburbSelect.value || !pendingPostcode) return;
    var parts = suburbSelect.value.split("|");
    if (parts.length !== 2) return;
    setStatus("Looking up…");
    resolveSuburb(parts[0], parts[1]);
  });

  // Warm the index in the background so the first search is quicker.
  loadIndex().catch(function () { /* optional until submit */ });
})();
