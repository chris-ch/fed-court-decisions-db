import os
import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

# Environment variables
HOST = os.environ["AWS_OPENSEARCH_ENDPOINT"]
INDEX_NAME = os.environ["AWS_OPENSEARCH_INDEX_NAME"]
DDB_TABLE = os.environ.get("DDB_TABLE_NAME", "manual-fed-court-decisions")
TOP_K = int(os.getenv("TOP_MATCHES", "10"))

# AWS clients/resources
_session = boto3.Session()
awsauth = AWSV4SignerAuth(_session.get_credentials(), _session.region_name, service="aoss")

OPENSEARCH = OpenSearch(
    hosts=[{"host": HOST, "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    http_compress=True,
    timeout=30,
)

dynamodb = boto3.client('dynamodb')


def lambda_handler(event, _ctx):
    enriched_mappings = []

    for vec in event.get("embeddings", []):
        # 1. Query OpenSearch
        resp = OPENSEARCH.search(
            index=INDEX_NAME,
            body={"size": TOP_K,
                  "query": {"knn": {"embedding": {"vector": vec, "k": TOP_K}}}
            }
        )

        seen = set()
        docrefs = []
        for hit in resp["hits"]["hits"]:
            ref = hit["_source"]["doc_id"]
            if ref not in seen:
                seen.add(ref)
                docrefs.append(ref)

        # 2. Batch fetch metadata with escaped reserved keywords
        meta_map = {}
        if docrefs:
            keys = [{'docref': {'S': ref}} for ref in docrefs]
            response = dynamodb.batch_get_item(
                RequestItems={
                    DDB_TABLE: {
                        'Keys': keys,
                        'ProjectionExpression': 'docref, text_compressed, #u',
                        'ExpressionAttributeNames': {'#u': 'url'}
                    }
                }
            )
            items = response.get('Responses', {}).get(DDB_TABLE, [])
            meta_map = {
                item['docref']['S']: {
                    'text_compressed': item.get('text_compressed', {}).get('S'),
                    'url': item.get('url', {}).get('S')
                }
                for item in items
            }

        # 3. Enrich and assemble
        enriched = []
        for ref in docrefs:
            entry = {'docref': ref,
                     'text_compressed': None,
                     'url': None}
            if ref in meta_map:
                entry.update(meta_map[ref])
            enriched.append(entry)

        enriched_mappings.append(enriched)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"mappings": enriched_mappings})
    }
