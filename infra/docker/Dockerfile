# Backend Dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/app ${LAMBDA_TASK_ROOT}

# Set handler
CMD [ "main.handler" ]

