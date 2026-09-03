#!/usr/bin/env python3
"""Sanity checks for the static Silver Bears site."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
JS = (DOCS / "js" / "properties.js").read_text()
properties, _ = json.JSONDecoder().raw_decode(JS[JS.find("[") :])

ids = [p["id"] for p in properties]
names = [p["name"] for p in properties]

assert len(properties) == 24, f"expected 24 centers, got {len(properties)}"
assert len(ids) == len(set(ids)), "duplicate property ids"
assert len(names) == len(set(names)), "duplicate property names"
assert "i-southport-plaza" in ids
assert "7450-green-bay" not in ids
assert "medison" not in ids
assert "sample-page" not in ids

available = [p for p in properties if p["availableSpaces"] > 0]
leased = [p for p in properties if p["availableSpaces"] == 0]
assert len(available) == 18, f"expected 18 available, got {len(available)}"
assert len(leased) == 6, f"expected 6 fully leased, got {len(leased)}"
assert len({p["state"] for p in properties}) == 10

forbidden = [
    "sample-page",
    "Leasing Inquires",
    "Lorem Ipsum",
    "Export as Spreadsheet",
    "Conveinence",
    "Orthadontist",
    "Hygeinist",
    "Opthamology",
    "Materninty",
    "Maintenace",
    "Lot #",
    "0 Properties Found",
    "0 properties found",
]
site_text = "\n".join(path.read_text() for path in DOCS.rglob("*.html"))
for needle in forbidden:
    assert needle not in site_text, f"leftover copy found: {needle}"

assert "family=DM+Sans" in site_text
assert "Fraunces" not in site_text
assert "Figtree" not in site_text

for p in properties:
    index = DOCS / "properties" / p["id"] / "index.html"
    assert index.exists(), f"missing center page {p['id']}"
    text = index.read_text()
    assert p["name"] in text
    assert "How to lease" in text
    assert "Find space" not in text

aliases = {
    "medison": "madison",
    "7450-green-bay": "i-southport-plaza",
    "sugarcreek-plaza-ll": "sugarcreek-plaza-ii",
}
for alias, canonical in aliases.items():
    text = (DOCS / "properties" / alias / "index.html").read_text()
    assert f"../{canonical}/" in text

for name in ("index.html", "properties/index.html", "how-to-lease/index.html", "contact/index.html"):
    text = (DOCS / name).read_text()
    for label in ("Home", "Properties", "How to lease", "Contact"):
        assert label in text, f"{name} missing {label}"
    assert "Find space" not in text, f"{name} still has Find space chrome"
    assert "family=DM+Sans" in text

home = (DOCS / "index.html").read_text()
assert home.count("<h1>") == 1
assert "Retail space in real shopping centers." in home
assert "hero-photo" in home
assert "hero-overlay" in home
assert "18" in home and "centers with space" in home
assert 'id="about"' not in home
for p in leased:
    assert p["name"] not in home, f"zero-space center on Home: {p['name']}"
for p in available:
    assert p["name"] in home, f"available center missing from Home: {p['name']}"
assert home.count('class="view"') >= 18
assert "badge" not in home

lease = (DOCS / "how-to-lease/index.html").read_text()
assert lease.count('class="step"') == 3
assert "Browse" in lease
assert "Inquire" in lease
assert "Credit check" in lease
assert "Five steps" not in lease
assert "Credit Check Authorization" in lease
assert "Not Available" not in lease

contact = (DOCS / "contact/index.html").read_text()
assert "I-Southport Plaza" in contact
assert "The Village Shoppes of Madison" in contact
assert "Not Available" not in contact
assert "Lot #" not in contact

site_js = (DOCS / "js" / "site.js").read_text()
assert "badge" not in site_js
assert ">View</a>" in site_js
assert 'availability.value = "available"' in site_js
assert "sbHref(property.photo)" in site_js

css = (DOCS / "css" / "styles.css").read_text()
assert "#f4f5f6" in css.lower() or "#F4F5F6" in css
assert "#1c1e21" in css.lower() or "#1C1E21" in css
assert "#1f4d3a" in css.lower() or "#1F4D3A" in css
assert "DM Sans" in css

assert (DOCS / "assets" / "hero.jpg").exists()
assert (DOCS / ".nojekyll").exists()

print("ok: designer system, 18 available on Home, three lease steps, no leftover WordPress junk")
