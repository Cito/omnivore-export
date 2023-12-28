#!/usr/bin/python3.11

"""Export Links from Omnivore.

more info at https://github.com/Cito/omnivore-export
"""

from datetime import date
from json import dump
from os import environ

from gql import gql, Client
from gql.transport.httpx import HTTPXTransport

api_url = "https://api-prod.omnivore.app/api/graphql"
api_key = "FFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"

backup_path = "omnivore_backup.json"

search = "in:all"
limit = 100
timeout = 15
with_content = False

add_date_to_path = True

query_export = """
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


def get_all(url, key):
    print("Reading data...")
    headers = {'Authorization': key}
    transport = HTTPXTransport(url=url, headers=headers, timeout=timeout)
    client = Client(transport=transport)
    query = gql(query_export)
    variables = {'search': search, 'limit': limit, 'after': None,
                 'withContent': with_content}
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


def save_backup(data, path):
    print("Saving data...")
    with open(path, 'w', encoding='utf-8') as backup:
        dump(data, backup)


def main():
    url = environ.get('OMNIVORE_API_URL', api_url)
    key = environ.get('OMNIVORE_API_KEY', api_key)
    nodes = get_all(url, key)
    print("Number of links:", len(nodes))
    path = environ.get('OMNIVORE_BACKUP_PATH', backup_path)
    if add_date_to_path:
        parts = list(path.partition('.'))
        parts.insert(-2, "-" + date.today().isoformat())
        path = ''.join(parts)
    save_backup(nodes, path)


if __name__ == '__main__':
    main()
