#!/usr/bin/env python3
"""Generate the static GitHub Pages site from docs/js/properties.js."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

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


def availability(p: dict) -> str:
    if not p["availableSpaces"]:
        return "No current availability"
    spaces = "1 space" if p["availableSpaces"] == 1 else f"{p['availableSpaces']} spaces"
    return f"{spaces} · {fmt_num(p['availableSf'])} SF"


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
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">
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
    <div class="header-cta">
      <a class="btn btn-primary btn-small" href="ROOT/properties/">Find space</a>
      <button class="nav-toggle" type="button" aria-label="Open menu"><span></span></button>
    </div>
  </div>
</header>
"""


def footer() -> str:
    return """<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h2>Silver Bears Real Estate</h2>
        <p>Family-owned commercial retail and shopping-center portfolio. Leasing and property management.</p>
        <p>P.O. Box #811240<br>Boca Raton, FL 33481</p>
      </div>
      <div>
        <h2>Explore</h2>
        <ul>
          <li><a href="ROOT/index.html">Home</a></li>
          <li><a href="ROOT/properties/">Properties</a></li>
          <li><a href="ROOT/how-to-lease/">How to lease</a></li>
          <li><a href="ROOT/contact/">Contact</a></li>
        </ul>
      </div>
      <div>
        <h2>Leasing inquiries</h2>
        <p><a href="mailto:leasing@bearsmgmt.com">leasing@bearsmgmt.com</a><br>
        <a href="tel:8883429378">888.342.9378</a> (toll free)</p>
        <p class="maintenance-link"><a href="ROOT/contact/#maintenance">Report a maintenance issue</a></p>
      </div>
    </div>
    <div class="subfooter">
      <span>&copy; <span data-year></span> Silver Bears Real Estate</span>
      <span><a href="ROOT/privacy/">Privacy</a> · <a href="ROOT/terms/">Terms</a></span>
    </div>
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
    if p["availableSpaces"]:
        rows = []
        for space in p.get("spaces") or []:
            note = f' <span class="muted">({escape(space["note"])})</span>' if space.get("note") else ""
            sf = f'{fmt_num(space["sf"])} SF' if space.get("sf") else "—"
            rows.append(f'<tr><td>{escape(space["id"])}{note}</td><td>{sf}</td></tr>')
        body = "".join(rows) or "<tr><td colspan='2'>See leasing for current suites.</td></tr>"
        spaces_block = (
            f"<h2>Available space</h2><p>{avail}.</p>"
            f"<p>These are the suites currently listed as open. There is no picker for spaces that are not for lease.</p>"
            f"<table class='spaces-table'><thead><tr><th>Suite</th><th>Size</th></tr></thead><tbody>{body}</tbody></table>"
        )
    else:
        spaces_block = (
            "<h2>Availability</h2><p>This center is in the portfolio and is fully leased right now. "
            "Ask leasing about upcoming space or nearby centers.</p>"
        )
    map_href = ""
    if p.get("address"):
        from urllib.parse import quote

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
      <p class="kicker"><a href="ROOT/properties/">Properties</a> / {state_name}</p>
      <h1>{name}</h1>
      <p class="lede">{city}, {state}{(' · ' + address) if address else ''}</p>
    </div>
    <div class="property-hero">
      {photo}
      <div>
        <p>{avail}.</p>
        <p>Family-owned shopping center in {city}, {state_name}. Inquire about a suite that is listed as available, or go to How to lease for application forms.</p>
        {directions}
        <p><a class="btn btn-primary" href="#inquire">Inquire about this center</a></p>
      </div>
    </div>
    <div class="section">
      {spaces_block}
    </div>
    <div class="section" id="inquire">
      <div class="panel">
        <h2>Inquire about {name}</h2>
        <p class="form-note">Opens your email to leasing@bearsmgmt.com. Nothing is stored on this website.</p>
        <form data-mailto-form data-to="leasing@bearsmgmt.com">
          <input type="hidden" name="_subject" value="Leasing inquiry: {name}">
          <label class="field">Name<input name="Name" required></label>
          <label class="field">Email<input type="email" name="Email" required></label>
          <label class="field">Phone<input type="tel" name="Phone"></label>
          <label class="field">Business type<input name="Business type"></label>
          <label class="field">Message<textarea name="Message" required>I am interested in {name} in {city}, {state}.</textarea></label>
          <p><button class="btn btn-primary" type="submit">Send inquiry</button> <a class="btn btn-ghost" href="ROOT/how-to-lease/">How to lease</a></p>
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
            """  <section class="hero">
    <div class="wrap">
      <p class="kicker">Your investment is our investment.</p>
      <h1>Retail space in real shopping centers.</h1>
      <p class="lede">Connecting communities through exceptional shopping experience. We are a family-owned owner and manager of community shopping centers — leasing space and taking care of the centers day to day.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="ROOT/properties/">Browse properties</a>
        <a class="btn btn-ghost" href="ROOT/how-to-lease/">How to lease</a>
      </div>
      <div class="stats" aria-label="Portfolio snapshot">
        <div class="stat"><b>24</b><span>shopping centers in this portfolio</span></div>
        <div class="stat"><b>10</b><span>states, from Wisconsin to Florida</span></div>
        <div class="stat"><b>18</b><span>centers with space available now</span></div>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="kicker">Featured</p>
          <h2>Centers with space to lease</h2>
        </div>
        <a href="ROOT/properties/">See all properties</a>
      </div>
      <div class="grid" data-featured></div>
    </div>
  </section>
  <section class="section" id="about">
    <div class="wrap split">
      <div>
        <p class="kicker">About us</p>
        <h2>A family-owned retail portfolio</h2>
        <p>Silver Bears Real Estate leases and manages shopping centers for tenants who want to serve local shoppers. There is no separate About page — this is it. Browse the list, pick a center, then talk to leasing.</p>
        <p>We do not pad this site with invented square-footage totals or founding-year claims. The properties and available space you see here match the current public portfolio.</p>
        <p><a class="btn btn-primary" href="ROOT/properties/">Find space</a> <a class="btn btn-ghost" href="ROOT/contact/">Talk to leasing</a></p>
      </div>
      <div class="panel">
        <h2>How a lease starts</h2>
        <p>1. Browse properties and filter by state or size.</p>
        <p>2. Pick a center and note the suites that are actually open.</p>
        <p>3. Send an inquiry or download the application forms.</p>
        <p><a href="ROOT/how-to-lease/">Read the full process</a></p>
      </div>
    </div>
  </section>""",
        ),
    )

    write(
        "properties/index.html",
        page(
            "Properties — Silver Bears Real Estate",
            "Search Silver Bears shopping centers by state, city, and available space.",
            "properties",
            """  <section class="page-hero">
    <div class="wrap">
      <p class="kicker">Portfolio</p>
      <h1>Properties</h1>
      <p class="lede">One list of the shopping centers we lease and manage. Filter by state, city, or size. Centers with no space right now stay on the list, marked as fully leased. Each center is listed once — there is no state mega-menu and no tenant-category maze.</p>
      <form class="filters" id="property-filters" onsubmit="return false;">
        <label class="field">Search
          <input id="filter-q" type="search" placeholder="Center, city, or address" autocomplete="off">
        </label>
        <label class="field">State
          <select id="filter-state"><option value="">All states</option></select>
        </label>
        <label class="field">City
          <select id="filter-city"><option value="">All cities</option></select>
        </label>
        <label class="field">Availability
          <select id="filter-availability">
            <option value="">All centers</option>
            <option value="available">Space available</option>
            <option value="leased">Fully leased</option>
          </select>
        </label>
        <label class="field">Available size
          <select id="filter-size">
            <option value="">Any size</option>
            <option value="lt5">Under 5,000 SF</option>
            <option value="5to15">5,000–15,000 SF</option>
            <option value="gt15">Over 15,000 SF</option>
          </select>
        </label>
      </form>
      <noscript><p>Turn on JavaScript to search and filter the 24-center list.</p></noscript>
      <div class="results-bar">
        <p data-count>Loading centers…</p>
        <p class="muted">Each center is listed once.</p>
      </div>
      <div class="grid" data-property-grid></div>
      <div class="empty" data-empty hidden>
        <h2>No centers match these filters</h2>
        <p>Try another state, city, or size — or clear the filters to see the full portfolio.</p>
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
            "Five steps to lease retail space with Silver Bears, including application forms and background check.",
            "lease",
            """  <section class="page-hero">
    <div class="wrap">
      <p class="kicker">For tenants</p>
      <h1>How to lease</h1>
      <p class="lede">The old leasing page was a wall of legal text and three PDF buttons. This is the actual path: browse, pick a center, inquire, complete a credit check, then talk to leasing.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap steps">
      <article class="step">
        <div class="step-num">01</div>
        <div>
          <h2>Browse properties</h2>
          <p>Open the portfolio and filter by state, city, or available size. You will not be asked to hunt through a state mega-menu or a category list of retail types.</p>
          <p><a href="ROOT/properties/">Open the property list</a></p>
        </div>
      </article>
      <article class="step">
        <div class="step-num">02</div>
        <div>
          <h2>Pick a center</h2>
          <p>Open a center page for the address and the suites that are actually available. If a center is fully leased, it is marked that way. We do not ask you to choose a dummy lot that is not for lease.</p>
        </div>
      </article>
      <article class="step">
        <div class="step-num">03</div>
        <div>
          <h2>Send an inquiry or download forms</h2>
          <p>Use the inquiry form on a center page or on Contact. Name the center you want — not a dummy lot number. To apply, download the three forms below, complete them, and send them to leasing.</p>
          <div class="forms">
            <a class="form-link" href="ROOT/assets/forms/credit-check-authorization.pdf">Credit Check Authorization <span>PDF</span></a>
            <a class="form-link" href="ROOT/assets/forms/business-background.pdf">Business Background <span>PDF</span></a>
            <a class="form-link" href="ROOT/assets/forms/personal-financial-statement.pdf">Personal Financial Statement <span>PDF</span></a>
          </div>
        </div>
      </article>
      <article class="step">
        <div class="step-num">04</div>
        <div>
          <h2>Background and credit check</h2>
          <p>Every applicant goes through a financial background check. That usually means a look at credit history, and we may ask for more financial information. We can decline an application if the check raises concerns or if requested information is not provided. A security deposit or additional financial guarantee may be part of a lease. Submitting an application means you agree to that review — we use it only to decide whether we can offer you a space.</p>
        </div>
      </article>
      <article class="step">
        <div class="step-num">05</div>
        <div>
          <h2>Contact leasing</h2>
          <p>Questions about a suite, a form, or timing? Start with the leasing team.</p>
          <p>Jared Aberman, leasing representative<br>
          <a href="mailto:jared@silverbears.com">jared@silverbears.com</a> · <a href="tel:8883429378">888.342.9378</a></p>
          <p>Leasing inquiries<br>
          <a href="mailto:leasing@bearsmgmt.com">leasing@bearsmgmt.com</a></p>
          <p><a class="btn btn-primary" href="ROOT/contact/">Go to contact</a></p>
        </div>
      </article>
    </div>
  </section>""",
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
      <p class="kicker">Contact</p>
      <h1>Talk to leasing</h1>
      <p class="lede">Use the form for a space inquiry, or call. Maintenance requests are further down this page — they are not in the main navigation.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap contact-grid">
      <div class="panel contact-card">
        <h3>Leasing inquiries</h3>
        <p><a href="mailto:leasing@bearsmgmt.com">leasing@bearsmgmt.com</a><br>
        <a href="tel:8883429378">888.342.9378</a> (toll free)</p>
        <p>Jared Aberman, leasing representative<br>
        <a href="mailto:jared@silverbears.com">jared@silverbears.com</a></p>
      </div>
      <div class="panel contact-card">
        <h3>Office</h3>
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
        <p class="form-note">Choose a real shopping center, not a dummy lot. This form opens your email app to leasing@bearsmgmt.com.</p>
        <form data-mailto-form data-to="leasing@bearsmgmt.com">
          <input type="hidden" name="_subject" value="Leasing inquiry from silverbears.com">
          <label class="field">Name<input name="Name" required autocomplete="name"></label>
          <label class="field">Email<input type="email" name="Email" required autocomplete="email"></label>
          <label class="field">Phone<input type="tel" name="Phone" autocomplete="tel"></label>
          <label class="field">Property<select name="Property">{property_select()}</select></label>
          <label class="field">Message<textarea name="Message" required placeholder="What kind of space are you looking for?"></textarea></label>
          <p><button class="btn btn-primary" type="submit">Send inquiry</button></p>
        </form>
      </div>
      <div>
        <h2>How to lease</h2>
        <p>If you are ready to apply, download the forms and read the background-check step first.</p>
        <p><a class="btn btn-ghost" href="ROOT/how-to-lease/">How to lease</a></p>
        <div class="panel" id="maintenance" style="margin-top:24px">
          <h2>Maintenance report</h2>
          <p>Tenants: describe the issue and pick the shopping center. This is not in the header or the mobile menu.</p>
          <form data-mailto-form data-to="mary@silverbears.com">
            <input type="hidden" name="_subject" value="Maintenance report">
            <label class="field">Name<input name="Name" required></label>
            <label class="field">Email<input type="email" name="Email" required></label>
            <label class="field">Shopping center<select name="Shopping center" required>{property_select()}</select></label>
            <label class="field">What is wrong?<textarea name="Problem" required></textarea></label>
            <p><button class="btn btn-primary" type="submit">Report issue</button></p>
          </form>
        </div>
      </div>
    </div>
  </section>""",
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
      <p class="kicker">Legal</p>
      <h1>Privacy</h1>
      <p>This GitHub Pages site is a static marketing website. Inquiry and maintenance forms open your own email app; they do not store messages on this host.</p>
      <p>If you send us an email, we will use your name, contact details, and message to respond to a leasing or property-management request. Application forms you submit may include financial and identification information, which we use to evaluate a lease — see <a href="ROOT/how-to-lease/">How to lease</a>.</p>
      <p>This page is a short placeholder for the Pages deployment. The longer policy used on the current WordPress site remains at <a href="https://silverbears.com/privacy-policy/">silverbears.com/privacy-policy</a>. Privacy questions: <a href="mailto:privacy@silverbears.com">privacy@silverbears.com</a>.</p>
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
      <p class="kicker">Legal</p>
      <h1>Terms</h1>
      <p>This website describes shopping centers in the Silver Bears portfolio and how to inquire about leasing. Listings, suite sizes, and availability can change. Nothing here is an offer to lease until we sign a written agreement.</p>
      <p>Do not use this site for anything unlawful. Photos and property information are provided for prospective tenants and shoppers. Application forms are for genuine lease inquiries only.</p>
      <p>This page is a short placeholder for the Pages deployment. The live WordPress terms remain at <a href="https://silverbears.com/terms-and-conditions/">silverbears.com/terms-and-conditions</a>.</p>
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
      <p class="kicker">404</p>
      <h1>That page is not here.</h1>
      <p class="lede">No leftover sample pages, test forms, or duplicate city dumps. Try Home, Properties, How to lease, or Contact.</p>
      <p><a class="btn btn-primary" href="ROOT/index.html">Go home</a> <a class="btn btn-ghost" href="ROOT/properties/">Find space</a></p>
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
      <p class="kicker">Contact</p>
      <h1>Send the email to finish</h1>
      <p class="lede">This site cannot post messages by itself. If your email app opened, send the draft. If it did not, write directly to <a href="mailto:leasing@bearsmgmt.com">leasing@bearsmgmt.com</a>.</p>
      <p><a class="btn btn-primary" href="ROOT/properties/">Back to properties</a></p>
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

    # Keep first-version filenames so older PR links still resolve.
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
