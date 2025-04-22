cp -R data/onnx_model embedding-service/.

# Build the Docker image
docker build -t sentence-embedding-lambda embedding-service

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create an ECR repository (if not already created)
aws ecr create-repository --repository-name sentence-embedding-lambda --region $AWS_REGION

# Log in to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag the Docker image
docker tag sentence-embedding-lambda:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/sentence-embedding-lambda:latest

# Push the Docker image to ECR
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/sentence-embedding-lambda:latest
