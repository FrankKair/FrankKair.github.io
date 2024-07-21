from dataclasses import dataclass
from collections import Counter
from datetime import datetime, timedelta
import csv
from abc import ABC, abstractmethod


class Stats(ABC):
    @abstractmethod
    def write(self, input_csv_file, output):
        raise NotImplementedError('Missing write Stats method')


class CountryStats(Stats):
    def __init__(self):
        self.count = 0
        self.countries = Counter()

    def write(self, input_csv_file, output):
        with open(input_csv_file, 'r', encoding='utf-8') as csvfile:
            parsed = csv.reader(csvfile)
            country_column = None
            for count, row in enumerate(parsed):
                # Find 'country' header index
                if count == 0:
                    for index, header in enumerate(row):
                        if header == 'country':
                            country_column = index
                            break
                    continue
                if not country_column:
                    return

                # Count occurrences
                if row[0]:
                    self.count += 1
                    countries = row[country_column].split(' / ')
                    for c in countries:
                        self.countries[c] += 1

        with open(output, 'a') as out:
            out.write('\n## Stats\n\n')
            out.write(f"Total: {self.count}\n")

            sorted_items = self.countries.most_common()
            out.write('\n| Country | Count |\n')
            out.write('|---------|-------|\n')

            for key, count in sorted_items:
                out.write(f"| {str(key)} | {str(count)} |\n")


class MusicStats(Stats):
    @dataclass(frozen=True)
    class Album:
        artist: str
        album: str
        year: int
        country: str
        review: str

    def __init__(self):
        self.data = []
        self.count = 0
        self.countries = Counter()
        self.decades = Counter()

    def add(self, album):
        self.data.append(album)
        self.count += 1
        self.countries[album.country] += 1
        decade = str(album.year // 10 * 10) + 's'
        self.decades[decade] += 1

    def parse_csv(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            parsed = csv.reader(csvfile)
            for count, r in enumerate(parsed):
                if count != 0 and r[0] != '':
                    album = self.Album(r[0], r[1], int(r[2]), r[3], r[4])
                    self.add(album)

    def write(self, input_csv_file, output):
        self.parse_csv(input_csv_file)
        with open(output, 'a') as out:
            out.write('\n## Stats\n\n')
            out.write(f"Total: {self.count}\n")

            sorted_items = self.countries.most_common()
            out.write('\n| Country | Count |\n')
            out.write('|---------|-------|\n')

            for key, count in sorted_items:
                out.write(f"| {str(key)} | {str(count)} |\n")

            sorted_items = self.decades.most_common()
            out.write('\n| Decade | Count |\n')
            out.write('|--------|-------|\n')
            for key, count in sorted_items:
                out.write(f"| {str(key)} | {str(count)} |\n")


class CsvToMarkdownPost:
    def __init__(self, input_file, stats=None, by_year=False):
        output_file = input_file.split('.')[0]
        self.input_file = input_file
        self.output = f"content/posts/{output_file}.md"
        self.title = output_file
        self.headers = []
        self.rows = []
        self.stats = stats
        self.by_year = by_year
        self.write()

    def write(self):
        self.write_headers()
        self.write_data()
        if self.stats:
            self.stats.write(self.input_file, self.output)

    def write_headers(self):
        with open(self.output, 'w') as out:
            out.write('+++\n')
            out.write(f"title = '{self.title}'\n")
            date = datetime.now() - timedelta(hours=1)
            formatted = date.isoformat(timespec='seconds') + 'Z'
            out.write(f"date = {formatted}\n")
            out.write('+++\n\n')

    def write_data(self):
        def year(date):
            return date.split('/')[-1]

        with open(self.input_file, 'r', encoding='utf-8') as csvfile:
            parsed = csv.reader(csvfile)
            for count, row in enumerate(parsed):
                if count == 0:
                    self.headers = row
                else:
                    self.rows.append(row)

        top_header = ''
        next_line = ''
        for header in self.headers:
            top_header += f"| {header} "
            next_line += '| --- '
        top_header += '|'
        next_line += '|'

        years = set()
        with open(self.output, 'a') as out:
            for count, row in enumerate(self.rows):
                if self.by_year:
                    curr_year = year(row[-1])
                    if curr_year not in years:
                        years.add(curr_year)
                        out.write(f"\n## {curr_year}\n\n")
                        out.write(f"{top_header}\n")
                        out.write(f"{next_line}\n")
                elif count == 0:
                    out.write(f"{top_header}\n")
                    out.write(f"{next_line}\n")

                line = ''
                for content in row:
                    line += f"| {content} "
                line += '|\n'
                out.write(line)


if __name__ == '__main__':
    CsvToMarkdownPost(
        'Travelling.csv',
        stats=CountryStats()
    )

    CsvToMarkdownPost(
        'Books.csv',
        stats=CountryStats(),
        by_year=True
    )

    CsvToMarkdownPost(
        'Music.csv',
        stats=MusicStats(),
        by_year=True
    )
