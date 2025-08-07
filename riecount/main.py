import logging
import sys
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
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

@app.get("/get_all", response_model=AllCountersResponse)
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


@app.get("/", response_class=HTMLResponse)
def homepage():
    with lock:
        data = read_all_counters()
    # Generate HTML for the table
    table_rows = "".join(
        f"<tr><td>{name}</td><td>{count}</td></tr>" for name, count in data.items()
    )
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Counter Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 0;
                background-color: #f4f4f9;
            }}
            table {{
                width: 50%;
                border-collapse: collapse;
                margin: 20px auto;
                background-color: #fff;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #f9f9f9;
            }}
            h1 {{
                text-align: center;
                color: #333;
            }}
            .buttons {{
                text-align: center;
                margin-top: 20px;
            }}
            .buttons a {{
                display: inline-block;
                padding: 10px 20px;
                margin: 5px;
                font-size: 16px;
                color: #fff;
                background-color: #007BFF;
                text-decoration: none;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            .buttons a:hover {{
                background-color: #0056b3;
            }}
        </style>
    </head>
    <body>
        <h1>Counter Dashboard</h1>
        <table>
            <thead>
                <tr>
                    <th>Counter Name</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        <div class="buttons">
            <a href="/docs" target="_blank">Swagger UI</a>
            <a href="/redoc" target="_blank">ReDoc</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)