import os, boto3, json
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

HOST        = os.environ["AWS_OPENSEARCH_ENDPOINT"]
INDEX_NAME  = os.environ["AWS_OPENSEARCH_INDEX_NAME"]
TOP_K       = int(os.getenv("TOP_MATCHES", "10"))

# 👉 Region comes from the current execution context
_session   = boto3.Session()                 # no args → picks up AWS_REGION
awsauth    = AWSV4SignerAuth(_session.get_credentials(),
                             _session.region_name,
                             service="aoss")

OPENSEARCH = OpenSearch(
    hosts=[{"host": HOST, "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    http_compress=True,
    timeout=30,
)

def lambda_handler(event, _ctx):
    mappings = []
    for vec in event.get("embeddings", []):
        resp = OPENSEARCH.search(
            index=INDEX_NAME,
            body={
                "size": TOP_K,
                "query": {"knn": {"embedding": {"vector": vec, "k": TOP_K}}}
            }
        )
        ids, seen = [], set()
        for hit in resp["hits"]["hits"]:          # already score-sorted
            doc_id = hit["_source"]["doc_id"]
            if doc_id not in seen:
                seen.add(doc_id)
                ids.append(doc_id)
        mappings.append(ids)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"mappings": mappings})
    }
