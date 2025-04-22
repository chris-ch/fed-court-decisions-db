import json
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from pathlib import Path

# Paths to ONNX model and tokenizer (inside Lambda's /tmp or bundled directory)
MODEL_PATH = "/opt/model.onnx"  # Use /opt for Lambda layers
TOKENIZER_PATH = "/opt/tokenizer"

def lambda_handler(event, context):
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)

        # Load ONNX model
        session = ort.InferenceSession(MODEL_PATH)

        # Parse input sentences from event
        body = json.loads(event.get("body", "{}"))
        sentences = body.get("sentences", [])

        if not sentences:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No sentences provided"})
            }

        # Tokenize sentences
        inputs = tokenizer(sentences, return_tensors="np", padding=True, truncation=True)

        # Prepare ONNX inputs
        onnx_inputs = {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"]
        }

        # Run inference
        outputs = session.run(None, onnx_inputs)[0]

        # Convert embeddings to list for JSON serialization
        embeddings = outputs.tolist()

        return {
            "statusCode": 200,
            "body": json.dumps({"embeddings": embeddings}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"  # For CORS if needed
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
