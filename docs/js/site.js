(function () {
  const yearEl = document.querySelector("[data-year]");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  const toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      document.body.classList.toggle("nav-open");
    });
  }

  document.querySelectorAll("[data-mailto-form]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      const data = new FormData(form);
      const to = form.getAttribute("data-to") || "leasing@bearsmgmt.com";
      const subject = data.get("_subject") || "Website inquiry";
      const lines = [];
      data.forEach(function (value, key) {
        if (key === "_subject") return;
        lines.push(key + ": " + value);
      });
      const href =
        "mailto:" +
        to +
        "?subject=" +
        encodeURIComponent(subject) +
        "&body=" +
        encodeURIComponent(lines.join("\n"));
      window.location.href = href;
    });
  });

  const params = new URLSearchParams(window.location.search);
  const prefill = document.querySelector("[name='Property']");
  if (prefill && params.get("property")) {
    prefill.value = params.get("property");
  }
})();

function sbHref(path) {
  var parts = location.pathname.replace(/\/+$/, "").split("/").filter(Boolean);
  if (parts[0] === "silverbears") parts.shift();
  var depth = parts.length;
  if (depth && /\.html$/i.test(parts[depth - 1])) depth -= 1;
  var prefix = depth ? "../".repeat(depth) : "";
  return prefix + path;
}

function sbFormatNumber(n) {
  return Number(n).toLocaleString("en-US");
}

function sbIsOutlot(space) {
  var sid = String((space && space.id) || "").replace(/^#/, "").toUpperCase();
  var note = String((space && space.note) || "").toLowerCase();
  return note.indexOf("outlot") !== -1 || sid.indexOf("OP") === 0;
}

function sbAvailability(property) {
  if (!property.availableSpaces) return "Fully leased";
  var spaces = property.spaces || [];
  var outlots = spaces.filter(sbIsOutlot);
  var suites = spaces.filter(function (space) { return !sbIsOutlot(space); });
  var parts = [];
  if (suites.length) {
    var sf = suites.reduce(function (sum, space) { return sum + (Number(space.sf) || 0); }, 0);
    var label = suites.length === 1 ? "1 space" : suites.length + " spaces";
    parts.push(label + " · " + sbFormatNumber(sf) + " SF");
  }
  if (outlots.length) {
    parts.push(outlots.length === 1 ? "1 outlot available" : outlots.length + " outlots available");
  }
  return parts.length ? parts.join(" · ") : "Fully leased";
}

function sbCardLine(property) {
  if (!property.availableSpaces) return "Fully leased";
  return property.availableSpaces + " / " + sbFormatNumber(property.availableSf) + " SF";
}

function sbCard(property) {
  const href = sbHref("properties/" + encodeURIComponent(property.id) + "/");
  return (
    '<article class="property-card">' +
    "<h3><a href=\"" +
    href +
    '">' +
    property.name +
    '</a></h3><p class="card-meta">' +
    sbCardLine(property) +
    '</p><p class="place">' +
    property.city +
    '</p><a class="view" href="' +
    href +
    '">View</a></article>'
  );
}

function sbFilterProperties(list, filters) {
  const q = (filters.q || "").trim().toLowerCase();
  return list.filter(function (property) {
    if (filters.state && property.state !== filters.state) return false;
    if (filters.availability === "available" && property.availableSpaces === 0) return false;
    if (filters.availability === "leased" && property.availableSpaces > 0) return false;
    if (q) {
      const hay = [property.name, property.city, property.state, property.stateName, property.address]
        .join(" ")
        .toLowerCase();
      if (hay.indexOf(q) === -1) return false;
    }
    return true;
  });
}

function sbUnique(list, key) {
  return list
    .map(function (item) { return item[key]; })
    .filter(function (value, index, arr) { return arr.indexOf(value) === index; })
    .sort();
}

function sbInitPropertiesPage() {
  const grid = document.querySelector("[data-property-grid]");
  if (!grid || !window.SB_PROPERTIES) return;

  const empty = document.querySelector("[data-empty]");
  const count = document.querySelector("[data-count]");
  const q = document.querySelector("#filter-q");
  const state = document.querySelector("#filter-state");
  const availability = document.querySelector("#filter-availability");

  sbUnique(window.SB_PROPERTIES, "state").forEach(function (code) {
    const opt = document.createElement("option");
    const sample = window.SB_PROPERTIES.find(function (p) { return p.state === code; });
    opt.value = code;
    opt.textContent = sample.stateName + " (" + code + ")";
    state.appendChild(opt);
  });

  function render() {
    const results = sbFilterProperties(window.SB_PROPERTIES, {
      q: q.value,
      state: state.value,
      availability: availability.value
    });

    if (results.length === 0) {
      grid.classList.add("is-hidden");
      grid.innerHTML = "";
      empty.hidden = false;
      count.textContent = "No matching centers";
      return;
    }

    empty.hidden = true;
    grid.classList.remove("is-hidden");
    grid.innerHTML = results.map(sbCard).join("");
    count.textContent =
      results.length +
      (results.length === 1 ? " center" : " centers") +
      (availability.value === "available" ? " with space" : "");
  }

  ["input", "change"].forEach(function (evt) {
    q.addEventListener(evt, render);
    state.addEventListener(evt, render);
    availability.addEventListener(evt, render);
  });

  const params = new URLSearchParams(window.location.search);
  if (params.get("q")) q.value = params.get("q");
  if (params.get("state")) state.value = params.get("state");
  if (params.get("availability")) availability.value = params.get("availability");
  else availability.value = "available";

  const clearBtns = document.querySelectorAll("[data-clear-filters]");
  clearBtns.forEach(function (clearBtn) {
    clearBtn.addEventListener("click", function () {
      q.value = "";
      state.value = "";
      availability.value = "available";
      render();
    });
  });

  render();
}

document.addEventListener("DOMContentLoaded", function () {
  sbInitPropertiesPage();
});
