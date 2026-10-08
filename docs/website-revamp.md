# Website revamp notes

## What changed

The former Cactus site published five CSV logs as timestamped, untracked posts. The redesign separates authored writing from generated collections and publishes all nine logs. CSV source files and root-level notes were left untouched.

- **Design:** custom Hugo templates and one stylesheet, with system light/dark mode, readable articles, accessible navigation and contained scrolling for collection tables.
- **Generation:** deterministic Markdown and JSON; all fields, flags, partial dates and blank entries retained. Years sort newest first, with CSV order preserved within each year and an explicit Undated group. Statistics retain the existing country/decade rules.
- **Cleanup:** removed Cactus’s 144 files and 59 unused published assets. Hugo remains the build engine. CI pins 0.167.0 to match the local version, without theme installation, submodules, Sass or Node.
- **Deployment:** the existing GitHub Actions → Pages deployment model remains; Python 3.12 generates collections before Hugo builds.

## Collections and routes

Counts are the **8 October 2026 migration baseline**, not hard-coded totals.

| CSV source | Entries | URL under `/collections/` |
| --- | ---: | --- |
| `books.csv` | 165 | `books/` |
| `movies.csv` | 86 | `movies/` |
| `music.csv` | 251 | `music/` |
| `travelling.csv` | 34 | `travel/` |
| `Concerts.csv` | 81 | `concerts/` |
| `cinema-club.csv` | 28 | `cinema-club/` |
| `books-to-read.csv` | 191 | `books-to-read/` |
| `recs-movie.csv` | 77 | `film-recommendations/` |
| `recs-music.csv` | 9 | `music-recommendations/` |
| **Total** | **922** | |

The five former `/posts/<slug>/` routes redirect to their collection pages: `books`, `movies`, `music`, `cinema-club` and `books-to-read`. `/posts/`, `/posts/page/1/` and `/categories/` redirect to `/collections/`; `/page/1/` redirects home. `/tags/` remains available. `/index.xml` and `/posts/index.xml` serve the writing feed alongside `/writing/index.xml`.

The five legacy generated filenames remain ignored by Git and Hugo, preventing old local output from shadowing redirects.

## Verification

- All nine CSV hashes unchanged; all **922 entries** preserved. The 721 previously published entries match the baseline after accounting for Markdown smart punctuation and regrouping undated films.
- Seven standard-library tests cover data preservation, statistics, dates, repeatability, source/article protection, malformed input and unpublishing. Built-page checks validate every collection cell, redirects, internal links and RSS.
- Repeated builds were byte-identical. After theme removal, `make check` passed with installed Hugo 0.167.0 without warnings; CSS was unchanged.
- Firefox checked 14 pages, including a temporary article, at **320, 375, 768 and 1440px** in light/dark mode: **112 combinations**. No page overflow; table scrolling, expanded statistics and keyboard focus worked. Body and muted text contrast exceeded 4.5:1.

The temporary article and testing packages were removed. Live Pages deployment and other browser engines were not tested. For authoring and preview commands, see [the README](../README.md).
