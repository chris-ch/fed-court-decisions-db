FROM public.ecr.aws/lambda/python:3.13

# Install dependencies
RUN pip install --no-cache-dir --root-user-action=ignore \
    onnxruntime transformers numpy

# Copy Lambda function code
COPY embedding.py ${LAMBDA_TASK_ROOT}

# Copy model and tokenizer
COPY onnx_model/model.onnx /opt/model.onnx
COPY onnx_model/tokenizer.json /opt/tokenizer/
COPY onnx_model/tokenizer_config.json /opt/tokenizer/
COPY onnx_model/special_tokens_map.json /opt/tokenizer/
COPY onnx_model/vocab.txt /opt/tokenizer/

# Set the CMD to the Lambda handler
CMD ["embedding.lambda_handler"]
