#!/usr/bin/python3.11

"""Summarize Links from Omnivore.

more info at https://github.com/Cito/omnivore-export
"""

from collections import Counter
from os import environ

from gql import Client, gql
from gql.transport.httpx import HTTPXTransport

api_url = "https://api-prod.omnivore.app/api/graphql"
api_key = "FFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"

search = "in:all"
limit = 100
timeout = 15

add_date_to_path = True

query_summarize = """
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


def get_all(url, key):
    print("Reading data...")

    headers = {'Authorization': key}
    transport = HTTPXTransport(url=url, headers=headers, timeout=timeout)
    client = Client(transport=transport)
    query = gql(query_summarize)
    variables = {'search': 'in:all', 'limit': limit, 'after': None}
    all_nodes = []

    while True:
        print(".", end="", flush=True)
        result = client.execute(query, variables)
        edges = result['search']['edges']
        if not edges:
            break
        variables['after'] = edges[-1]['cursor']
        nodes = [edge['node'] for edge in edges]
        all_nodes += nodes
    print()

    return all_nodes


def show_table(data, width=80):
    max_key_len = max(len(key) for key in data)
    max_val_len = max(len(str(val)) for val in data.values())
    cols = width // (max_key_len + max_val_len + 5)
    row = []
    for key, val in sorted(data.items()):
        row.append(f"{key:<{max_key_len}}: {val:>{max_val_len}}")
        if len(row) >= cols:
            print(' | '.join(row))
            row = []
    if row:
        print(' | '.join(row))


def summarize(nodes):
    print("Summarizing...")

    num_archived = num_inbox = 0
    page_type_counter = Counter()
    label_counter = Counter()
    for node in nodes:
        if node['isArchived']:
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
    url = environ.get('OMNIVORE_API_URL', api_url)
    key = environ.get('OMNIVORE_API_KEY', api_key)

    nodes = get_all(url, key)
    summarize(nodes)


if __name__ == '__main__':
    main()
