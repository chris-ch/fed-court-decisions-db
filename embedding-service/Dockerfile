FROM public.ecr.aws/lambda/python:3.13

# Install dependencies
RUN pip install onnxruntime transformers numpy

# Copy Lambda function code
COPY embedding.py ${LAMBDA_TASK_ROOT}

# Copy model and tokenizer
COPY onnx_model/model.onnx ${LAMBDA_TASK_ROOT}/model.onnx
COPY onnx_model/tokenizer.json ${LAMBDA_TASK_ROOT}/tokenizer/
COPY onnx_model/tokenizer_config.json ${LAMBDA_TASK_ROOT}/tokenizer/
COPY onnx_model/special_tokens_map.json ${LAMBDA_TASK_ROOT}/tokenizer/
COPY onnx_model/vocab.txt ${LAMBDA_TASK_ROOT}/tokenizer/

# Set the CMD to the Lambda handler
CMD ["embedding.lambda_handler"]
