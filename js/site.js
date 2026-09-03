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
  const id = String(space.id || "").replace(/^#/, "").toUpperCase();
  const note = String(space.note || "").toLowerCase();
  return note.indexOf("outlot") !== -1 || id.indexOf("OP") === 0;
}

function sbAvailabilityLabel(property) {
  if (!property.availableSpaces) return "Fully leased";
  const listings = property.spaces || [];
  const outlots = listings.filter(sbIsOutlot);
  const suites = listings.filter(function (space) { return !sbIsOutlot(space); });
  const parts = [];
  if (suites.length) {
    const sf = suites.reduce(function (sum, space) { return sum + (space.sf || 0); }, 0);
    const label = suites.length === 1 ? "1 space" : suites.length + " spaces";
    parts.push(label + " · " + sbFormatNumber(sf) + " SF");
  }
  if (outlots.length) {
    parts.push(outlots.length === 1 ? "1 outlot available" : outlots.length + " outlots available");
  }
  return parts.join(" · ") || "Fully leased";
}

function sbCard(property) {
  const href = sbHref("properties/" + encodeURIComponent(property.id) + "/");
  const visual = property.photo
    ? '<a class="card-visual" href="' +
      href +
      '"><img src="' +
      sbHref(property.photo) +
      '" alt="' +
      property.name +
      " in " +
      property.city +
      '" width="800" height="500" loading="lazy"></a>'
    : '<a class="card-visual card-visual--type" href="' +
      href +
      '"><span class="mono-state">' +
      property.state +
      '</span><span class="mono-city">' +
      property.city +
      "</span></a>";

  return (
    '<article class="property-card">' +
    visual +
    '<div class="card-body"><h3><a href="' +
    href +
    '">' +
    property.name +
    '</a></h3><p class="place">' +
    property.city +
    '</p><p class="card-meta">' +
    sbAvailabilityLabel(property) +
    '</p><a class="view" href="' +
    href +
    '">View</a></div></article>'
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
