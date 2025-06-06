FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
# Install requirements without spaCy first
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir spacy==3.7.2 \
    && python -m spacy download en_core_web_sm --no-cache-dir

# Copy project
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["uvicorn", "namesearch.main:app", "--host", "0.0.0.0", "--port", "5000"]
