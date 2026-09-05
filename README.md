# Mana Dork Labs

Source for [manadorklabs.com](https://manadorklabs.com). Static HTML, no
dependencies.

## Editing the copy

All of the site's words live in `content/pages/` — one text file per page.
Edit the text, then run:

```bash
python build.py
```

That rewrites the `.html` files at the repo root. Commit both the content file
and the rebuilt HTML; Vercel serves the HTML as-is and does not run the build.

The format is documented in [content/pages/README.md](content/pages/README.md).
It is a handful of conventions — `## heading`, `- bullet`, `> quote`, and four
`:::` blocks for the layouts that need more structure.

## Local preview

```bash
python serve.py
```

Then open `http://localhost:8080`. It rebuilds before serving each page, so
you can edit a content file and just refresh. Links are written without the
`.html` extension to match Vercel's `cleanUrls`, which is why this exists
rather than `python -m http.server`.

## Pages

| Path       | Content file               | Notes                                            |
| ---------- | -------------------------- | ------------------------------------------------ |
| `/`        | `content/pages/index.txt`  | Wordmark, tagline, chips                         |
| `/vision`  | `content/pages/vision.txt` | What we're building                              |
| `/why`     | `content/pages/why.txt`    | The cooperativism case                           |
| `/roadmap` | `content/pages/roadmap.txt`| Stages, with the current one marked              |
| `/agora`   | `content/pages/agora.txt`  | Proof of concept — name and market not settled   |
| `/team`    | `content/pages/team.txt`   | Ethos and bios — motivations still to be written |

Adding a page means adding a file; the top-bar nav is built from the page
headers. The original notes the copy came from are in
`content/things-to-put-on-the-website.md`.

## Stack

Plain HTML and CSS. Layout and type live in `assets/site.css`; `build.py`
supplies the page structure around them. Type is
[Jura](https://fonts.google.com/specimen/Jura) and
[Space Mono](https://fonts.google.com/specimen/Space+Mono), loaded from Google
Fonts. Deployed on Vercel; response headers are configured in `vercel.json`.
