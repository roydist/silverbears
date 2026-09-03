# Silver Bears Real Estate

Static marketing site for [Silver Bears Real Estate](https://silverbears.com) — shopping-center leasing and property management. Built as a small GitHub Pages MVP, not WordPress.

**Live URL (GitHub Pages):** [https://roydist.github.io/silverbears/](https://roydist.github.io/silverbears/)

Live on GitHub Pages from `main` via the **Deploy GitHub Pages** workflow.

## Pages

- **Home** — full-bleed plaza hero, owner-operator positioning, three featured centers, then the three lease steps
- **Properties** — full list, defaulting to centers with space
- **How to lease** — browse → inquire → credit check / leasing team, plus the three application PDFs
- **Contact** — leasing and office contacts, inquiry form, maintenance report as a secondary path
- **Privacy / Terms** — short placeholders, with links to the current WordPress versions

Header navigation is only Home, Properties, How to lease, and Contact. There are no leftover test fields or sample pages.

Type is DM Sans. Color is off-white `#F4F5F6`, graphite `#1C1E21`, and one forest accent `#1B4A3A`. Radius is 3px.

## Run locally

The site is static HTML, CSS, and JavaScript in `docs/`. Serve that folder (relative links need an HTTP server, not `file://`):

```bash
python3 -m http.server 4173 --directory docs
```

Then open [http://127.0.0.1:4173/](http://127.0.0.1:4173/).

Sanity check / regenerate HTML from property data:

```bash
python3 scripts/build_site.py
python3 scripts/check-site.py
```

## URLs

Center pages live at `/properties/<slug>/`, matching the old WordPress paths (for example `/properties/southport-plaza/`). Old leftover slugs redirect:

- `/properties/medison/` → Madison (typo on the live site)
- `/properties/7450-green-bay/` → I-Southport Plaza (that address is a real center; the leftover slug is not a second listing)
- `/properties/sugarcreek-plaza-ll/` → Sugarcreek Plaza II
- `/leasing-information/` → How to lease
- `/forms-page/` → Contact

There is no sample-page, no spreadsheet export, and no tenant-category filter.

## Forms and PDFs

Inquiry and maintenance forms open a `mailto:` draft (no backend). Application PDFs are copies of the files already published on the live WordPress site:

- `docs/assets/forms/credit-check-authorization.pdf`
- `docs/assets/forms/business-background.pdf`
- `docs/assets/forms/personal-financial-statement.pdf`

Property photos in `docs/assets/properties/` are the company’s own published images from silverbears.com. Centers without a usable photo use a typographic card instead of stock photography. The home hero uses the Southport Plaza photo.

## Data

Property names, available space counts, square footage, cities, and states match the public portfolio list. Stats on the homepage (18 centers with space, 10 states, 24 in the portfolio) are counts of that list — not invented GLA totals or a founding year.
