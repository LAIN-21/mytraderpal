# Backend Dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Install HTTP proxy dependencies
RUN pip install --no-cache-dir requests

# Copy HTTP proxy (converts HTTP requests to Lambda invoke format)
# Build context is root, so paths are relative to root
COPY infra/docker/lambda-proxy.py /usr/local/bin/lambda-proxy.py
RUN chmod +x /usr/local/bin/lambda-proxy.py

# Copy startup script
COPY infra/docker/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

# Copy application code (will be overridden by volume mount for hot reload in dev)
# Copy to /var/task/app to match import structure (from app.api.router)
COPY src/app ${LAMBDA_TASK_ROOT}/app

# Override entrypoint to run our startup script directly
# The Lambda base image's entrypoint expects handler as arg, but we handle that in start.sh
ENTRYPOINT []
CMD ["/usr/local/bin/start.sh"]

