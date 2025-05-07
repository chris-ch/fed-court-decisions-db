import base64
import json
import zlib
import boto3
import openai
import os

lambda_client = boto3.client('lambda')
oai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def decompress_text(text_compressed: str) -> str:
    try:
        compressed_bytes = base64.b64decode(text_compressed)
        return zlib.decompress(compressed_bytes).decode("utf-8")
    except Exception as e:
        print(f"Decompression error: {e}")
        return "[Erreur de décompression]"

def lambda_handler(event, context):
    print(f"Received event: {event}")

    # Parse the body of the request (string -> dict)
    try:
        body = json.loads(event.get("body", "{}"))
        sentences = body.get("sentences", [])
    except json.JSONDecodeError as e:
        print(f"Error decoding body: {e}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }

    if not sentences:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No sentences provided"})
        }

    # 1. Call manual-compute-embeddings Lambda
    response1 = lambda_client.invoke(
        FunctionName='manual-compute-embeddings',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            "body": json.dumps({"sentences": sentences}),
            "headers": {"Content-Type": "application/json"},
            "httpMethod": "POST"
        })
    )
    body1 = json.loads(response1['Payload'].read())
    embeddings = json.loads(body1.get("body", "{}")).get("embeddings", [])

    print(f"Embeddings response: {embeddings}")

    # 2. Call manual-index-search Lambda
    response2 = lambda_client.invoke(
        FunctionName='manual-index-search',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            "embeddings": embeddings
        })
    )
    body2 = json.loads(response2['Payload'].read())

    mappings_list = json.loads(body2.get("body", "{}")).get("mappings", [])

    print(f"Embeddings and mappings: {list(zip(sentences, mappings_list))}")


    # Step 3: Generate legal analysis using OpenAI
    analyses = []
    for sentence, relevant_docs in zip(sentences, mappings_list):
        cleaned_docs = []
        for doc in relevant_docs:
            cleaned_docs.append({
                "docref": doc["docref"],
                "url": doc.get("url"),
                "text": decompress_text(doc["text_compressed"])
            })

        context = "\n\n".join(
            [f"Décision {doc['docref']}:\n{doc['text']}" for doc in cleaned_docs]
        )

        question = f"Fournis un avis juridique en te fondant sur les documents joints concernant le cas suivant : {sentence}"

        try:
            response = oai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a legal assistant who answers based only on provided documents."},
                    {"role": "user", "content": f"{context}\n\nQuestion: {question}"}
                ],
                temperature=0
            )

            analysis_text = response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}")
            analysis_text = "Erreur lors de l'appel à OpenAI."

        analyses.append({
            "input_sentence": sentence,
            "documents": cleaned_docs,
            "analysis": analysis_text
        })

    return {
        "statusCode": 200,
        "body": json.dumps({"analyses": analyses})
    }
