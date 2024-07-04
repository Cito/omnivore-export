#!/usr/bin/python3.12

"""Export Links from Omnivore.

more info at https://github.com/Cito/omnivore-export
"""

from datetime import date
from json import dump
from os import environ
from typing import Any

from gql import Client, gql
from gql.transport.httpx import HTTPXTransport

API_URL = "https://api-prod.omnivore.app/api/graphql"
API_KEY = "FFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"

BACKUP_PATH = "omnivore_backup.json"

SEARCH = "in:all"
LIMIT = 100
TIMEOUT = 15
WITH_CONTENT = False

ADD_DATE_TO_PATH = True

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
    url = environ.get("OMNIVORE_API_URL", API_URL)
    key = environ.get("OMNIVORE_API_KEY", API_KEY)
    search = environ.get("OMNIVORE_QUERY", SEARCH)
    with_content = bool(environ.get("OMNIVORE_WITH_CONTENT", WITH_CONTENT))
    nodes = get_all(url, key, search, with_content)
    print("Number of links:", len(nodes))
    path = environ.get("OMNIVORE_BACKUP_PATH", BACKUP_PATH)
    if ADD_DATE_TO_PATH:
        parts = list(path.partition("."))
        parts.insert(-2, "-" + date.today().isoformat())
        path = "".join(parts)
    save_backup(nodes, path)


if __name__ == "__main__":
    main()
