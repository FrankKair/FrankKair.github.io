from dataclasses import dataclass
from collections import Counter
from datetime import datetime, timedelta
import csv


@dataclass(frozen=True)
class Album:
    artist: str
    album: str
    year: int
    country: str
    review: str

    def review_year(self):
        return self.review.split('/')[-1]


class Stats:
    def __init__(self, filepath):
        self.data = []
        self.count = 0
        self.countries = Counter()
        self.decades = Counter()
        self.parse_csv(filepath)

    def add(self, album):
        self.data.append(album)
        self.count += 1
        self.countries[album.country] += 1
        decade = str(album.year // 10 * 10) + 's'
        self.decades[decade] += 1

    def parse_csv(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            parsed = csv.reader(csvfile)
            for count, row in enumerate(parsed):
                if count != 0 and row[0] != '':
                    self.add(
                        Album(
                            row[0],
                            row[1],
                            int(row[2]),
                            row[3],
                            row[4],
                        )
                    )


class PostConverter:
    def __init__(self, stats, output):
        self.stats = stats
        self.output = output

    def write_to_markdown(self):
        self.write_headers()
        self.write_albums_data()
        self.write_albums_stats()

    def write_headers(self):
        with open(self.output, 'w') as out:
            out.write('+++\n')
            out.write("title = 'Music Review'\n")
            date = datetime.now() - timedelta(hours=1)
            formatted = date.isoformat(timespec='seconds') + 'Z'
            out.write(f"date = {formatted}\n")
            out.write('+++\n')

    def write_albums_data(self):
        years = set()
        header = '| Artist | Album | Year | Country | Review |\n'
        next_line = '| ------ | ----- | ---- | ------- | ------ |\n'
        with open(self.output, 'a') as out:
            for a in self.stats.data:
                if a.review_year() not in years:
                    years.add(a.review_year())
                    out.write(f"\n## {a.review_year()}\n\n")
                    out.write(header)
                    out.write(next_line)
                line = ''
                line += f"| {a.artist} "
                line += f"| {a.album} "
                line += f"| {a.year} "
                line += f"| {a.country} "
                line += f"| {a.review} |\n"
                out.write(line)

    def write_albums_stats(self):
        with open(self.output, 'a') as out:
            out.write('\n## Stats\n\n')
            out.write(f"Total: {self.stats.count}\n")

            sorted_items = self.stats.countries.most_common()
            out.write('\n| Country | Count |\n')
            out.write('|---------|-------|\n')

            for key, count in sorted_items:
                out.write(f"| {str(key)} | {str(count)} |\n")

            sorted_items = self.stats.decades.most_common()
            out.write('\n| Decade | Count |\n')
            out.write('|--------|-------|\n')
            for key, count in sorted_items:
                out.write(f"| {str(key)} | {str(count)} |\n")


if __name__ == '__main__':
    stats = Stats('music-review-data.csv')
    PostConverter(stats, 'content/posts/music-review.md').write_to_markdown()
