(function () {
  "use strict";

  var app = document.getElementById("app");
  var btnMap = document.getElementById("btn-map");
  var btnList = document.getElementById("btn-list");
  var members = [];
  var vacancies = [];
  var view = "map";

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function vacancyNote() {
    if (!vacancies.length) return "";
    return (
      '<ul class="vacancy-list">' +
      vacancies.map(function (v) {
        var seat = v.electorate || v.region || "Unknown seat";
        var chamber = v.chamber || "";
        return (
          '<li class="muted">Vacant: ' +
          esc(seat) +
          (chamber ? " (" + esc(chamber) + ")" : "") +
          " — " +
          esc(v.reason || "Vacancy") +
          "</li>"
        );
      }).join("") +
      "</ul>"
    );
  }

  function render() {
    btnMap.classList.toggle("active", view === "map");
    btnList.classList.toggle("active", view === "list");

    if (members.length === 0) {
      app.innerHTML =
        '<section class="notice">' +
        "<h2>Victorian MP directory: coming soon</h2>" +
        '<p class="muted">The map and member list launch before the 28 November 2026 election. ' +
        "Every entry will link to official government sources.</p>" +
        vacancyNote() +
        "</section>";
      return;
    }

    // Map and list UI not built yet — keep a coming-soon shell and surface vacancies.
    app.innerHTML =
      '<section class="notice">' +
      "<h2>Victorian MP directory: coming soon</h2>" +
      '<p class="muted">Loaded ' +
      members.length +
      " current members. Map and list views are next.</p>" +
      vacancyNote() +
      "</section>";
  }

  btnMap.addEventListener("click", function () { view = "map"; render(); });
  btnList.addEventListener("click", function () { view = "list"; render(); });

  fetch("data/members.json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (Array.isArray(data)) {
        members = data;
        vacancies = [];
      } else if (data && typeof data === "object") {
        members = Array.isArray(data.members) ? data.members : [];
        vacancies = Array.isArray(data.vacancies) ? data.vacancies : [];
      } else {
        members = [];
        vacancies = [];
      }
      console.log("Loaded members:", members.length, "vacancies:", vacancies.length);
      render();
    })
    .catch(function (err) {
      console.error("Could not load members.json", err);
      members = [];
      vacancies = [];
      render();
    });
})();
