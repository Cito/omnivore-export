#!/usr/bin/python3.12

"""Summarize Links from Omnivore.

more info at https://github.com/Cito/omnivore-export
"""

import argparse
import sys
from collections import Counter
from os import environ
from typing import Any

from gql import Client, gql
from gql.transport.httpx import HTTPXTransport

API_URL = "https://api-prod.omnivore.app/api/graphql"
API_KEY = "XXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

SEARCH = "in:all"
LIMIT = 100
TIMEOUT = 15

ADD_DATE_TO_PATH = True

QUERY_SUMMARIZE = """
query Summarize($search: String!,
                $limit: Int!, $after: String) {
    search(query: $search,
           first: $limit, after: $after,
           includeContent: false) {
        ... on SearchSuccess {
            edges {
                node {
                    pageType
                    contentReader
                    createdAt
                    isArchived
                    readingProgressPercent
                    readingProgressTopPercent
                    readingProgressAnchorIndex
                    labels {
                        name
                    }
                    state
                    readAt
                    savedAt
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


def get_all(url: str, key: str, search: str) -> list[dict[str, Any]]:
    print("Reading data...")

    headers = {"Authorization": key}
    transport = HTTPXTransport(url=url, headers=headers, timeout=TIMEOUT)
    client = Client(transport=transport)
    query = gql(QUERY_SUMMARIZE)
    variables = {"search": search, "limit": TIMEOUT, "after": None}

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


def show_table(data: dict[str, Any], width: int = 80) -> None:
    max_key_len = max(len(key) for key in data)
    max_val_len = max(len(str(val)) for val in data.values())
    cols = width // (max_key_len + max_val_len + 5)

    row: list[str] = []
    for key, val in sorted(data.items()):
        row.append(f"{key:<{max_key_len}}: {val:>{max_val_len}}")
        if len(row) >= cols:
            print(" | ".join(row))
            row = []
    if row:
        print(" | ".join(row))


def summarize(nodes: list[dict[str, Any]]) -> None:
    print("Summarizing...")

    num_archived = num_inbox = 0
    page_type_counter = Counter[str]()
    label_counter = Counter[str]()
    for node in nodes:
        if node["isArchived"]:
            num_archived += 1
        else:
            num_inbox += 1
        page_type = node["pageType"]
        if page_type:
            page_type_counter.update([page_type.capitalize()])
        labels = node["labels"]
        if labels:
            labels = [label["name"] for label in node["labels"]]
            label_counter.update(labels)

    print()
    print("* Inbox:", num_inbox)
    print("* Archive:", num_archived)
    print()
    print("* Page types:")
    show_table(page_type_counter)
    print()
    print("* Labels:")
    show_table(label_counter)
    print()


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

    args = parser.parse_args()

    url = args.url
    key = args.key
    search = args.search

    if not key or "X" in key:
        print("Please specify your Omnivore API key.")
        sys.exit(1)

    nodes = get_all(url, key, search)
    summarize(nodes)


if __name__ == "__main__":
    main()
