FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# 1. Install system dependencies required for building many Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 2. Prevent Python from buffering logs (makes debugging easier)
ENV PYTHONUNBUFFERED=1

# 3. Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. Fallback: Copy code for production (compose volumes will override this in dev)
COPY . .

EXPOSE 8000

# 5. Default command (compose can still override this)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]