"""
Check built collection rows, legacy routes, internal links and RSS.
No packages.
"""

import json
import sys
import tomllib
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.rows = []
        self.links = []
        self.ids = set()
        self.refresh = None
        self.canonical = None
        self.in_log = False
        self.row = None
        self.cell = None
        self.missing = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag in {"a", "link"} and "href" in attrs:
            self.links.append(attrs["href"])
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs["href"]
        if tag in {"img", "script"} and "src" in attrs:
            self.links.append(attrs["src"])
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            self.refresh = attrs["content"].split("url=", 1)[-1]
        if tag == "table":
            self.in_log = "log-table" in attrs.get("class", "").split()
        if tag == "tr" and self.in_log:
            self.row = []
        if tag == "td" and self.in_log:
            self.cell = ""
            self.missing = False
        if tag == "span" and attrs.get("class") == "missing":
            self.missing = True

    def handle_data(self, text):
        if self.cell is not None:
            self.cell += text

    def handle_endtag(self, tag):
        if tag == "td" and self.cell is not None:
            self.row.append("" if self.missing else self.cell.strip())
            self.cell = None
        if tag == "tr" and self.in_log and self.row:
            self.rows.append(self.row)
        if tag == "table":
            self.in_log = False


def verify(destination):
    publications = tomllib.loads(
        (ROOT / "publications.toml").read_text()
    )["publication"]
    pages = {
        path: Page(path.read_text(encoding="utf-8"))
        for path in destination.rglob("*.html")
    }
    # Respect the Pages baseURL override (including a future custom domain).
    origin = pages[destination / "index.html"].canonical
    assert origin, "Homepage canonical URL is missing"
    total = 0
    for publication in publications:
        if not publication.get("published", True):
            continue
        slug = publication["slug"]
        data = json.loads(
            (ROOT / "data/collections" / f"{slug}.json").read_text()
        )
        page = pages[destination / "collections" / slug / "index.html"]
        expected = [
            [field.strip() for field in row]
            for group in data["groups"]
            for row in group["rows"]
        ]
        assert page.rows == expected, f"Rendered entries differ: {slug}"
        total += len(page.rows)
        for alias in publication.get("aliases", []):
            redirect = pages[
                destination / alias.strip("/") / "index.html"
            ].refresh
            assert redirect == urljoin(origin, f"collections/{slug}/"), (
                alias, redirect
            )

    aliases = {
        "posts": "collections/",
        "posts/page/1": "collections/",
        "categories": "collections/",
        "page/1": "",
    }
    for old, new in aliases.items():
        redirect = pages[destination / old / "index.html"].refresh
        assert redirect == urljoin(origin, new), old

    for path, page in pages.items():
        source = urljoin(origin, str(path.relative_to(destination)))
        for href in page.links:
            link = urlsplit(urljoin(source, href))
            if (
                link.scheme not in {"http", "https"}
                or link.netloc != urlsplit(origin).netloc
            ):
                continue
            target = destination / unquote(link.path).lstrip("/")
            if target.is_dir():
                target /= "index.html"
            assert target.is_file(), f"Broken link: {path} -> {href}"
            if link.fragment and target in pages:
                assert unquote(link.fragment) in pages[target].ids, (
                    f"Broken anchor: {path} -> {href}"
                )

    for feed in ["index.xml", "writing/index.xml", "posts/index.xml"]:
        channel = ET.parse(destination / feed).getroot().find("channel")
        assert channel is not None, feed
        for item in channel.findall("item"):
            assert "/writing/" in item.findtext("link"), feed
            assert item.findtext("pubDate"), feed
    print(
        f"Verified {total} rendered entries, legacy redirects, "
        f"internal links and RSS across {len(pages)} HTML pages."
    )


if __name__ == "__main__":
    destination = (
        Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "public"
    )
    verify(destination)
