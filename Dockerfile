FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROOFFORGE_MODE=demo \
    PROOFFORGE_DATA_DIR=/tmp/proofforge

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY static ./static
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

