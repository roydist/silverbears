#!/usr/bin/env python3
"""Generate the static GitHub Pages site from docs/js/properties.js."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
JS = (DOCS / "js" / "properties.js").read_text()
PROPERTIES, _ = json.JSONDecoder().raw_decode(JS[JS.find("[") :])

ALIASES = {
    "medison": "madison",
    "7450-green-bay": "i-southport-plaza",
    "sugarcreek-plaza-ll": "sugarcreek-plaza-ii",
}

NAV = [
    ("index.html", "Home", "home"),
    ("properties/", "Properties", "properties"),
    ("how-to-lease/", "How to lease", "lease"),
    ("contact/", "Contact", "contact"),
]


def fmt_num(n: int) -> str:
    return f"{n:,}"


def is_outlot(space: dict) -> bool:
    sid = str(space.get("id") or "").lstrip("#").upper()
    note = str(space.get("note") or "").lower()
    return "outlot" in note or sid.startswith("OP")


def split_listings(p: dict) -> tuple[list[dict], list[dict]]:
    spaces = p.get("spaces") or []
    outlots = [s for s in spaces if is_outlot(s)]
    suites = [s for s in spaces if not is_outlot(s)]
    return outlots, suites


def availability(p: dict) -> str:
    if not p["availableSpaces"]:
        return "Fully leased"
    outlots, suites = split_listings(p)
    parts: list[str] = []
    if suites:
        n = len(suites)
        sf = sum(int(s.get("sf") or 0) for s in suites)
        label = "1 space" if n == 1 else f"{n} spaces"
        parts.append(f"{label} · {fmt_num(sf)} SF")
    if outlots:
        n = len(outlots)
        parts.append("1 outlot available" if n == 1 else f"{n} outlots available")
    return " · ".join(parts) if parts else "Fully leased"


def card_line(p: dict) -> str:
    if not p["availableSpaces"]:
        return "Fully leased"
    return f"{p['availableSpaces']} / {fmt_num(p['availableSf'])} SF"


FEATURED_IDS = ("waynetowne-plaza", "the-highlands", "cedar-crest")


def by_id(pid: str) -> dict:
    return next(p for p in PROPERTIES if p["id"] == pid)


def head(title: str, description: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <link rel="icon" href="ROOT/assets/brand/favicon.png" type="image/png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="ROOT/css/styles.css">
</head>
<body>
"""


def header(active: str) -> str:
    links = []
    for href, label, key in NAV:
        cls = ' class="is-active"' if key == active else ""
        links.append(f'<a href="ROOT/{href}"{cls}>{label}</a>')
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="logo" href="ROOT/index.html">
      <span class="logo-mark" aria-hidden="true"></span>
      <span>Silver Bears<small>Real Estate</small></span>
    </a>
    <nav class="nav" aria-label="Primary">
      {''.join(links)}
    </nav>
    <button class="nav-toggle" type="button" aria-label="Open menu"><span></span></button>
  </div>
</header>
"""


def footer() -> str:
    return """<footer class="site-footer">
  <div class="wrap footer-row">
    <p>Silver Bears Real Estate. Family-owned shopping-center leasing and property management.</p>
    <p><a href="mailto:leasing@bearsmgmt.com">leasing@bearsmgmt.com</a> · <a href="tel:8883429378">888.342.9378</a></p>
    <nav>
      <a href="ROOT/privacy/">Privacy</a>
      <a href="ROOT/terms/">Terms</a>
    </nav>
  </div>
</footer>
"""


def page(title: str, description: str, active: str, content: str, extra_js: bool = True, prefix: str = "") -> str:
    scripts = """
<script src="ROOT/js/properties.js"></script>
<script src="ROOT/js/site.js"></script>
""" if extra_js else """
<script src="ROOT/js/site.js"></script>
"""
    html = (
        head(title, description)
        + header(active)
        + f'<main id="main">\n{content}\n</main>\n'
        + footer()
        + scripts
        + "</body>\n</html>\n"
    )
    return html.replace("ROOT/", prefix)


def write(rel: str, html: str) -> None:
    path = DOCS / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)


def redirect_page(target: str, label: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={escape(target)}">
  <link rel="canonical" href="{escape(target)}">
  <title>Redirecting — Silver Bears</title>
  <script>location.replace({json.dumps(target)});</script>
</head>
<body>
  <p>This page moved to <a href="{escape(target)}">{escape(label)}</a>.</p>
</body>
</html>
"""


def property_select(selected: str = "") -> str:
    opts = ['<option value="">Choose a center</option>']
    for p in PROPERTIES:
        sel = " selected" if p["id"] == selected else ""
        label = f"{p['name']} — {p['city']}, {p['state']}"
        opts.append(f'<option value="{escape(p["name"])}"{sel}>{escape(label)}</option>')
    return "\n".join(opts)


def card_html(p: dict) -> str:
    name = escape(p["name"])
    city = escape(p["city"])
    href = f'ROOT/properties/{escape(p["id"])}/'
    return (
        f'<article class="property-card">'
        f"<h3><a href=\"{href}\">{name}</a></h3>"
        f'<p class="card-meta">{escape(card_line(p))}</p>'
        f'<p class="place">{city}</p>'
        f'<a class="view" href="{href}">View</a>'
        f"</article>"
    )


def featured_cards() -> str:
    by_slug = {p["id"]: p for p in PROPERTIES}
    return "\n      ".join(card_html(by_slug[pid]) for pid in FEATURED_IDS)


def property_content(p: dict) -> str:
    name = escape(p["name"])
    city = escape(p["city"])
    state = escape(p["state"])
    state_name = escape(p["stateName"])
    avail = escape(availability(p))
    address = escape(p.get("address") or "")
    if p.get("photo"):
        photo = f'<div class="property-photo card-visual"><img src="ROOT/{escape(p["photo"])}" alt="{name}"></div>'
    else:
        photo = (
            f'<div class="property-photo card-visual card-visual--type">'
            f'<span class="mono-state">{state}</span><span class="mono-city">{city}</span></div>'
        )
    outlots, suites = split_listings(p)
    if p["availableSpaces"]:
        rows = []
        for space in p.get("spaces") or []:
            note = f' <span class="muted">({escape(space["note"])})</span>' if space.get("note") else ""
            sf = f'{fmt_num(space["sf"])} SF' if space.get("sf") else "—"
            rows.append(f'<tr><td>{escape(space["id"])}{note}</td><td>{sf}</td></tr>')
        body = "".join(rows) or "<tr><td colspan='2'>See leasing for current listings.</td></tr>"
        if outlots and not suites:
            heading = "Available outlots"
            col = "Outlot"
        elif outlots and suites:
            heading = "Available space"
            col = "Listing"
        else:
            heading = "Available space"
            col = "Suite"
        spaces_block = (
            f"<h2>{heading}</h2><p>{avail}.</p>"
            f"<table class='spaces-table'><thead><tr><th>{col}</th><th>Size</th></tr></thead><tbody>{body}</tbody></table>"
        )
    else:
        spaces_block = (
            "<h2>Availability</h2><p>This center is fully leased right now. "
            "Ask leasing about upcoming space or nearby centers.</p>"
        )
    if outlots and not suites:
        listing_note = (
            f"Shopping center in {city}, {state_name}. Available listings are outlots / pad sites, "
            "not inline shop suites. Inquire below, or go to How to lease for application forms."
        )
    elif outlots and suites:
        listing_note = (
            f"Shopping center in {city}, {state_name}. Listings include shop suites and outlots / pad sites. "
            "Inquire below, or go to How to lease for application forms."
        )
    else:
        listing_note = (
            f"Shopping center in {city}, {state_name}. Inquire about a listing, or go to How to lease for application forms."
        )
    map_href = ""
    if p.get("address"):
        map_href = "https://www.google.com/maps/search/?api=1&query=" + quote(p["address"])
    elif p.get("lat"):
        map_href = f"https://www.google.com/maps/search/?api=1&query={p['lat']},{p['lng']}"
    directions = (
        f'<p><a class="btn btn-ghost" href="{escape(map_href)}" rel="noopener">Get directions</a></p>'
        if map_href
        else ""
    )
    return f"""  <div class="wrap">
    <div class="page-hero">
      <p class="muted"><a href="ROOT/properties/">Properties</a> / {state_name}</p>
      <h1>{name}</h1>
      <p class="lede">{city}, {state}{(' · ' + address) if address else ''}</p>
    </div>
    <div class="property-hero">
      {photo}
      <div>
        <p>{avail}.</p>
        <p>{listing_note}</p>
        {directions}
        <p><a class="btn" href="#inquire">Inquire about this center</a></p>
      </div>
    </div>
    <div class="section">
      {spaces_block}
    </div>
    <div class="section" id="inquire">
      <div class="panel">
        <h2>Inquire about {name}</h2>
        <p class="form-note">Opens your email to leasing@bearsmgmt.com.</p>
        <form data-mailto-form data-to="leasing@bearsmgmt.com">
          <input type="hidden" name="_subject" value="Leasing inquiry: {name}">
          <label class="field">Name<input name="Name" required></label>
          <label class="field">Email<input type="email" name="Email" required></label>
          <label class="field">Phone<input type="tel" name="Phone"></label>
          <label class="field">Business type<input name="Business type"></label>
          <label class="field">Message<textarea name="Message" required>I am interested in {name} in {city}, {state}.</textarea></label>
          <p><button class="btn" type="submit">Send inquiry</button> <a class="btn btn-ghost" href="ROOT/how-to-lease/">How to lease</a></p>
        </form>
      </div>
    </div>
  </div>"""


def build() -> None:
    write(
        "index.html",
        page(
            "Silver Bears Real Estate — shopping-center leasing",
            "Family-owned commercial retail and shopping-center portfolio. Browse available space and talk to leasing.",
            "home",
            f"""  <section class="hero" aria-label="Southport Plaza">
    <img class="hero-photo" src="ROOT/assets/hero.jpg" alt="Southport Plaza shopping center">
    <div class="hero-overlay"></div>
    <div class="wrap">
      <h1>Retail space in grocery-anchored centers.</h1>
    </div>
  </section>
  <section class="proof">
    <div class="wrap">
      <p><strong>18</strong> centers with space · <strong>10</strong> states · <strong>24</strong> in the portfolio</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <h2>Featured centers</h2>
        <a class="view" href="ROOT/properties/">All properties</a>
      </div>
      <div class="grid grid-featured">
      {featured_cards()}
      </div>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <h2>How to lease</h2>
      <div class="steps">
        <article class="step">
          <div class="step-num">01</div>
          <div>
            <h3>Browse</h3>
            <p>Open a center and pick a suite or outlot.</p>
          </div>
        </article>
        <article class="step">
          <div class="step-num">02</div>
          <div>
            <h3>Inquire</h3>
            <p>Email leasing or use the contact form. Name the center and listing if you know it.</p>
          </div>
        </article>
        <article class="step">
          <div class="step-num">03</div>
          <div>
            <h3>Credit check</h3>
            <p>Send the tenant package. The leasing team reviews credit and follows up.</p>
          </div>
        </article>
      </div>
      <p><a class="view" href="ROOT/how-to-lease/">The three steps, with forms</a></p>
    </div>
  </section>""",
            extra_js=False,
        ),
    )

    write(
        "properties/index.html",
        page(
            "Properties — Silver Bears Real Estate",
            "Search Silver Bears shopping centers by state and available space.",
            "properties",
            """  <section class="page-hero">
    <div class="wrap">
      <h1>Properties</h1>
      <p class="lede">Centers with space first. Switch the filter to see the full portfolio, including fully leased centers.</p>
      <form class="filters" id="property-filters" onsubmit="return false;">
        <label class="field">Search
          <input id="filter-q" type="search" placeholder="Center, city, or address" autocomplete="off">
        </label>
        <label class="field">State
          <select id="filter-state"><option value="">All states</option></select>
        </label>
        <label class="field">Availability
          <select id="filter-availability">
            <option value="available">Space available</option>
            <option value="all">All centers</option>
            <option value="leased">Fully leased</option>
          </select>
        </label>
        <button class="btn btn-ghost" type="button" data-clear-filters>Clear</button>
      </form>
      <noscript><p>Turn on JavaScript to search and filter the 24-center list.</p></noscript>
      <div class="results-bar">
        <p data-count>Loading centers…</p>
      </div>
      <div class="grid" data-property-grid></div>
      <div class="empty" data-empty hidden>
        <h2>No centers match these filters</h2>
        <p>Try another state, or clear the filters to see centers with space.</p>
        <p><button class="btn btn-ghost" type="button" data-clear-filters>Clear filters</button></p>
      </div>
    </div>
  </section>""",
            prefix="../",
        ),
    )

    write(
        "how-to-lease/index.html",
        page(
            "How to lease — Silver Bears Real Estate",
            "Three steps to lease retail space with Silver Bears: browse, inquire, then credit check with the leasing team.",
            "lease",
            """  <section class="page-hero">
    <div class="wrap">
      <h1>How to lease</h1>
      <p class="lede">Three steps: browse a center, send an inquiry, then complete a credit check with the leasing team.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap split">
      <div class="steps">
        <article class="step">
          <div class="step-num">01</div>
          <div>
            <h2>Browse</h2>
            <p>Pick a center and a suite or outlot from the listings. Confirm size and notes.</p>
            <p><a class="view" href="ROOT/properties/">Open the property list</a></p>
          </div>
        </article>
        <article class="step">
          <div class="step-num">02</div>
          <div>
            <h2>Inquire</h2>
            <p>Email <a href="mailto:leasing@bearsmgmt.com">leasing@bearsmgmt.com</a> or use the contact form. Include business name, desired size, and target open date.</p>
          </div>
        </article>
        <article class="step">
          <div class="step-num">03</div>
          <div>
            <h2>Credit check</h2>
            <p>Complete the tenant package. The leasing team reviews credit and sends next steps.</p>
            <p>Jared Aberman · <a href="mailto:jared@silverbears.com">jared@silverbears.com</a> · <a href="tel:8883429378">888.342.9378</a></p>
            <p>Mary Garcia · <a href="mailto:mary@silverbears.com">mary@silverbears.com</a> · <a href="tel:6787693015">678.769.3015</a></p>
          </div>
        </article>
      </div>
      <aside class="panel">
        <h2>Forms</h2>
        <div class="forms">
          <a class="form-link" href="ROOT/assets/forms/credit-check-authorization.pdf">Credit Check Authorization <span>PDF</span></a>
          <a class="form-link" href="ROOT/assets/forms/business-background.pdf">Business Background <span>PDF</span></a>
          <a class="form-link" href="ROOT/assets/forms/personal-financial-statement.pdf">Personal Financial Statement <span>PDF</span></a>
        </div>
        <p>Email completed forms to <a href="mailto:mary@silverbears.com">mary@silverbears.com</a>.</p>
        <p>Every applicant completes a credit and background check.</p>
      </aside>
    </div>
  </section>""",
            extra_js=False,
            prefix="../",
        ),
    )

    write(
        "contact/index.html",
        page(
            "Contact — Silver Bears Real Estate",
            "Leasing and office contacts for Silver Bears Real Estate, plus a simple inquiry form.",
            "contact",
            f"""  <section class="page-hero">
    <div class="wrap">
      <h1>Contact</h1>
      <p class="lede">Space inquiries go to leasing@bearsmgmt.com. The form opens your email to that address.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap contact-grid">
      <div class="panel">
        <h2>Leasing</h2>
        <p><a href="mailto:leasing@bearsmgmt.com">leasing@bearsmgmt.com</a><br>
        <a href="tel:8883429378">888.342.9378</a></p>
        <p>Jared Aberman<br>
        <a href="mailto:jared@silverbears.com">jared@silverbears.com</a></p>
      </div>
      <div class="panel">
        <h2>Office</h2>
        <p><a href="tel:6787147893">678.714.7893</a><br>Monday–Friday, 8am–5pm EST</p>
        <p>P.O. Box #811240<br>Boca Raton, FL 33481</p>
        <p>Mary Garcia, property manager<br>
        <a href="mailto:mary@silverbears.com">mary@silverbears.com</a> · <a href="tel:6787693015">678.769.3015</a></p>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="wrap split">
      <div class="panel">
        <h2>Leasing inquiry</h2>
        <p class="form-note">This form opens your email to leasing@bearsmgmt.com.</p>
        <form data-mailto-form data-to="leasing@bearsmgmt.com">
          <input type="hidden" name="_subject" value="Leasing inquiry from silverbears.com">
          <label class="field">Name<input name="Name" required autocomplete="name"></label>
          <label class="field">Email<input type="email" name="Email" required autocomplete="email"></label>
          <label class="field">Phone<input type="tel" name="Phone" autocomplete="tel"></label>
          <label class="field">Property<select name="Property">{property_select()}</select></label>
          <label class="field">Message<textarea name="Message" required placeholder="What kind of space are you looking for?"></textarea></label>
          <p><button class="btn" type="submit">Send inquiry</button></p>
        </form>
      </div>
      <div class="panel" id="maintenance">
        <h2>Maintenance report</h2>
        <p class="form-note">Tenants: describe the issue and pick the shopping center.</p>
        <form data-mailto-form data-to="mary@silverbears.com">
          <input type="hidden" name="_subject" value="Maintenance report">
          <label class="field">Name<input name="Name" required></label>
          <label class="field">Email<input type="email" name="Email" required></label>
          <label class="field">Shopping center<select name="Shopping center" required>{property_select()}</select></label>
          <label class="field">What is wrong?<textarea name="Problem" required></textarea></label>
          <p><button class="btn" type="submit">Report issue</button></p>
        </form>
      </div>
    </div>
  </section>""",
            extra_js=False,
            prefix="../",
        ),
    )

    write(
        "privacy/index.html",
        page(
            "Privacy — Silver Bears Real Estate",
            "Privacy information for the Silver Bears marketing site.",
            "",
            """  <section class="page-hero">
    <div class="wrap legal">
      <h1>Privacy</h1>
      <p>Inquiry and maintenance forms open your email app. They do not store messages on this site.</p>
      <p>If you email us, we use your name, contact details, and message to respond to a leasing or property-management request. Application forms may include financial information, which we use to evaluate a lease — see <a href="ROOT/how-to-lease/">How to lease</a>.</p>
      <p>A longer privacy policy is at <a href="https://silverbears.com/privacy-policy/">silverbears.com/privacy-policy</a>. Questions: <a href="mailto:privacy@silverbears.com">privacy@silverbears.com</a>.</p>
    </div>
  </section>""",
            extra_js=False,
            prefix="../",
        ),
    )

    write(
        "terms/index.html",
        page(
            "Terms — Silver Bears Real Estate",
            "Terms of use for the Silver Bears marketing site.",
            "",
            """  <section class="page-hero">
    <div class="wrap legal">
      <h1>Terms</h1>
      <p>This website describes shopping centers in the Silver Bears portfolio and how to inquire about leasing. Listings, sizes, and availability can change. Nothing here is an offer to lease until we sign a written agreement.</p>
      <p>Do not use this site for anything unlawful. Application forms are for genuine lease inquiries only.</p>
      <p>Longer terms are at <a href="https://silverbears.com/terms-and-conditions/">silverbears.com/terms-and-conditions</a>.</p>
    </div>
  </section>""",
            extra_js=False,
            prefix="../",
        ),
    )

    write(
        "404.html",
        page(
            "Page not found — Silver Bears Real Estate",
            "That page is not on this site.",
            "",
            """  <section class="page-hero">
    <div class="wrap">
      <h1>That page is not here.</h1>
      <p class="lede">Try Home, Properties, How to lease, or Contact.</p>
      <p><a class="btn" href="ROOT/index.html">Go home</a> <a class="btn btn-ghost" href="ROOT/properties/">Properties</a></p>
    </div>
  </section>""",
            extra_js=False,
        ),
    )

    write(
        "thanks.html",
        page(
            "Message ready — Silver Bears Real Estate",
            "Your email app should have opened with the inquiry.",
            "contact",
            """  <section class="page-hero">
    <div class="wrap">
      <h1>Send the email to finish</h1>
      <p class="lede">If your email app opened, send the draft to finish. If it did not, write to <a href="mailto:leasing@bearsmgmt.com">leasing@bearsmgmt.com</a>.</p>
      <p><a class="btn" href="ROOT/properties/">Back to properties</a></p>
    </div>
  </section>""",
            extra_js=False,
        ),
    )

    for p in PROPERTIES:
        write(
            f"properties/{p['id']}/index.html",
            page(
                f"{p['name']} — Silver Bears Real Estate",
                f"{p['name']} in {p['city']}, {p['state']}. {availability(p)}.",
                "properties",
                property_content(p),
                extra_js=False,
                prefix="../../",
            ),
        )

    for alias, canonical in ALIASES.items():
        dest = by_id(canonical)
        write(f"properties/{alias}/index.html", redirect_page(f"../{canonical}/", dest["name"]))

    write("leasing-information/index.html", redirect_page("../how-to-lease/", "How to lease"))
    write("forms-page/index.html", redirect_page("../contact/", "Contact"))

    write("properties.html", redirect_page("properties/", "Properties"))
    write("how-to-lease.html", redirect_page("how-to-lease/", "How to lease"))
    write("contact.html", redirect_page("contact/", "Contact"))
    write("privacy.html", redirect_page("privacy/", "Privacy"))
    write("terms.html", redirect_page("terms/", "Terms"))
    write(
        "property.html",
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Redirecting — Silver Bears</title>
  <script>
    (function () {
      var id = new URLSearchParams(location.search).get('id') || '';
      var aliases = {medison:'madison','7450-green-bay':'i-southport-plaza','sugarcreek-plaza-ll':'sugarcreek-plaza-ii'};
      if (aliases[id]) id = aliases[id];
      location.replace(id ? ('properties/' + encodeURIComponent(id) + '/') : 'properties/');
    })();
  </script>
</head>
<body>
  <p><a href="properties/">Go to properties</a></p>
</body>
</html>
""",
    )

    print(f"built {len(PROPERTIES)} center pages and {len(ALIASES)} old-slug redirects")


if __name__ == "__main__":
    build()
