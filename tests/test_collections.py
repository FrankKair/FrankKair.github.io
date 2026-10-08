"""Data preservation checks, using only Python's standard library."""

import csv
import importlib.util
import re
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location(
    "generator", ROOT / "scripts/generate-markdowns.py"
)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "csv", self.root / "csv")
        shutil.copy(ROOT / "publications.toml", self.root)

    def snapshot(self):
        return {
            str(p.relative_to(self.root)): p.read_bytes()
            for p in self.root.rglob("*")
            if p.is_file()
        }

    def test_every_csv_field_and_entry_is_preserved(self):
        publications = generator.load_config(
            self.root / "publications.toml"
        )["publication"]
        self.assertEqual(
            {p["csv"] for p in publications},
            {
                str(p.relative_to(self.root))
                for p in (self.root / "csv").glob("*.csv")
            },
        )
        for publication in publications:
            with self.subTest(collection=publication["slug"]):
                with (self.root / publication["csv"]).open(
                    newline="", encoding="utf-8"
                ) as source:
                    headers, *rows = csv.reader(source)
                data = generator.build_collection(publication, self.root)
                self.assertEqual(data["headers"], headers)
                self.assertEqual(data["count"], len(rows))
                self.assertEqual(len(data["rows"]), len(rows))
                for original, actual in zip(rows, data["rows"]):
                    for column, old, new in zip(headers, original, actual):
                        if column == "country":
                            # Only flags and whitespace may change.
                            def names(value):
                                return [
                                    re.sub("[🇦-🇿]", "", part).strip()
                                    for part in value.split("/")
                                    if part.strip()
                                ]
                            self.assertEqual(names(new), names(old))
                        else:
                            self.assertEqual(new, old)
                grouped = [
                    tuple(row)
                    for group in data["groups"]
                    for row in group["rows"]
                ]
                self.assertEqual(
                    Counter(grouped), Counter(map(tuple, data["rows"]))
                )

    def test_generation_preserves_sources_and_articles_and_is_repeatable(self):
        writing = self.root / "content/writing/notes.md"
        writing.parent.mkdir(parents=True)
        writing.write_text(
            '+++\ntitle = "My article"\n+++\nHandwritten text.\n'
        )
        before = self.snapshot()
        generator.generate(self.root)
        first = self.snapshot()
        for path, contents in before.items():
            self.assertEqual(first[path], contents, path)
        mtimes = {
            p: p.stat().st_mtime_ns
            for p in self.root.rglob("*")
            if p.is_file()
        }
        generator.generate(self.root)
        self.assertEqual(first, self.snapshot())
        self.assertEqual(mtimes, {p: p.stat().st_mtime_ns for p in mtimes})

    def test_authored_collection_page_is_not_overwritten(self):
        page = self.root / "content/collections/books.md"
        page.parent.mkdir(parents=True)
        page.write_text("My handwritten book notes")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            generator.generate(self.root)
        self.assertEqual(before, self.snapshot())

    def test_malformed_csv_fails_before_writing_any_output(self):
        with (self.root / "csv/recs-music.csv").open("a") as target:
            target.write("\nToo,many,fields,in,this,record\n")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "expected 5 fields"):
            generator.generate(self.root)
        self.assertEqual(before, self.snapshot())

    def test_partial_dates_and_undated_entries_stay_in_the_log(self):
        path = self.root / "csv/dates.csv"
        path.write_text(
            "title,date\nOlder,2019\nPartial,-/07/2022\nUnknown,\n"
            "Earlier,01/01/2022\n",
            encoding="utf-8",
        )
        data = generator.build_collection(
            {"csv": "csv/dates.csv", "group_by": "date"}, self.root
        )
        self.assertEqual(
            [g["label"] for g in data["groups"]],
            ["2022", "2019", "Undated"],
        )
        self.assertEqual(
            [r[0] for r in data["groups"][0]["rows"]], ["Partial", "Earlier"]
        )
        self.assertEqual(sum(len(g["rows"]) for g in data["groups"]), 4)

    def test_flags_and_statistics(self):
        self.assertEqual(
            generator.add_flags("United Kingdom / 🇫🇷 France / Rome"),
            "🇬🇧 United Kingdom / 🇫🇷 France / Rome",
        )
        self.assertEqual(
            generator.add_flags("UK / USA / Türkiye / Hong Kong"),
            "🇬🇧 UK / 🇺🇸 USA / 🇹🇷 Türkiye / 🇭🇰 Hong Kong",
        )
        self.assertEqual(
            generator.add_flags("Ancient Greece / Rome"),
            "Ancient Greece / Rome",
        )
        self.assertEqual(
            generator.add_flags(" Canada/USA "), "🇨🇦 Canada / 🇺🇸 USA"
        )
        flags = generator.add_flags("UK / USA / Türkiye / Hong Kong")
        self.assertEqual(generator.add_flags(flags), flags)
        rows = [
            ["🇬🇧 UK / 🇫🇷 France", "1999"],
            ["🇬🇧 UK", "2001"],
            ["Rome", "8th century BC"],
        ]
        stats = generator.compute_stats(
            ["country", "year"], rows, ["country", "decade:year"]
        )
        self.assertEqual(
            dict(stats[0]["items"]), {"🇬🇧 UK": 2, "🇫🇷 France": 1, "Rome": 1}
        )
        self.assertEqual(dict(stats[1]["items"]), {"1990s": 1, "2000s": 1})

    def test_source_csvs_have_no_embedded_flags(self):
        for path in (self.root / "csv").glob("*.csv"):
            with self.subTest(csv=path.name):
                self.assertNotRegex(path.read_text(encoding="utf-8"), "[🇦-🇿]")

    def test_unpublishing_removes_only_generated_pages(self):
        generator.generate(self.root)
        authored = self.root / "content/collections/_index.md"
        authored.write_text("Collection introduction")
        config = self.root / "publications.toml"
        config.write_text(
            config.read_text().replace(
                'slug = "books"', 'slug = "books"\npublished = false'
            )
        )
        generator.generate(self.root)
        self.assertFalse((self.root / "content/collections/books.md").exists())
        self.assertFalse((self.root / "data/collections/books.json").exists())
        self.assertEqual(authored.read_text(), "Collection introduction")


if __name__ == "__main__":
    unittest.main()
