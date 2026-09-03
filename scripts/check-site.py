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

for p in properties:
    index = DOCS / "properties" / p["id"] / "index.html"
    assert index.exists(), f"missing center page {p['id']}"
    text = index.read_text()
    assert p["name"] in text
    assert "Find space" in text
    assert "How to lease" in text

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
    for label in ("Home", "Properties", "How to lease", "Contact", "Find space"):
        assert label in text, f"{name} missing {label}"

home = (DOCS / "index.html").read_text()
assert "Your investment is our investment." in home
assert 'id="about"' in home

lease = (DOCS / "how-to-lease/index.html").read_text()
assert "Leasing inquiries" in lease
assert "Credit Check Authorization" in lease
assert "Not Available" not in lease

contact = (DOCS / "contact/index.html").read_text()
assert "I-Southport Plaza" in contact
assert "The Village Shoppes of Madison" in contact
assert "Report a maintenance issue" in (DOCS / "index.html").read_text()
assert "Not Available" not in contact
assert "Lot #" not in contact

print("ok: 24 unique centers, folder URLs, aliases, no leftover WordPress junk")
