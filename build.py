"""Build the site's HTML pages from the text files in content/pages/.

Run `python build.py`. Every .txt file in content/pages/ becomes one page in
dist/, alongside a copy of assets/, and the top-bar nav is assembled from their
headers, so adding a page is a matter of adding a file. dist/ is what Vercel
deploys and is not checked in. `python serve.py` runs this for you on
every request, so while previewing locally you only need to save and refresh.

The markup the content files use is documented in content/pages/README.md.
Nothing here is imported by the site itself: the output is plain static HTML.
"""

import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PAGES = ROOT / "content" / "pages"
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"  # what gets deployed; not checked in

FONTS = "https://fonts.googleapis.com/css2?family=Jura:wght@300..700&family=Space+Mono:wght@400;700&display=swap"
FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' fill='%230b0d0b'/%3E"
    "%3Crect x='6' y='6' width='5' height='20' fill='%234f8f74'/%3E"
    "%3Crect x='13' y='6' width='4' height='4' fill='%23ede7d8'/%3E"
    "%3Crect x='19' y='6' width='4' height='4' fill='%23ede7d8'/%3E"
    "%3Crect x='13' y='14' width='4' height='4' fill='%23ede7d8'/%3E"
    "%3Crect x='19' y='14' width='4' height='4' fill='%23ede7d8'/%3E"
    "%3Crect x='13' y='22' width='4' height='4' fill='%23ede7d8'/%3E"
    "%3Crect x='19' y='22' width='4' height='4' fill='%23ede7d8'/%3E%3C/svg%3E"
)
FOOTER_NOTE = "In formation &middot; 2026"
CONTACT = "mailto:hello@manadorklabs.com"


# --- text -> html -------------------------------------------------------


def inline(text):
    """Escape a line and apply the few inline marks the content files use."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\*(.+?)\*", r"<em>\1</em>", out)  # after **bold**, so pairs are left
    out = out.replace("--", "&mdash;").replace("'", "&rsquo;")
    return out


def split_header(raw):
    """Split a content file into its `key: value` header and its body."""
    header, body, key = {}, [], None
    lines = raw.replace("\r\n", "\n").split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            body = lines[i + 1 :]
            break
        if line.startswith("- ") and isinstance(header.get(key), list):
            header[key].append(line[2:].strip())
        else:
            key, _, value = line.partition(":")
            key = key.strip()
            # A key with nothing after the colon collects the `- ` lines below it.
            header[key] = value.strip() if value.strip() else []
    return header, body


KNOWN_KEYS = {
    "title", "description", "nav", "order", "eyebrow", "heading", "lede",
    "links", "tagline", "chips",
}


def check_keys(header, name):
    """Warn about header keys we do not recognise.

    Almost always a `- ` list that lost the key above it, which would
    otherwise just go quiet: the block it belonged to simply stops rendering.
    """
    for key in header:
        if key not in KNOWN_KEYS:
            print(f"  {name}: ignoring unknown setting '{key}'", file=sys.stderr)


def paragraphs(lines):
    """Group lines into blank-line-separated chunks."""
    chunks, current = [], []
    for line in lines:
        if line.strip():
            current.append(line.strip())
        elif current:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def link_row(items, cls):
    """Render `href | label` pairs as a row of bordered links."""
    out = [f'    <div class="{cls}">']
    for item in items:
        href, _, label = item.partition("|")
        out.append(f'      <a href="{href.strip()}">{inline(label.strip())}</a>')
    out.append("    </div>")
    return out


# --- the fenced blocks --------------------------------------------------


def render_values(lines):
    out = ['    <ul class="values">']
    for line in lines:
        if line.startswith("- "):
            out.append(f"      <li>{inline(line[2:].strip())}</li>")
    out.append("    </ul>")
    return out


def render_compare(lines):
    out = ['    <div class="compare">']
    open_column = False
    for line in lines:
        if line.startswith("### "):
            if open_column:
                out += ["        </ul>", "      </section>"]
            out.append("      <section>")
            out.append(f"        <h3>{inline(line[4:].strip())}</h3>")
            out.append("        <ul>")
            open_column = True
        elif line.startswith("- "):
            out.append(f"          <li>{inline(line[2:].strip())}</li>")
    if open_column:
        out += ["        </ul>", "      </section>"]
    out.append("    </div>")
    return out


def render_stages(lines):
    out = ['    <ol class="stages">']
    for line in lines:
        if not line.startswith("- "):
            continue
        text = line[2:].strip()
        current = text.startswith("[now]")
        if current:
            text = text[5:].strip()
        tag = '<span class="tag">Current</span>' if current else ""
        out.append(f'      <li class="now">' if current else "      <li>")
        out.append(f"        <b>{inline(text)}{tag}</b>")
        out.append("      </li>")
    out.append("    </ol>")
    return out


def render_people(lines):
    """Each `### Name` starts a card. `photo:` sets the headshot (blank leaves
    the empty slot), `draft: label | text` adds a dashed placeholder note."""
    people, person = [], None
    for chunk in paragraphs(lines):
        if chunk.startswith("### "):
            person = {"name": chunk[4:].strip(), "photo": "", "parts": []}
            people.append(person)
        elif person is None:
            continue
        elif chunk.startswith("photo:"):
            person["photo"] = chunk.split(":", 1)[1].strip()
        elif chunk.startswith("draft:"):
            label, _, text = chunk[6:].partition("|")
            person["parts"].append(("draft", label.strip(), text.strip()))
        else:
            person["parts"].append(("p", chunk, ""))

    out = ['    <div class="people">']
    for person in people:
        out.append("      <article>")
        if person["photo"]:
            src = html.escape(person["photo"], quote=True)
            alt = html.escape(person["name"], quote=True)
            out.append(f'        <div class="shot"><img src="{src}" alt="{alt}"></div>')
        else:
            out.append('        <div class="shot"><span>Headshot</span></div>')
        out.append(f'        <h3>{inline(person["name"])}</h3>')
        for kind, a, b in person["parts"]:
            if kind == "p":
                out.append(f"        <p>{inline(a)}</p>")
            else:
                out.append('        <div class="draft">')
                out.append(f"          <b>{inline(a)}</b>")
                out.append(f"          {inline(b)}")
                out.append("        </div>")
        out.append("      </article>")
    out.append("    </div>")
    return out


def render_draft(lines, label):
    out = ['    <div class="draft">']
    out.append(f"      <b>{inline(label)}</b>")
    for chunk in paragraphs(lines):
        out.append(f"      {inline(chunk)}")
    out.append("    </div>")
    return out


FENCES = {
    "values": render_values,
    "compare": render_compare,
    "stages": render_stages,
    "people": render_people,
}


def render_body(lines):
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(":::"):
            name, _, label = line[3:].strip().partition(" ")
            block, i = [], i + 1
            while i < len(lines) and not lines[i].startswith(":::"):
                block.append(lines[i])
                i += 1
            i += 1
            if name == "draft":
                out += render_draft(block, label or "Draft")
            elif name in FENCES:
                out += FENCES[name](block)
            else:
                raise SystemExit(f"unknown block ':::{name}'")
            continue
        if line.startswith("## "):
            out.append(f"    <h2>{inline(line[3:].strip())}</h2>")
            i += 1
            continue
        if line.startswith("- "):
            out.append('    <ul class="list">')
            while i < len(lines) and lines[i].startswith("- "):
                out.append(f"      <li>{inline(lines[i][2:].strip())}</li>")
                i += 1
            out.append("    </ul>")
            continue
        if line.startswith("> "):
            quote = []
            while i < len(lines) and lines[i].startswith("> "):
                quote.append(lines[i][2:].strip())
                i += 1
            out.append(f'    <p class="pull">{inline(" ".join(quote))}</p>')
            continue
        if line.strip():
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i][0] in "#->:":
                para.append(lines[i].strip())
                i += 1
            if para:
                out.append(f'    <p>{inline(" ".join(para))}</p>')
            else:
                i += 1
            continue
        i += 1
    return out


# --- page assembly ------------------------------------------------------


def meta_text(value):
    """Titles and descriptions: escaped, with `--` spelled as an em dash."""
    return html.escape(value, quote=True).replace("--", "&mdash;")


def head(page, nav_pages):
    title = meta_text(page["title_tag"])
    desc = meta_text(page.get("description", ""))
    kind = "website" if page["slug"] == "index" else "article"
    return [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{title}</title>",
        f'<meta name="description" content="{desc}">',
        '<meta name="robots" content="index, follow">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{desc}">',
        f'<meta property="og:type" content="{kind}">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link href="{FONTS}" rel="stylesheet">',
        '<link rel="stylesheet" href="/assets/site.css">',
        f'<link rel="icon" href="{FAVICON}">',
        "</head>",
        "<body>",
        "",
    ]


def top_bar(page, nav_pages):
    if page["slug"] == "index":
        brand = '    <p class="micro">Mana Dork Labs</p>'
    else:
        brand = '    <a class="brand" href="/">Mana Dork Labs</a>'
    out = ['  <header class="bar bar--top">', brand]
    out.append('    <nav class="nav" aria-label="Primary">')
    for other in nav_pages:
        here = ' aria-current="page"' if other["slug"] == page["slug"] else ""
        out.append(f'      <a href="/{other["slug"]}"{here}>{other["nav"]}</a>')
    out += ["    </nav>", "  </header>", ""]
    return out


def home_main(page):
    out = ['  <main class="stage">']
    out.append('    <div class="mark" role="img" aria-label="Mana Dork Labs">')
    out.append('      <span class="colrule"></span>')
    for row in ("MANA", "DORK", "LABS"):
        cells = [
            f'<span class="cell key">{row[0]}</span>'
            if i == 0
            else f'<span class="cell">{c}</span>'
            for i, c in enumerate(row)
        ]
        out.append("      " + "".join(cells))
    out.append("    </div>")
    out.append("")
    out.append(f'    <p class="tagline">{inline(page["tagline"])}</p>')
    out.append("")
    chips = "<s>/</s>".join(f"<b>{inline(c)}</b>" for c in page.get("chips", []))
    out += ['    <div class="chips">', f"      {chips}", "    </div>", "  </main>", ""]
    return out


def content_main(page):
    out = ['  <main class="page">']
    out.append(f'    <p class="eyebrow">{inline(page["eyebrow"])}</p>')
    out.append(f'    <h1>{inline(page["heading"])}</h1>')
    if page.get("lede"):
        out.append(f'    <p class="lede">{inline(page["lede"])}</p>')
    out.append("")
    out += render_body(page["body"])
    if page.get("links"):
        out.append("")
        out += link_row(page["links"], "next")
    out += ["  </main>", ""]
    return out


def footer():
    return [
        '  <footer class="bar bar--bottom">',
        f'    <p class="micro">{FOOTER_NOTE}</p>',
        f'    <a class="contact" href="{CONTACT}">Get in touch</a>',
        "  </footer>",
        "",
        "</body>",
        "</html>",
        "",
    ]


def build():
    pages = []
    for path in sorted(PAGES.glob("*.txt")):
        header, body = split_header(path.read_text(encoding="utf-8"))
        check_keys(header, path.name)
        header["slug"] = path.stem
        # `// ...` lines are notes to ourselves; they never reach the page.
        header["body"] = [l for l in body if not l.lstrip().startswith("//")]
        header["title_tag"] = header.get("title", "Mana Dork Labs")
        pages.append(header)

    nav_pages = sorted(
        (p for p in pages if p.get("nav")), key=lambda p: int(p.get("order", 99))
    )

    # Render everything before writing anything, so a typo in one content file
    # leaves the built site untouched rather than half-updated.
    rendered = {}
    for page in pages:
        lines = head(page, nav_pages) + top_bar(page, nav_pages)
        lines += home_main(page) if page["slug"] == "index" else content_main(page)
        lines += footer()
        name = "index.html" if page["slug"] == "index" else f'{page["slug"]}.html'
        rendered[name] = "\n".join(lines)

    # A fresh dist/ each time, so a page deleted from content/pages/ stops
    # being deployed instead of lingering as a stale file.
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for name, text in rendered.items():
        (DIST / name).write_text(text, encoding="utf-8")
    shutil.copytree(ASSETS, DIST / "assets")
    return sorted(rendered)


if __name__ == "__main__":
    names = build()
    print(f"built {len(names)} pages: {', '.join(names)}", file=sys.stderr)
