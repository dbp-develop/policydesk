(function () {
  "use strict";

  var app = document.getElementById("app");
  var btnMap = document.getElementById("btn-map");
  var btnList = document.getElementById("btn-list");
  var members = [];
  var view = "map";

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
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
        "</section>";
      return;
    }

    if (view === "list") {
      app.innerHTML = "<ul>" + members.map(function (m) {
        return "<li>" + esc(m.name) + " (" + esc(m.party) + ")</li>";
      }).join("") + "</ul>";
    } else {
      app.innerHTML = '<p class="muted">Map view coming next.</p>';
    }
  }

  btnMap.addEventListener("click", function () { view = "map"; render(); });
  btnList.addEventListener("click", function () { view = "list"; render(); });

  fetch("data/members.json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      members = Array.isArray(data) ? data : [];
      console.log("Loaded members:", members.length);
      render();
    })
    .catch(function (err) {
      console.error("Could not load members.json", err);
      render();
    });
})();
