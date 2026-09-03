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
    "Connecting communities through exceptional shopping experience.",
    "Your investment is our investment.",
    "family-owned owner and manager",
    "Family-owned",
    "family owned",
    "family-owned",
    "There is no separate About page",
    "We do not pad this site",
    "dummy lot",
    "dummy lot number",
    "state mega-menu",
    "tenant-category maze",
    "This is not in the header",
    "not in the main navigation",
    "not in the header or the mobile menu",
    "not a public upload",
    "The old leasing page was a wall of legal text",
    "Retail space in real shopping centers.",
    "Choose a real shopping center",
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
assert "Retail space in grocery-anchored centers." in home
assert "Your investment is our investment." not in home
assert "Connecting communities" not in home
assert "Family-owned" not in home
assert "4 / 13,466 SF" in home
assert "5 outlots" in home
assert "5 / 323,652 SF" not in home
assert "5 outlots available" not in home
assert "3 / 38,480 SF + 1 outlot" in home

# Regression: The Highlands must never show aggregated outlot SF
assert "323,652 SF" not in home, "The Highlands card must not aggregate outlot acreage as SF"
assert home.index("Waynetowne Plaza") < home.index("The Highlands") < home.index("Cedar Crest")
assert "hero-photo" in home
assert "hero-overlay" in home
assert "18" in home and "centers with space" in home
assert 'id="about"' not in home
assert "founded" not in home.lower()
assert "international" not in home.lower()
assert "global" not in home.lower()
featured = home.split('class="grid grid-featured"', 1)[1].split("</section>", 1)[0]
waynetowne_end = featured.find("</article>", featured.find("Waynetowne"))
waynetowne_card = featured[featured.find("Waynetowne"):waynetowne_end]
assert "card-visual" not in waynetowne_card
assert "<img" not in waynetowne_card
featured_names = ["Waynetowne Plaza", "The Highlands", "Cedar Crest"]
for name in featured_names:
    assert name in featured, f"featured missing {name}"
for p in available:
    if p["name"] not in featured_names:
        assert p["name"] not in featured, f"extra center on Home: {p['name']}"
for p in leased:
    assert p["name"] not in featured, f"zero-space center on Home: {p['name']}"
assert featured.count("property-card") == 3
assert "badge" not in home

lease = (DOCS / "how-to-lease/index.html").read_text()
assert lease.count('class="step"') == 3
assert "Browse" in lease
assert "Inquire" in lease
assert "Credit check" in lease
assert "Three steps from first inquiry to a signed lease." in lease
assert "Review current availability by state, city, or size." in lease
assert "Contact the leasing team with your business name, required size, intended use, and target opening date." in lease
assert "Every applicant undergoes a financial background review" in lease
assert "Download, complete, and return the three forms below to the leasing team." in lease
assert "Jared Aberman" in lease
assert "Mary Garcia" in lease
assert "Five steps" not in lease
assert "Credit Check Authorization" in lease
assert "Not Available" not in lease
assert "public upload" not in lease
assert "WordPress" not in lease

contact = (DOCS / "contact/index.html").read_text()
assert "I-Southport Plaza" in contact
assert "The Village Shoppes of Madison" in contact
assert "Leasing inquiries, property management, and maintenance requests." in contact
assert "This form opens your email application addressed to the leasing team." in contact
assert "Tenants: select your shopping center and describe the issue." in contact
assert "P.O. Box #811240" in contact
assert "Boca Raton, FL 33481" in contact
assert "888.342.9378" in contact
assert "678.714.7893" in contact
assert "Jared Aberman" in contact
assert "Mary Garcia" in contact
assert "Not Available" not in contact
assert "Lot #" not in contact
assert "dummy" not in contact.lower()
assert "not in the header" not in contact

highlands = (DOCS / "properties" / "the-highlands" / "index.html").read_text()
assert "The Highlands is a shopping center in Bristol, Virginia, in the Silver Bears portfolio." in highlands
assert "5 outlots available" in highlands
assert "323,652" not in highlands
assert "50,529" in highlands
assert "84,945" in highlands
assert "55,757" in highlands
assert "54,885" in highlands
assert "77,536" in highlands
assert "pad sites" in highlands
assert "5 spaces" not in highlands

southport_outlot = (DOCS / "properties" / "i-southport-plaza" / "index.html").read_text()
assert "1 outlot available" in southport_outlot
assert "1 space · 3,000 SF" not in southport_outlot

cedar = (DOCS / "properties" / "cedar-crest" / "index.html").read_text()
assert "3 spaces · 38,480 SF" in cedar
assert "1 outlot available" in cedar
assert "4 spaces · 42,680 SF" not in cedar

regency = (DOCS / "properties" / "regency-point" / "index.html").read_text()
assert "1 space · 2,310 SF" in regency
assert "1 outlot available" in regency
assert "2 spaces · 7,310 SF" not in regency

site_js = (DOCS / "js" / "site.js").read_text()
assert "badge" not in site_js
assert ">View</a>" in site_js
assert 'availability.value = "available"' in site_js
assert "sbCardLine" in site_js
assert "sbCardLine" in site_js
assert "property.photo" not in site_js

footer = "Silver Bears Real Estate. Shopping-center leasing and property management."
for name in ("index.html", "properties/index.html", "how-to-lease/index.html", "contact/index.html", "privacy/index.html", "terms/index.html", "404.html", "thanks.html"):
    text = (DOCS / name).read_text()
    assert footer in text, f"{name} missing formal footer"
    assert "Family-owned" not in text
    assert "family-owned" not in text

properties_index = (DOCS / "properties" / "index.html").read_text()
assert "Twenty-four shopping centers across ten states, from Wisconsin to Florida." in properties_index

not_found = (DOCS / "404.html").read_text()
assert "Page not found." in not_found
assert "That page is not here." not in not_found

highlands_start = home.rfind("<article", 0, home.find("the-highlands"))
highlands_end = home.find("</article>", highlands_start) + len("</article>")
highlands_card = home[highlands_start:highlands_end]
assert "5 outlots" in highlands_card
assert "card-visual" in highlands_card
assert "323,652" not in highlands_card
assert "5 / 323,652 SF" not in highlands_card

css = (DOCS / "css" / "styles.css").read_text()
assert "#f4f5f6" in css.lower()
assert "#1c1e21" in css.lower()
assert "#1b4a3a" in css.lower()
assert "#1f4d3a" not in css.lower()
assert "Fraunces" not in css
assert "Figtree" not in css
assert "DM Sans" in css
assert "--radius: 3px" in css
assert "border-radius: 18px" not in css
assert "Segoe UI" not in css

assert (DOCS / "assets" / "hero.jpg").exists()
assert (DOCS / ".nojekyll").exists()

print("ok: type-only cards, three featured centers, designer system")
