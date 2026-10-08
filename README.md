# FrankKair.github.io

```text
Writing & About (Markdown) -----------------+
                                            |
Collections (CSV) --> Python ---------------+--> Hugo
                     flags, years & stats   |      |
                                            |      v
Design (templates + CSS) -------------------+   public/
                                               HTML + CSS
                                                   |
                                                   v
                                              GitHub Pages
```

Dependencies: `Python 3.11+` and [`Hugo`](https://gohugo.io/).

## Usage

```
$ make

generate     Regenerate collections from CSV
serve        Preview drafts at http://localhost:1313
build        Build into public/ and remove stale output
test         Run generator tests
check        Test, build, and verify data, links and RSS
help         Show commands
```

Writing: `hugo new content writing/my-note.md`

Collections: Edit `csv/`; define categories in `publications.toml`. 

Deploy: Push to `main`; GitHub Actions builds and deploys to GitHub Pages.
