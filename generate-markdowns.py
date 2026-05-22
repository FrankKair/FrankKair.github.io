import csv
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
import tomllib

from flags import FLAGS


def load_config(path='publications.toml'):
    with open(path, 'rb') as f:
        return tomllib.load(f)


def add_flag(value):
    parts = value.split(' / ')
    result = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Already has a flag emoji (regional indicator symbols)
        if any('\U0001F1E6' <= chr <= '\U0001F1FF' for chr in part):
            result.append(part)
        elif part in FLAGS:
            result.append()
        else:
            result.append(part)
    return ' / '.join(result)


def read_csv(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = [row for row in reader if row and row[0]]
    return headers, rows


def extract_year_from_date(value):
    """Extract year from dd/mm/yyyy format/"""
    parts = value.strip().split('/')
    if len(parts) == 3:
        return parts[2]
    return None


def compute_stats(headers, rows, stat_configs):
    """
    Compute stats based on declared config list.
    Supported formats:
    - country     -> count occurrences in the country column (split on '/')
    - decade:year -> bucket 'year' column values into decades
    """
    output_lines = []
    total = len(rows)
    output_lines.append('\n## Stats\n')
    output_lines.append(f"Total: {total}")

    for stat in stat_configs:
        if ':' in stat:
            stat_type, column_name = stat.split(':', 1)
        else:
            stat_type = stat
            column_name = stat

        if column_name not in headers:
            continue

        col_idx = headers.index(column_name)
        counter = Counter()

        if stat_type == 'country':
            for row in rows:
                values = row[col_idx].split(' / ')
                for v in values:
                    if v.strip():
                        counter[v.strip()] += 1
            label = 'Country'
        elif stat_type == 'decade':
            for row in rows:
                try:
                    year = int(row[col_idx])
                    decade = f"{year // 10 * 10}s"
                    counter[decade] += 1
                except (ValueError, IndexError):
                    pass
            label = 'Decade'
        else:
            continue

        sorted_items = counter.most_common()
        output_lines.append(f"\n| {label} | Count |")
        output_lines.append('|---------|-------|')
        for key, count in sorted_items:
            output_lines.append(f"| {key} | {count} |")

    return '\n'.join(output_lines) + '\n'


def build_table_header(headers):
    top = ''
    sep = ''
    for h in headers:
        top += f"| {h} "
        sep += '| --- '
    top += '|'
    sep += '|'
    return top, sep


def build_row(row):
    line = ''
    for content in row:
        line += f"| {content} "
    line += '|'
    return line


def generate_post(pub):
    csv_file = pub['csv']
    title = pub.get('title', Path(csv_file).stem)
    group_by = pub.get('group_by')
    stats_configs = pub.get('stats', [])
    published = pub.get('published', True)

    if not published:
        return

    if not Path(csv_file).exists():
        print(f"  Skipping {csv_file} (file not found)")

    headers, rows = read_csv(csv_file)
    output_path = Path('content/posts') / f"{title}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    country_cols = []
    for stat in stats_configs:
        col_name = stat.split(':', 1)[-1] if ':' in stat else stat
        stat_type = stat.split(':', 1)[0] if ':' in stat else stat
        if stat_type == 'country' and col_name in headers:
            country_cols.append(headers.index(col_name))

    for row in rows:
        for col_idx in country_cols:
            if col_idx < len(row) and row[col_idx]:
                row[col_idx] = add_flag(row[col_idx])

    lines = []

    # Hugo front matter
    lines.append('+++')
    lines.append(f"title = '{title}'")
    date = datetime.now() - timedelta(hours=1)
    lines.append(f"date = {date.isoformat(timespec='seconds')}Z")
    lines.append('+++\n')

    # Table data
    top_header, sep = build_table_header(headers)

    if group_by and group_by in headers:
        col_idx = headers.index(group_by)
        seen_years = set()
        for row in rows:
            date_val = row[col_idx] if col_idx < len(row) else ''
            year = extract_year_from_date(date_val)
            if year and year not in seen_years:
                seen_years.add(year)
                lines.append(f"\n## {year}\n")
                lines.append(top_header)
                lines.append(sep)
            lines.append(build_row(row))
    else:
        lines.append(top_header)
        lines.append(sep)
        for row in rows:
            lines.append(build_row(row))

    if stats_configs:
        lines.append(compute_stats(headers, rows, stats_configs))

    output_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"  {output_path}")


def main():
    publications = load_config().get('publication', [])
    print(f"Generating {len(publications)} publications:")
    for p in publications:
        generate_post(p)
    print('✅ Done!')


if __name__ == '__main__':
    main()
