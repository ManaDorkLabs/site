# Mana Dork Labs

Source for [manadorklabs.com](https://manadorklabs.com). Static HTML with no
build step and no dependencies.

## Pages

| Path       | File            | Notes                                          |
| ---------- | --------------- | ---------------------------------------------- |
| `/`        | `index.html`    | Wordmark holding page                          |
| `/vision`  | `vision.html`   | What we're building                            |
| `/why`     | `why.html`      | The cooperativism case                         |
| `/roadmap` | `roadmap.html`  | Stages, with the current one marked            |
| `/agora`   | `agora.html`    | Proof of concept — name and market not settled |
| `/team`    | `team.html`     | Ethos and bios — motivations still to be written |

Raw source notes for the copy live in `content/`.

## Local preview

```bash
python serve.py
```

Then open `http://localhost:8080`. Links are written without the `.html`
extension to match Vercel's `cleanUrls`, so use `serve.py` rather than
`python -m http.server`, which would 404 on them.

## Stack

Plain HTML and CSS, shared through `assets/site.css`. Type is
[Jura](https://fonts.google.com/specimen/Jura) and
[Space Mono](https://fonts.google.com/specimen/Space+Mono), loaded from Google
Fonts. Deployed on Vercel; response headers are configured in `vercel.json`.
