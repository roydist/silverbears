#!/usr/bin/env python3
"""Sanity checks for the static Silver Bears site."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
JS = (DOCS / "js" / "properties.js").read_text()

match = re.search(r"window\.SB_PROPERTIES = (\[.*?\]);", JS, re.S)
if not match:
    raise SystemExit("Could not parse SB_PROPERTIES")

properties = json.loads(match.group(1))
ids = [p["id"] for p in properties]
names = [p["name"] for p in properties]

assert len(properties) == 24, f"expected 24 centers, got {len(properties)}"
assert len(ids) == len(set(ids)), "duplicate property ids"
assert len(names) == len(set(names)), "duplicate property names"

available = [p for p in properties if p["availableSpaces"] > 0]
leased = [p for p in properties if p["availableSpaces"] == 0]
assert len(available) == 18, f"expected 18 available, got {len(available)}"
assert len(leased) == 6, f"expected 6 fully leased, got {len(leased)}"
assert len({p["state"] for p in properties}) == 10

pages = [
    "index.html",
    "properties.html",
    "how-to-lease.html",
    "contact.html",
    "privacy.html",
    "terms.html",
    "property.html",
    "404.html",
]
for name in pages:
    text = (DOCS / name).read_text()
    assert "sample-page" not in text.lower()
    assert "Leasing Inquires" not in text
    for label in ("Home", "Properties", "How to lease", "Contact", "Find space"):
        assert label in text, f"{name} missing {label}"

lease = (DOCS / "how-to-lease.html").read_text()
assert "Leasing inquiries" in lease
assert "Credit Check Authorization" in lease
assert "Business Background" in lease
assert "Personal Financial Statement" in lease

nonsense = [
    p
    for p in properties
    if "xyzzy-no-center" in (p["name"] + p["city"] + p["address"]).lower()
]
assert nonsense == []

leased_names = {p["name"] for p in leased}
assert "Sand Lake Corners" in leased_names
assert "Southport Plaza" not in leased_names

print("ok: 24 unique centers, 18 available, 10 states, required pages present")
