FROM public.ecr.aws/lambda/python:3.12

# Set HuggingFace cache directory within the Lambda task root (persists in container)
ENV HF_HOME=${LAMBDA_TASK_ROOT}/models
ENV TRANSFORMERS_CACHE=${LAMBDA_TASK_ROOT}/models
ENV SENTENCE_TRANSFORMERS_HOME=${LAMBDA_TASK_ROOT}/models

# Install PyTorch CPU-only first (much smaller than full torch)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
COPY requirements-semantic.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements.txt -r requirements-semantic.txt

# Pre-download the embedding model during build (uses HF_HOME set above)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy function code and fix permissions
COPY src/ ${LAMBDA_TASK_ROOT}/src/
RUN chmod -R 755 ${LAMBDA_TASK_ROOT}/src/

# Vector index and CSV will be downloaded from S3 at runtime

# Set the CMD to your handler
CMD [ "src.handler.lambda_handler" ]
