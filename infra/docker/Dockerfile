# Backend Dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (will be overridden by volume mount for hot reload in dev)
COPY src/app ${LAMBDA_TASK_ROOT}

# Set handler
# Note: Lambda RIE reloads code on each request when using volume mounts
CMD [ "main.handler" ]

