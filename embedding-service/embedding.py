import json
import onnxruntime as ort
from transformers import AutoTokenizer
import os

# Paths to ONNX model and tokenizer
MODEL_PATH = "/opt/model.onnx"
TOKENIZER_PATH = "/opt/tokenizer"

# Load tokenizer from local directory
tokenizer = AutoTokenizer.from_pretrained(
    TOKENIZER_PATH,
    local_files_only=True  # Force local files only
)

session = ort.InferenceSession(MODEL_PATH)


def lambda_handler(event, context):
    try:
        # Verify tokenizer directory exists
        if not os.path.isdir(TOKENIZER_PATH):
            raise FileNotFoundError(f"Tokenizer directory not found: {TOKENIZER_PATH}")

        # Load ONNX model
        if not os.path.isfile(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

        # Parse input sentences from event
        body = json.loads(event.get("body", "{}"))
        sentences = body.get("sentences", [])

        if not sentences:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No sentences provided"}),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
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
                "Access-Control-Allow-Origin": "*"
            }
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Content-Type": "application/json"
            }
        }