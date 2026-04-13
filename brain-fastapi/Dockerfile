# Use official Python runtime
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# We don't copy the code here because we will use Volumes for hot-reloading in dev.
# We just need to install the dependencies.
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI runs on
EXPOSE 8000