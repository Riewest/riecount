FROM python:3.11-slim

WORKDIR /app

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY riecount ./riecount

RUN mkdir /data
ENV COUNTER_FILE=/data/counter.json

EXPOSE 8000

CMD ["uvicorn", "riecount.main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
