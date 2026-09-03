(function () {
  const yearEl = document.querySelector("[data-year]");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  const toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      document.body.classList.toggle("nav-open");
    });
  }

  const form = document.querySelector("[data-mailto-form]");
  if (form) {
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
  }

  const params = new URLSearchParams(window.location.search);
  const prefill = document.querySelector("[name='Property']");
  if (prefill && params.get("property")) {
    prefill.value = params.get("property");
  }
})();

function sbFormatNumber(n) {
  return Number(n).toLocaleString("en-US");
}

function sbAvailabilityLabel(property) {
  if (!property.availableSpaces) return "No current availability";
  const spaces = property.availableSpaces === 1 ? "1 space" : property.availableSpaces + " spaces";
  return spaces + " · " + sbFormatNumber(property.availableSf) + " SF";
}

function sbCard(property) {
  const visual = property.photo
    ? '<div class="card-visual"><img src="' +
      property.photo +
      '" alt="' +
      property.name +
      ' in ' +
      property.city +
      ", " +
      property.state +
      '"><span class="badge' +
      (property.availableSpaces ? "" : " badge-leased") +
      '">' +
      (property.availableSpaces ? "Available" : "Fully leased") +
      "</span></div>"
    : '<div class="card-visual card-visual--type"><span class="badge' +
      (property.availableSpaces ? "" : " badge-leased") +
      '">' +
      (property.availableSpaces ? "Available" : "Fully leased") +
      '</span><span class="mono-state">' +
      property.state +
      '</span><span class="mono-city">' +
      property.city +
      "</span></div>";

  return (
    '<a class="property-card" href="property.html?id=' +
    encodeURIComponent(property.id) +
    '">' +
    visual +
    '<div class="card-body"><div class="place">' +
    property.city +
    ", " +
    property.state +
    "</div><h3>" +
    property.name +
    '</h3><div class="card-meta">' +
    sbAvailabilityLabel(property) +
    "</div></div></a>"
  );
}

function sbFilterProperties(list, filters) {
  const q = (filters.q || "").trim().toLowerCase();
  return list.filter(function (property) {
    if (filters.state && property.state !== filters.state) return false;
    if (filters.city && property.city !== filters.city) return false;
    if (filters.availability === "available" && property.availableSpaces === 0) return false;
    if (filters.availability === "leased" && property.availableSpaces > 0) return false;
    if (filters.size === "lt5" && !(property.availableSpaces > 0 && property.availableSf < 5000)) return false;
    if (filters.size === "5to15" && !(property.availableSpaces > 0 && property.availableSf >= 5000 && property.availableSf <= 15000)) return false;
    if (filters.size === "gt15" && !(property.availableSpaces > 0 && property.availableSf > 15000)) return false;
    if (q) {
      const hay = [property.name, property.city, property.state, property.stateName, property.address]
        .join(" ")
        .toLowerCase();
      if (hay.indexOf(q) === -1) return false;
    }
    return true;
  });
}

function sbRenderFeatured() {
  const root = document.querySelector("[data-featured]");
  if (!root || !window.SB_PROPERTIES) return;
  const featured = (window.SB_FEATURED || []).map(function (id) {
    return window.SB_PROPERTIES.find(function (p) { return p.id === id; });
  }).filter(Boolean);
  root.innerHTML = featured.map(sbCard).join("");
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
  const city = document.querySelector("#filter-city");
  const availability = document.querySelector("#filter-availability");
  const size = document.querySelector("#filter-size");

  sbUnique(window.SB_PROPERTIES, "state").forEach(function (code) {
    const opt = document.createElement("option");
    const sample = window.SB_PROPERTIES.find(function (p) { return p.state === code; });
    opt.value = code;
    opt.textContent = sample.stateName + " (" + code + ")";
    state.appendChild(opt);
  });

  function refreshCities() {
    const current = city.value;
    const source = state.value
      ? window.SB_PROPERTIES.filter(function (p) { return p.state === state.value; })
      : window.SB_PROPERTIES;
    const cities = sbUnique(source, "city");
    city.innerHTML = '<option value="">All cities</option>';
    cities.forEach(function (name) {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      city.appendChild(opt);
    });
    if (cities.indexOf(current) !== -1) city.value = current;
  }

  function render() {
    const results = sbFilterProperties(window.SB_PROPERTIES, {
      q: q.value,
      state: state.value,
      city: city.value,
      availability: availability.value,
      size: size.value
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
      (results.length === window.SB_PROPERTIES.length ? " in the portfolio" : " match these filters");
  }

  ["input", "change"].forEach(function (evt) {
    q.addEventListener(evt, render);
    state.addEventListener(evt, function () {
      refreshCities();
      render();
    });
    city.addEventListener(evt, render);
    availability.addEventListener(evt, render);
    size.addEventListener(evt, render);
  });

  const params = new URLSearchParams(window.location.search);
  if (params.get("q")) q.value = params.get("q");
  if (params.get("state")) state.value = params.get("state");
  if (params.get("availability")) availability.value = params.get("availability");
  if (params.get("size")) size.value = params.get("size");

  const clearBtn = document.querySelector("[data-clear-filters]");
  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      q.value = "";
      state.value = "";
      availability.value = "";
      size.value = "";
      refreshCities();
      city.value = "";
      render();
    });
  }

  refreshCities();
  if (params.get("city")) city.value = params.get("city");
  render();
}

function sbInitPropertyPage() {
  const root = document.querySelector("[data-property-detail]");
  if (!root || !window.SB_PROPERTIES) return;
  const id = new URLSearchParams(window.location.search).get("id");
  const property = window.SB_PROPERTIES.find(function (p) { return p.id === id; });
  if (!property) {
    root.innerHTML =
      '<div class="page-hero"><p class="kicker">Properties</p><h1>Center not found</h1><p class="lede">That listing is not in the current portfolio. Browse the full list instead.</p><p><a class="btn btn-primary" href="properties.html">Back to properties</a></p></div>';
    document.title = "Center not found — Silver Bears";
    return;
  }

  document.title = property.name + " — Silver Bears";
  const photo = property.photo
    ? '<div class="property-photo card-visual"><img src="' +
      property.photo +
      '" alt="' +
      property.name +
      '"></div>'
    : '<div class="property-photo card-visual card-visual--type"><span class="mono-state">' +
      property.state +
      '</span><span class="mono-city">' +
      property.city +
      "</span></div>";

  const spacesRows = (property.spaces || [])
    .map(function (space) {
      return (
        "<tr><td>" +
        space.id +
        (space.note ? ' <span class="muted">(' + space.note + ")</span>" : "") +
        "</td><td>" +
        (space.sf ? sbFormatNumber(space.sf) + " SF" : "—") +
        "</td></tr>"
      );
    })
    .join("");

  const spacesBlock = property.availableSpaces
    ? "<h2>Available space</h2><p>" +
      sbAvailabilityLabel(property) +
      ".</p><table class='spaces-table'><thead><tr><th>Suite</th><th>Size</th></tr></thead><tbody>" +
      (spacesRows || "<tr><td colspan='2'>See leasing for current suites.</td></tr>") +
      "</tbody></table>"
    : "<h2>Availability</h2><p>This center is in the portfolio and is fully leased right now. Ask leasing about upcoming space or nearby centers.</p>";

  const mapHref = property.address
    ? "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(property.address)
    : property.lat
      ? "https://www.google.com/maps/search/?api=1&query=" + property.lat + "," + property.lng
      : "";

  root.innerHTML =
    '<div class="page-hero"><p class="kicker"><a href="properties.html">Properties</a> / ' +
    property.stateName +
    "</p><h1>" +
    property.name +
    '</h1><p class="lede">' +
    property.city +
    ", " +
    property.state +
    (property.address ? " · " + property.address : "") +
    "</p></div><div class='property-hero'>" +
    photo +
    "<div><p>" +
    sbAvailabilityLabel(property) +
    '.</p><p>Family-owned shopping center in ' +
    property.city +
    ", " +
    property.stateName +
    ". Inquire about a suite, or go to How to lease for application forms.</p>" +
    (mapHref ? '<p><a class="btn btn-ghost" href="' + mapHref + '" rel="noopener">Get directions</a></p>' : "") +
    '<p><a class="btn btn-primary" href="#inquire">Inquire about this center</a></p></div></div><div class="section">' +
    spacesBlock +
    '</div><div class="section" id="inquire"><div class="panel"><h2>Inquire about ' +
    property.name +
    '</h2><p class="form-note">Opens your email to leasing@bearsmgmt.com. Nothing is stored on this website.</p>' +
    '<form data-mailto-form data-to="leasing@bearsmgmt.com"><input type="hidden" name="_subject" value="Leasing inquiry: ' +
    property.name +
    '"><label class="field">Name<input name="Name" required></label><label class="field">Email<input type="email" name="Email" required></label><label class="field">Phone<input type="tel" name="Phone"></label><label class="field">Business type<input name="Business type"></label><label class="field">Message<textarea name="Message" required>I am interested in ' +
    property.name +
    " in " +
    property.city +
    ", " +
    property.state +
    ".</textarea></label><p><button class='btn btn-primary' type='submit'>Send inquiry</button> <a class='btn btn-ghost' href='how-to-lease.html'>How to lease</a></p></form></div></div>";

  const form = root.querySelector("[data-mailto-form]");
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const data = new FormData(form);
    const lines = [];
    data.forEach(function (value, key) {
      if (key === "_subject") return;
      lines.push(key + ": " + value);
    });
    window.location.href =
      "mailto:leasing@bearsmgmt.com?subject=" +
      encodeURIComponent(data.get("_subject")) +
      "&body=" +
      encodeURIComponent(lines.join("\n"));
  });
}

document.addEventListener("DOMContentLoaded", function () {
  sbRenderFeatured();
  sbInitPropertiesPage();
  sbInitPropertyPage();
});
