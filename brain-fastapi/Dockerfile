FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies and upgrade pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# This line ensures the 'uvicorn' command is found by the system
ENV PATH="/usr/local/bin:$PATH"

# We don't COPY . here because docker-compose uses volumes for hot-reloading
EXPOSE 8000