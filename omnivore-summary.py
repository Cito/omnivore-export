#!/usr/bin/python3.11

"""Export Links from Omnivore.

more info at https://github.com/Cito/omnivore-export
"""

from collections import Counter
from os import environ

from gql import gql, Client
from gql.transport.httpx import HTTPXTransport

api_url = "https://api-prod.omnivore.app/api/graphql"
api_key = "FFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"


add_date_to_path = True

query_all = """
{
    search(first: 9999, after: null, query: "in:all") {
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
            }
        }
        ... on SearchError {
            errorCodes
        }
    }
}

"""


def get_all(url, key):
    headers = dict(Authorization=key)
    transport = HTTPXTransport(url=url, headers=headers)
    client = Client(transport=transport)
    query = gql(query_all)
    result = client.execute(query)
    return result


def summarize(data):
    num_archived = num_inbox = 0
    page_type_counter = Counter()
    label_counter = Counter()
    for edge in data["search"]["edges"]:
        node = edge["node"]
        if node['isArchived']:
            num_archived += 1
        else:
            num_inbox += 1
        page_type = node["pageType"]
        if page_type:
            page_type_counter.update([page_type])
        labels = node["labels"]
        if labels:
            labels = [label["name"] for label in node["labels"]]
            label_counter.update(labels)

    print()
    print("* Inbox:", num_inbox)
    print("* Archive:", num_archived)
    print()
    print("* Page types:")
    for key, value in sorted(page_type_counter.items()):
        print(f"  - {key.capitalize()}: {value}")
    print()
    print("* Labels:")
    for key, value in sorted(label_counter.items()):
        print(f"  - {key}: {value}")
    print()


def main():
    url = environ.get('OMNIVORE_API_URL', api_url)
    key = environ.get('OMNIVORE_API_KEY', api_key)
    print("Reading data...")
    data = get_all(url, key)
    print("Summarizing...")
    summarize(data)


if __name__ == '__main__':
    main()
