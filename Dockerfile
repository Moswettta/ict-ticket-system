# ICT Ticket System - Production image
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

WORKDIR /app/backend
RUN chmod +x entrypoint.sh

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
