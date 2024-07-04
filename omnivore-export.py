#!/usr/bin/python3.12

"""Export Links from Omnivore.

more info at https://github.com/Cito/omnivore-export
"""

import argparse
import sys
from datetime import date
from json import dump
from os import environ
from typing import Any

from gql import Client, gql
from gql.transport.httpx import HTTPXTransport

API_URL = "https://api-prod.omnivore.app/api/graphql"
API_KEY = "XXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

BACKUP_PATH = "omnivore_backup.json"
WITH_DATE = True

SEARCH = "in:all"
LIMIT = 100
TIMEOUT = 15
WITH_CONTENT = False

QUERY_EXPORT = """
query Export($search: String!,
             $limit: Int!, $after: String,
             $withContent: Boolean!) {
    search(query: $search,
           first: $limit, after: $after,
           includeContent: $withContent) {
        ... on SearchSuccess {
            edges {
                node {
                    title
                    slug
                    url
                    pageType
                    contentReader
                    createdAt
                    updatedAt
                    isArchived
                    readingProgressPercent
                    readingProgressTopPercent
                    readingProgressAnchorIndex
                    author
                    image
                    description
                    publishedAt
                    ownedByViewer
                    originalArticleUrl
                    uploadFileId
                    labels {
                        name
                    }
                    pageId
                    shortId
                    quote
                    annotation
                    state
                    siteName
                    subscription
                    readAt
                    savedAt
                    wordsCount
                    content
                    archivedAt
                }
                cursor
            }
        }
        ... on SearchError {
            errorCodes
        }
    }
}
"""


def get_all(
    url: str, key: str, search: str, with_content: bool
) -> list[dict[str, Any]]:
    print("Reading data...")

    headers = {"Authorization": key}
    transport = HTTPXTransport(url=url, headers=headers, timeout=TIMEOUT)
    client = Client(transport=transport)
    query = gql(QUERY_EXPORT)
    variables = {
        "search": search,
        "limit": LIMIT,
        "after": None,
        "withContent": with_content,
    }

    all_nodes: list[Any] = []
    while True:
        print(".", end="", flush=True)
        result = client.execute(query, variables)
        edges = result["search"]["edges"]
        if not edges:
            break
        variables["after"] = edges[-1]["cursor"]
        nodes = [edge["node"] for edge in edges]
        all_nodes += nodes
    print()
    return all_nodes


def save_backup(data: Any, path: str):
    print("Saving data...")

    with open(path, "w", encoding="utf-8") as backup:
        print(f"Dumping at {path}")
        dump(data, backup)


def main():
    parser = argparse.ArgumentParser(description="Export links from Omnivore API")
    parser.add_argument(
        "--url",
        default=environ.get("OMNIVORE_API_URL", API_URL),
        help="the Omnivore API URL",
    )
    parser.add_argument(
        "--key",
        default=environ.get("OMNIVORE_API_KEY", API_KEY),
        help="the Omnivore API Key",
    )
    parser.add_argument(
        "--search",
        default=environ.get("OMNIVORE_QUERY", SEARCH),
        help="the Omnivore search query",
    )
    with_content = environ.get("OMNIVORE_WITH_CONTENT", WITH_CONTENT)
    if isinstance(with_content, str):
        with_content = not with_content.lower() in ("", "0", "no", "false")
    parser.add_argument(
        "--with-content",
        action="store_true",
        default=with_content,
        help="include page content in the backup",
    )
    parser.add_argument(
        "--path",
        default=environ.get("OMNIVORE_BACKUP_PATH", BACKUP_PATH),
        help="the backup file path",
    )
    with_date = environ.get("OMNIVORE_WITH_DATE", WITH_DATE)
    if isinstance(with_date, str):
        with_date = not with_date.lower() in ("", "0", "no", "false")
    parser.add_argument(
        "--without-date",
        action="store_true",
        default=not with_date,
        help="do not add the current date to the backup path",
    )

    args = parser.parse_args()
    url = args.url
    key = args.key
    search = args.search
    with_content = args.with_content
    path = args.path
    with_date = not args.without_date

    if not key or "X" in key:
        print("Please specify your Omnivore API key.")
        sys.exit(1)

    nodes = get_all(url, key, search, with_content)
    print("Number of links:", len(nodes))
    if with_date:
        parts = list(path.partition("."))
        parts.insert(-2, "-" + date.today().isoformat())
        path = "".join(parts)
    save_backup(nodes, path)


if __name__ == "__main__":
    main()
