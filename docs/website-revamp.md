# Website revamp audit

## Baseline — 8 October 2026

The repository used Hugo Extended 0.124.0 and a tracked, vendored copy of Cactus (not a submodule). `generate-markdowns.py` read five entries in `publications.toml`, wrote untracked Markdown to `content/posts/<Title>.md`, and stamped it with the current time. The broad `content/*` ignore rule also prevented authored articles from being tracked. The generator and production baseline build completed locally; Cactus emitted one existing `IsSet` warning.

GitHub Actions built on pushes to `main` and manual dispatch. It installed Hugo, generated Markdown, used `actions/configure-pages`, built `public/`, uploaded a Pages artifact and deployed it via `actions/deploy-pages`. There was no CNAME file or custom domain configuration in the repository. The new workflow preserves this model and Hugo pin, specifies Python 3.12 for `tomllib`, removes unused Sass/Node installation steps, and adds data verification.

## Data inventory and routes

Every row and meaningful field in all nine source CSV files is preserved. Counts below are the migration baseline, not values hard-coded in the generator.

| Source | Entries | Former URL | Current URL |
| --- | ---: | --- | --- |
| `csv/books.csv` | 165 | `/posts/books/` | `/collections/books/` |
| `csv/movies.csv` | 86 | `/posts/movies/` | `/collections/movies/` |
| `csv/music.csv` | 251 | `/posts/music/` | `/collections/music/` |
| `csv/travelling.csv` | 34 | Not published | `/collections/travel/` |
| `csv/Concerts.csv` | 81 | Not published | `/collections/concerts/` |
| `csv/cinema-club.csv` | 28 | `/posts/cinema-club/` | `/collections/cinema-club/` |
| `csv/books-to-read.csv` | 191 | `/posts/books-to-read/` | `/collections/books-to-read/` |
| `csv/recs-movie.csv` | 77 | Not published | `/collections/film-recommendations/` |
| `csv/recs-music.csv` | 9 | Not published | `/collections/music-recommendations/` |
| **Total** | **922** | | |

The five formerly published collections contain 721 entries. The four newly exposed logs add 201. The original tables, countries, flags, date strings and music decade statistics were captured before edits for comparison. No existing interactive filters or sorting controls were present. Year anchors and native collapsible statistics now provide navigation without JavaScript.

Aliases preserve the five old collection URLs, `/posts/`, `/posts/page/1/`, `/page/1/` and `/categories/`. Tags retain their route; root and posts RSS URLs now serve writing. Redirects are static Hugo alias pages with canonical URLs and meta refresh.

Display names now use “Films” for `movies.csv`, “Travel” for `travelling.csv`, and “Concerts & theatre” for the log containing both concerts and stage shows. The concert description includes plans because the source contains a future event. CSV filenames, values and dates are unchanged. Incomplete book entries, historical countries, partial dates and blank recommendation dates remain represented.

Root-level untracked language notes and `nobel_literature.csv` were outside the original publication configuration and `csv/` logs. They were left untouched and are not silently published as articles or collections.

## Implementation

- Keep Cactus with site-level overrides; the PaperMod compatibility assessment and rationale are in the README. No theme source files changed.
- Authored content lives in `content/writing/`, `content/about.md` and section introductions. A writing archetype supplies dates, summaries, optional tags and draft status.
- Generated collection Markdown contains deterministic front matter. JSON data retains all columns, grouped rows, counts and statistics for shared Hugo table layouts. Generation validates every CSV before writing and refuses to overwrite unmarked authored collection pages.
- The header, footer, article, index, collection and RSS templates use local CSS and system fonts. Collections have a wider reading area; articles use a 70-character measure. The site follows system light/dark preference, includes a skip link and visible focus outlines, and uses scrollable semantic tables.

## Verification

- Seven standard-library tests cover complete CSV field/row preservation, flags and statistics, partial/unknown dates, deterministic generation, source/article immutability, malformed input and safe removal of unpublished generated pages.
- Production HTML verification compares every rendered collection cell and row in order, validates old URL redirects, checks internal links/anchors and parses all three writing RSS routes.
- CSV hashes and the five baseline rendered tables were compared before/after; no source bytes or entries changed. Comparisons account for the old Markdown renderer's smart quotes/ellipses and the new explicit Undated group. Collection cells now show the source punctuation directly; undated films move into their own group rather than appearing among dated entries.
- Two consecutive production builds and generations were compared byte-for-byte, including generated content/data and published output.
- The existing Firefox installation checked homepage, writing index, temporary Markdown article, About, collections overview and all nine collections at **320, 375, 768 and 1440px**, in both colour schemes: **112 page/viewport/theme checks**. No page-level horizontal overflow; mobile table scrolling and opened statistics remained contained. Screenshots of homepage, article and collection layouts were inspected. The temporary test article was removed afterward.
- Native keyboard navigation reached the visible skip link. Body/muted text contrast measured 13.60:1 / 5.46:1 in light mode and 14.21:1 / 8.29:1 in dark mode.
- Temporary browser packages and downloads were removed. No Chromium/Chrome was installed; Firefox testing used a temporary profile and Python's standard library.

Live GitHub Pages deployment and other browser engines were not exercised. The feature branch must be merged/pushed to `main` to deploy. External GitHub links were checked for correct destinations, not exhaustively network-crawled.
