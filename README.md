# riecount

`riecount` is a simple REST API built with FastAPI that acts as a counter service. It allows you to increment, retrieve, and manage named counters. The counters are stored in a JSON file, making it lightweight and easy to use.

## Features

- **Health Check**: Check if the service is running.
- **Retrieve All Counters**: Get a list of all counters and their values.
- **Retrieve a Specific Counter**: Get the value of a specific counter by name.
- **Increment a Counter**: Increment the value of a specific counter by 1.

## API Endpoints

1. **Health Check**
   - **GET** `/health`
   - Response: `{ "status": "ok" }`

2. **Retrieve All Counters**
   - **GET** `/`
   - Response: `{ "counters": { "counter_name": count_value, ... } }`

3. **Retrieve a Specific Counter**
   - **GET** `/get_count`
   - Query Parameter: `name` (default: `default-counter`)
   - Response: `{ "name": "counter_name", "count": count_value }`

4. **Increment a Counter**
   - **POST** `/count`
   - Query Parameter: `name` (default: `default-counter`)
   - Response: `{ "name": "counter_name", "count": new_count_value }`

## Running the App Locally

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```
2. Run the app:
    ```bash
    uvicorn riecount.main:app --reload
    ```
3. Access the API:
    - Swagger UI: http://127.0.0.1:8000/docs
    - Redoc: http://127.0.0.1:8000/redoc

## Deploying with Docker Compose

1. Ensure you have Docker and Docker Compose installed.

2. Build and deploy the app using the provided `compose.yml` file:
   ```bash
   docker-compose up -d
   ```

3. The app will be available at [http://localhost:8000](http://localhost:8000).

4. To stop the app:
   ```bash
   docker-compose down
   ```

## Persistent Data

The app uses a JSON file to store counter data. When deployed with Docker Compose, the `compose.yml` file maps the `./data` directory on your host to the container's `/data` directory. This ensures that counter data persists even if the container is restarted.

## Example Usage

- Increment the default counter:
  ```bash
  curl -X POST "http://localhost:8000/count"
  ```

- Retrieve all counters:
  ```bash
  curl "http://localhost:8000/"
  ```

- Retrieve a specific counter:
  ```bash
  curl "http://localhost:8000/get_count?name=test"
  ```

- Check the health of the service:
  ```bash
  curl "http://localhost:8000/health"
  ```

