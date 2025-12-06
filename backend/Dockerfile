FROM public.ecr.aws/lambda/python:3.12

# Install PyTorch CPU-only first (smaller than full torch)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Note: Reference CSV will be loaded from S3 or bundled separately
# Vector index will be downloaded from S3 at runtime

# Pre-download the embedding model during build to speed up cold starts
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Vector index will be downloaded from S3 at runtime

# Set the CMD to your handler
CMD [ "src.handler.lambda_handler" ]
