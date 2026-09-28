#!/usr/bin/env python3
"""Build menu.html from data/menu.json.

The header, footer and SVG brush filters are copied from index.html (between the
<!-- shared:... --> markers) so both pages stay in sync.

Run from the repo root:  python3 scripts/build-menu.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.therichpourny.com"
DOORDASH = "https://www.doordash.com/store/the-rich-pour-bites-&amp;-beverage-house-massapequa-park-39579205/"

# Drinks first, then food, kids, and beans to take home
ORDER = [
    "Rich Pour Favorite Lattes",
    "Summer Lattes",
    "Summer Matchas",
    "Espresso Bar",
    "Coffee Counter",
    "The Cloud Bar (Cold Foam)",
    "The Tiki Bar: Refreshers",
    "Dirty Sodas",
    "Croffles",
    "The Croffle Lab",
    "Avocado Toast",
    "Pressed Paninis",
    "Mini Melts",
    "The Kiddo Cafe - Yummy Munchies",
    "The Kiddo Cafe - Happy Sips",
    "Bagged Coffee Beans",
]

# Display names where DoorDash's section name reads awkwardly on the site
RENAME = {
    "The Kiddo Cafe - Yummy Munchies": "The Kiddo Café: Yummy Munchies",
    "The Kiddo Cafe - Happy Sips": "The Kiddo Café: Happy Sips",
    "The Cloud Bar (Cold Foam)": "The Cloud Bar",
}

# Swash / dab colors cycle through the painted wall
SWASHES = [
    ("var(--pink)", "var(--violet)"),
    ("var(--lime)", "var(--sky)"),
    ("var(--sky)", "var(--pink)"),
    ("var(--violet)", "var(--lime)"),
]
DABS = ["var(--pink)", "var(--lime)", "var(--sky)", "var(--violet)", "#1c2a6b", "#f6c9dc"]


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def shared(block):
    src = (ROOT / "index.html").read_text()
    m = re.search(rf"    <!-- shared:{block} -->\n(.*?)    <!-- /shared:{block} -->", src, re.S)
    if not m:
        raise SystemExit(f"shared:{block} markers not found in index.html")
    return m.group(1)


def e(text):
    return html.escape(text or "", quote=True)


def dish(item):
    popular = '<span class="dish-tag">Popular</span>' if item.get("popular") else ""
    price = f'<span class="dish-price">{e(item["price"])}</span>' if item.get("price") else ""
    desc = f'<p>{e(item["description"])}</p>' if item.get("description") else ""
    photo = ""
    if item.get("photo"):
        photo = (f'<img src="/{e(item["photo"])}" alt="{e(item["name"])}" '
                 f'width="560" height="560" loading="lazy" decoding="async">')
    cls = "dish" if photo else "dish no-photo"
    return f"""                    <article class="{cls}">
                        {photo}
                        <div class="dish-body">
                            <h3><span>{e(item["name"])}</span>{price}</h3>
                            {desc}
                            {popular}
                        </div>
                    </article>"""


def json_ld(sections):
    def price(p):
        return (p or "").replace("$", "")

    return {
        "@context": "https://schema.org",
        "@type": "Menu",
        "name": "The Rich Pour menu",
        "url": f"{SITE}/menu.html",
        "inLanguage": "en-US",
        "hasMenuSection": [
            {
                "@type": "MenuSection",
                "name": RENAME.get(s["name"], s["name"]),
                "hasMenuItem": [
                    {
                        "@type": "MenuItem",
                        "name": i["name"],
                        **({"description": i["description"]} if i.get("description") else {}),
                        **({"image": f'{SITE}/{i["photo"]}'} if i.get("photo") else {}),
                        **({"offers": {"@type": "Offer", "price": price(i["price"]), "priceCurrency": "USD"}}
                           if i.get("price") else {}),
                    }
                    for i in s["items"]
                ],
            }
            for s in sections
        ],
    }


def main():
    data = json.loads((ROOT / "data/menu.json").read_text())
    by_name = {s["name"]: s for s in data["sections"]}
    sections = [by_name[n] for n in ORDER if n in by_name]
    sections += [s for s in data["sections"] if s["name"] not in ORDER]

    # Links in the shared header point at home-page sections
    header = shared("header").replace('href="#', 'href="/#')
    header = header.replace('<a href="/menu.html">Menu</a>',
                            '<a href="/menu.html" class="is-page" aria-current="page">Menu</a>')

    chips, blocks = [], []
    for n, s in enumerate(sections):
        name = RENAME.get(s["name"], s["name"])
        sid = slug(name)
        a, b = SWASHES[n % len(SWASHES)]
        chips.append(f'                <li><a href="#{sid}" style="--dab: {DABS[n % len(DABS)]}">{e(name)}</a></li>')
        dishes = "\n".join(dish(i) for i in s["items"])
        blocks.append(f"""        <section class="menu-sec" id="{sid}" style="--swash-a: {a}; --swash-b: {b};">
            <div class="wrap">
                <h2 class="section-title">{e(name)}</h2>
                <div class="dish-grid">
{dishes}
                </div>
            </div>
        </section>""")

    ld = json.dumps(json_ld(sections), indent=2, ensure_ascii=False).replace("</", "<\\/")
    count = sum(len(s["items"]) for s in sections)

    page = f"""<!DOCTYPE html>
<!-- Generated by scripts/build-menu.py from data/menu.json. Edit those, not this file. -->
<html lang="en" class="no-js">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Menu | The Rich Pour, Massapequa Park, NY</title>
    <meta name="description" content="The full Rich Pour menu: signature lattes, matcha, espresso, cold foam, refreshers, dirty sodas, croffles, avocado toast, paninis and more in Massapequa Park, NY.">
    <link rel="canonical" href="{SITE}/menu.html">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <meta name="theme-color" content="#0a4d66">

    <meta property="og:type" content="website">
    <meta property="og:site_name" content="The Rich Pour">
    <meta property="og:locale" content="en_US">
    <meta property="og:url" content="{SITE}/menu.html">
    <meta property="og:title" content="Menu | The Rich Pour">
    <meta property="og:description" content="Signature lattes, matcha, refreshers, croffles, avocado toast and paninis in Massapequa Park, NY.">
    <meta property="og:image" content="{SITE}/images/share-card.jpg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="The Rich Pour logo beside the café's espresso machine in front of its painted wall">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Menu | The Rich Pour">
    <meta name="twitter:description" content="Signature lattes, matcha, refreshers, croffles, avocado toast and paninis.">
    <meta name="twitter:image" content="{SITE}/images/share-card.jpg">

    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Gloock&family=Schibsted+Grotesk:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/styles.css">

    <script type="application/ld+json">
{ld}
    </script>
</head>
<body>
    <div class="sheen" aria-hidden="true"></div>
{shared("defs")}
{header}

    <main id="top" class="menu-page">
        <section class="menu-hero">
            <div class="wrap">
                <h1 class="section-title">Menu</h1>
                <p class="menu-intro">Everything we pour and plate, from signature lattes to croffles.</p>
                <div class="actions">
                    <a class="btn btn-solid" href="{DOORDASH}" target="_blank" rel="noopener">Order on DoorDash</a>
                </div>
                <p class="menu-fineprint">Prices are from our DoorDash menu and may differ in the café.</p>
            </div>
        </section>

        <nav class="menu-jump" aria-label="Menu sections">
            <ul class="wrap">
{chr(10).join(chips)}
            </ul>
        </nav>

{chr(10).join(blocks)}
    </main>

{shared("footer")}
    <script src="/site.js"></script>
</body>
</html>
"""
    (ROOT / "menu.html").write_text(page)
    print(f"menu.html: {len(sections)} sections, {count} items")


if __name__ == "__main__":
    main()
