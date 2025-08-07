import logging
import sys
import uvicorn
from fastapi import FastAPI, Query
from threading import Lock
import os
import json
from pydantic import BaseModel
from typing import Dict

# === Config ===
DEFAULT_NAME = "default-counter"
COUNTER_FILE = os.getenv("COUNTER_FILE", os.path.join(os.getcwd(), "counter.json"))

# === Setup unified logging with ISO 8601 timestamps ===
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"  # ISO 8601 without milliseconds

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    stream=sys.stdout,
)

logger = logging.getLogger("riecount")  # your app logger
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = logging.getLogger().handlers  # use root handlers
uvicorn_logger.setLevel(logging.INFO)

class CustomAccessFormatter(logging.Formatter):
    def format(self, record):
        # Format access logs with ISO 8601 timestamp
        ct = self.formatTime(record, datefmt=DATE_FORMAT)
        return f"{ct} - {record.levelname} - {record.getMessage()}"

access_logger = logging.getLogger("uvicorn.access")
for handler in access_logger.handlers:
    handler.setFormatter(CustomAccessFormatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))

app = FastAPI()
lock = Lock()



# === Helper Functions ===

def read_all_counters():
    if not os.path.exists(COUNTER_FILE):
        return {}
    with open(COUNTER_FILE, "r") as f:
        return json.load(f)

def write_all_counters(data: dict):
    with open(COUNTER_FILE, "w") as f:
        json.dump(data, f)

# === Response Models ===

class HealthCheckResponse(BaseModel):
    status: str

class CounterResponse(BaseModel):
    name: str
    count: int

class AllCountersResponse(BaseModel):
    counters: Dict[str, int]

# === API Endpoints ===

@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    return {"status": "ok"}

@app.get("/", response_model=AllCountersResponse)
def get_all_counters():
    with lock:
        data = read_all_counters()
    return {"counters": data}

@app.get("/get_count", response_model=CounterResponse)
def get_count(name: str = Query(DEFAULT_NAME)):
    with lock:
        data = read_all_counters()
        count = data.get(name, 0)
    return {"name": name, "count": count}

@app.post("/count", response_model=CounterResponse)
def increment_count(name: str = Query(DEFAULT_NAME)):
    with lock:
        data = read_all_counters()
        count = data.get(name, 0) + 1
        data[name] = count
        write_all_counters(data)
    logger.info(f"Incremented counter '{name}' to {count}")
    return {"name": name, "count": count}
