FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# App code
COPY . .

# Copy docs (dashboard HTML etc.)
COPY ../docs ./docs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
