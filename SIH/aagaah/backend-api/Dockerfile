FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/backend-api
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend-api backend-api
COPY data-ingestion data-ingestion
COPY ml-model ml-model
COPY database database
COPY data data
RUN python ml-model/train.py
CMD ["uvicorn", "aagaah.main:app", "--host", "0.0.0.0", "--port", "8000"]
