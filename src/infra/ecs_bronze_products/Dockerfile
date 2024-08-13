# Base image
FROM python:3.12-slim-bookworm

# Install awsdk pandas
RUN pip3 install awswrangler pandas

# Copy your .py file
COPY src/etl/ /app/etl/
COPY src/infra/ecs_bronze_products/main.py /app

# Set the working directory
WORKDIR /app

# Run the script
CMD ["python", "main.py"]
