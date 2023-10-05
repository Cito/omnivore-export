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
limit = 9999
with_content = False

add_date_to_path = True

query_all = """
query Export($search: String!,
             $limit: Int!,
             $withContent: Boolean!) {
    search(query: $search, 
           first: $limit,
           after: null,
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
            }
        }
        ... on SearchError {
            errorCodes
        }
    }
}
"""


def get_all(url, key):
    headers = {'Authorization': key}
    transport = HTTPXTransport(url=url, headers=headers)
    client = Client(transport=transport)
    query = gql(query_all)
    variables = {'search': search, 'limit': limit, 'withContent': with_content}
    return client.execute(query, variables)


def save_backup(data, path):
    with open(path, 'w', encoding='utf-8') as backup:
        dump(data, backup)


def main():
    url = environ.get('OMNIVORE_API_URL', api_url)
    key = environ.get('OMNIVORE_API_KEY', api_key)
    data = get_all(url, key)
    print("Number of links:", len(data["search"]["edges"]))
    path = environ.get('OMNIVORE_BACKUP_PATH', backup_path)
    if add_date_to_path:
        parts = list(path.partition('.'))
        parts.insert(-2, "-" + date.today().isoformat())
        path = ''.join(parts)
    save_backup(data, path)


if __name__ == '__main__':
    main()
