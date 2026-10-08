# FrankKair.github.io

Frank's personal website: writing, reading and listening logs, films, travel and live performances. Built with Hugo and Python's standard library, published through GitHub Pages.

## Local preview

Use **Hugo 0.167.0** (the version pinned in CI) and **Python 3.11+** (CI uses 3.12). Your installed Hugo Extended also works; there is no need for a separate Hugo installation. There are no themes, pip or npm dependencies to install.

```sh
make serve      # generate collections, then preview at http://localhost:1313
make build      # generate collections, then build minified output in public/
make check      # generator tests, production build, rendered data/link/RSS checks
```

You can set `HUGO=/path/to/hugo` or `PYTHON=python3.12` when running Make. `public/` is generated output; `make build` removes obsolete files there. After editing a CSV during a preview, run `make generate` in a second terminal; Hugo reloads the generated pages.

## Add a collection entry

1. Edit the appropriate file in `csv/`, retaining its header and column count. Quote fields containing commas with CSV double quotes. Keep Unicode names and flags as written.
2. Insert the entry in the order you want it displayed within its year. Dates use `dd/mm/yyyy`; partial dates and bare years remain supported. Blank fields are shown as “not recorded”, not discarded.
3. Run `make check`, then commit the source CSV. Generated files are ignored by Git.

`publications.toml` controls category titles, descriptions, slugs, column labels, aliases, year grouping and statistics. To add a category, add a `[[publication]]` entry with a unique `slug`, `title` and `csv` path. Include `group_by` for a date column and `stats = ["country", "decade:year"]` as appropriate. Set `published = false` to hide a category; the generator removes only its marked generated files.

The generator writes **only** `content/collections/<slug>.md` and `data/collections/<slug>.json`. It preserves CSV order within years, sorts year groups newest first, and keeps undated entries in a final group. Ungrouped lists retain CSV order. Countries are flagged when known; existing flags and historical labels remain intact. Country and decade statistics retain the existing counting rules. CSV files are never rewritten.

## Publish a Markdown article

```sh
hugo new content writing/my-first-note.md
```

Edit `content/writing/my-first-note.md`. The writing archetype includes:

```toml
+++
title = 'My first note'
date = 2026-10-08T12:00:00+01:00
description = 'A short introduction for the article list.'
tags = ['Programming']
draft = true
+++
```

Write Markdown below the front matter. `make serve` includes drafts; set `draft = false` to publish. The date must not be in the future for a production build. Articles appear chronologically at `/writing/`, in the homepage's latest four entries, and in the RSS feed at `/writing/index.xml`. The generator never touches `content/writing/`.

Edit the introduction in `content/_index.md` and the About page in `content/about.md`. Only content under `content/` is published; loose notes in the repository root are not articles.

## Design

This is a self-contained Hugo site: templates live in `layouts/` and the single stylesheet is `assets/css/site.css`. Hugo uses these templates directly without a theme. The design follows the supplied reference: a quiet header, personal introduction, writing list and two-column collection overview. Colours follow the system light/dark preference. Collection tables have semantic headings, a keyboard-focusable horizontal scroll region and a visible scroll hint on narrow screens.

The former Cactus theme was removed once the custom templates covered every page. The only bundled assets are the site's own CSS and favicon, with no application JavaScript, font libraries, SCSS, external font, media API or frontend build chain.

## Deployment

Push or merge to `main` to trigger `.github/workflows/hugo.yaml`, or run it manually in GitHub Actions. It installs the pinned Hugo and Python versions, runs the generator tests, generates collections **before** `hugo --gc --minify`, checks rendered rows/links/RSS, uploads `public/` with `actions/upload-pages-artifact`, then deploys with `actions/deploy-pages`.

The repository's Pages source must remain **GitHub Actions**. `baseURL` is `https://frankkair.github.io/`; the workflow retains the URL supplied by `actions/configure-pages`, preserving Pages domain handling. This revamp does not change repository settings or publish from the feature branch.

## Existing links and verification

The five old collection URLs redirect from `/posts/<slug>/` to `/collections/<slug>/`: `books`, `books-to-read`, `music`, `movies` and `cinema-club`. `/posts/` and `/categories/` redirect to `/collections/`; the former first-page pagination URLs also redirect. `/tags/` remains available. `/index.xml` and `/posts/index.xml` now carry the writing feed alongside `/writing/index.xml`.

Old generated files under `content/posts/` were untracked. Their five exact filenames remain ignored by Git and Hugo so existing checkouts cannot shadow the redirects; no local files need to be deleted. Handwritten content and section introductions are now tracked.

See [the revamp audit](docs/website-revamp.md) for the baseline inventory, migration details and verification results. `make check` uses only Python's standard library and Hugo. Browser checks used the Mac's existing Firefox; no browser automation packages are required.
