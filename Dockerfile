FROM python:3.10-slim

# Keep Python lean and unbuffered for clean container logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Install deps first so the layer caches when only app code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY templates ./templates
COPY static ./static

EXPOSE 8000

# Shell form so ${PORT} expands: hosts like Render inject $PORT at runtime.
# Falls back to 8000 locally (matches docker-compose port mapping).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
