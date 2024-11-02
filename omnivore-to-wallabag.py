#!/usr/bin/python3.12

"""Convert Omnivore export to Wallabag.

more info at https://github.com/Cito/omnivore-export
"""

import json
from pathlib import Path
from typing import Any

OMNIVORE_EXPORT_DIR = './export'
WALLABAG_IMPORT_FILE = 'wallabag.json'

BATCH_SIZE = 500


def get_json_file_number(json_file: Path) -> int:
    return int(json_file.stem.split('_', 2)[1])


def convert_tag(tag: str) -> str:
    return tag.lower()


def convert_data(data: dict[str, Any]) -> dict[str, Any]:
    slug = data['slug']
    data = {
        'title': data['title'],
        'url': data['url'],
        'tags': [convert_tag(label) for label in data['labels']],
        'is_archived': 1 if data['state'] == 'Archived' else 0,
        'is_starred': 0,
        'mimetype': 'text/html; charset=utf-8',
        'created_at': data['savedAt'],
        'updated_at': data['updatedAt'],
        'published_at': data['publishedAt'],
        'preview_picture': data['thumbnail']
    }
    if slug:
        content_file = Path(
            OMNIVORE_EXPORT_DIR).joinpath("content", slug + ".html")
        if content_file.exists():
            content = content_file.read_text(encoding='utf-8')
            data['content'] = content
    return data


def write_output(output: list[dict[str, Any]], suffix: str) -> None:
    import_file = WALLABAG_IMPORT_FILE
    if suffix:
        import_file = import_file.replace('.json', f'_{suffix}.json')
    print("Writing output to", import_file)
    with open(import_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=None)


def main():
    print("Reading input from", OMNIVORE_EXPORT_DIR)
    json_files = sorted(
        Path(OMNIVORE_EXPORT_DIR).glob('metadata_*_to_*.json'),
        key=get_json_file_number)
    if BATCH_SIZE:
        num_articles = int(
            str(json_files[-1]).split('_', 3)[3].split('.', 1)[0]) + 1
        num_parts = num_articles // BATCH_SIZE + 1
        num_digits = len(str(num_parts)) if num_parts > 1 else 0
    else:
        num_digits = 0
    num_batch = 1
    output: list[dict[str, Any]] = []
    for json_file in json_files:
        print("Converting", json_file)
        with open(json_file, encoding='utf-8') as f:
            articles = json.load(f)
            for article in articles:
                output.append(convert_data(article))
                if len(output) > BATCH_SIZE:
                    write_output(
                        output,
                        f"{num_batch:0{num_digits}}" if num_digits else '')
                    num_batch += 1
                    output.clear()
    if output:
        write_output(
            output,
            f"{num_batch:0{num_digits}}" if num_digits else '')
    print("Conversion finished.")


if __name__ == "__main__":
    main()
