# Editing the site copy

One file here is one page. Edit the text and commit it — Vercel rebuilds the
site on every push, so there is nothing to regenerate by hand. To see a change
before pushing, run `python serve.py` from the repo root and refresh the
browser; it rebuilds on every request.

The filename is the URL: `why.txt` becomes `/why`. `index.txt` is the home
page and is the one page with a different shape (see the bottom of this file).

## The header

Everything above the first blank line is `key: value` settings.

```
title: Why cooperatives -- Mana Dork Labs
description: What search engines and link previews show.
nav: The Why
order: 2
eyebrow: The Why
heading: Why cooperatives
lede: The one sentence under the big heading.
links:
- /vision | The Vision
- mailto:hello@manadorklabs.com | Get in touch
```

- `nav` is the top-bar label. Leave it out to keep a page off the nav.
- `order` sorts the nav, low to high.
- `eyebrow` is the small green label above the heading.
- `heading` is the big Jura heading. `lede` is optional.
- `links` are the bordered links at the bottom, written as `href | label`.

Adding a page is adding a file with a header; deleting one is deleting the
file. The build writes a fresh `dist/` each time, so nothing lingers.

## The body

Everything after the first blank line. Blank lines separate paragraphs; a
paragraph can be spread across as many lines as you like.

```
## A section heading

An ordinary paragraph. Use **bold** and *italic* for emphasis, [a link](/why)
for links, and -- for an em dash. Apostrophes are curled for you.

> A pull quote, set off with a green rule.
> It can run to several lines.

- A bullet
- Another bullet
```

A line starting with `//` is a note to yourself. It is stripped out and never
reaches the page — useful for parking a line you are not ready to publish.

## The special blocks

Four layouts need more than paragraphs, so they are fenced with `:::`.

**Two columns of costs**, as on The Why:

```
:::compare
### Cooperative costs
- Collective bargaining
- Meeting overhead
### Capitalist costs
- Management surveillance
- Dividend payments
:::
```

**The values row**, as on The Team:

```
:::values
- Leave the world better than we found it.
- Strive to enable agency for all people.
:::
```

**The roadmap stages.** `[now]` marks the current one and gives it the green
square and the "Current" tag. Move it down the list as you go.

```
:::stages
- [now] Develop the core technology
- Find the proof of concept marketplace
:::
```

**People.** `photo:` takes a file in `assets/` — leave it blank for the empty
headshot slot. `draft:` is the dashed placeholder box, written as
`label | text`.

```
:::people
### Rob

photo: /assets/rob.jpg

Aerospace engineer with experience operating in a fast-paced environment.

draft: Motivation -- to write | Rob's own words, in a form fit to publish.
:::
```

**A standalone placeholder**, as on The Agora. The words after `:::draft` are
its label:

```
:::draft Not yet announced
The name is a work in progress.
:::
```

## The home page

`index.txt` is header-only — no body. It sets the line under the wordmark and
the three words in the box:

```
tagline: Infrastructure for marketplace cooperatives.
chips:
- Transact
- Govern
- Own
```

The MANA / DORK / LABS grid itself is the logo, so it lives in `build.py`
rather than here.

## If the build complains

`python build.py` prints the error and stops without writing anything. The
usual causes are a `:::` fence that was never closed, or a block name that
isn't one of the four above. It also warns about `ignoring unknown setting`,
which nearly always means a `- ` list in the header lost the `key:` line above
it — the list is then silently dropped, so it is worth heeding.

Note that a build failure fails the whole Vercel deployment, which leaves the
last good version live rather than breaking the site.
