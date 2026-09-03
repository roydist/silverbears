# Silver Bears Real Estate

Static marketing site for [Silver Bears Real Estate](https://silverbears.com) — family-owned shopping-center leasing and property management. Built to replace the current WordPress site with a small, fast set of public pages.

**Live URL (GitHub Pages):** [https://roydist.github.io/silverbears/](https://roydist.github.io/silverbears/)

The files are on `main` and on the `gh-pages` branch. A repo admin still needs to turn Pages on once (Settings → Pages → deploy `gh-pages` / root). The GitHub token used here cannot create a Pages site.

## Pages

- **Home** — who they are, featured centers, portfolio counts taken only from the 24-center list
- **Properties** — one searchable list (state, city, availability, size). Fully leased centers stay on the list. Empty filters hide the grid instead of showing a zero-result table
- **How to lease** — five steps, application PDFs, plain-English background check
- **Contact** — leasing and office contacts, inquiry form, maintenance report as a secondary path
- **Privacy / Terms** — short placeholders, with links to the current WordPress versions

Header navigation is only Home, Properties, How to lease, and Contact, plus a **Find space** button. There are no leftover test fields or sample pages.

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

## GitHub Pages

The site files are ready in two places:

- `docs/` on `main` (GitHub Actions workflow in `.github/workflows/pages.yml`)
- `gh-pages` branch (same site at the branch root)

This agent cannot flip **Settings → Pages** (the GitHub token is not allowed to create a Pages site). One click from a repo admin publishes https://roydist.github.io/silverbears/ :

1. Open **Settings → Pages**
2. **Build and deployment → Source:** Deploy from a branch
3. **Branch:** `gh-pages` / folder `/ (root)` — Save

Or: Source **GitHub Actions**, then re-run the “Deploy GitHub Pages” workflow on `main`.

After that, center URLs look like `https://roydist.github.io/silverbears/properties/southport-plaza/`.

## Forms and PDFs

Inquiry and maintenance forms open a `mailto:` draft (no backend). Application PDFs are copies of the files already published on the live WordPress site:

- `docs/assets/forms/credit-check-authorization.pdf`
- `docs/assets/forms/business-background.pdf`
- `docs/assets/forms/personal-financial-statement.pdf`

Property photos in `docs/assets/properties/` are the company’s own published images from silverbears.com. Centers without a usable photo use a typographic card instead of stock photography.

## Data

Property names, available space counts, square footage, cities, and states match the public portfolio list. Stats on the homepage (24 centers, 10 states, 18 with space) are counts of that list — not invented GLA totals or a founding year.
