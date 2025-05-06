import os
import json
import boto3
import base64

# Environment variables
DB_CLUSTER_ARN = os.environ["AURORA_CLUSTER_ARN"]
DB_SECRET_ARN = os.environ["AURORA_SECRET_ARN"]
DB_NAME = os.environ["AURORA_DB_NAME"]

DDB_TABLE = os.environ.get("DDB_TABLE_NAME", "manual-fed-court-decisions")
TOP_K = int(os.getenv("TOP_MATCHES", "10"))

# AWS clients
rds_data = boto3.client("rds-data")
dynamodb = boto3.client("dynamodb")


def query_top_k_embeddings(vector):
    # Convert Python list to PostgreSQL vector format
    pg_vector_str = "[" + ",".join(f"{x:.6f}" for x in vector) + "]"
    
    sql = f"""
        SELECT doc_id, chunk_id
        FROM embeddings
        ORDER BY embedding <-> '{pg_vector_str}'::vector
        LIMIT {TOP_K};
    """
    response = rds_data.execute_statement(
        secretArn=DB_SECRET_ARN,
        resourceArn=DB_CLUSTER_ARN,
        database=DB_NAME,
        sql=sql
    )

    results = []
    for row in response.get("records", []):
        doc_id = row[0]['stringValue']
        results.append(doc_id)
    return results


def lambda_handler(event, _ctx):
    enriched_mappings = []

    for vec in event.get("embeddings", []):
        docrefs = list(dict.fromkeys(query_top_k_embeddings(vec)))  # Deduplicate, preserve order

        # Fetch metadata from DynamoDB
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

        enriched = []
        for ref in docrefs:
            entry = {'docref': ref, 'text_compressed': None, 'url': None}
            if ref in meta_map:
                entry.update(meta_map[ref])
            enriched.append(entry)

        enriched_mappings.append(enriched)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"mappings": enriched_mappings})
    }
