# Task API

This is a simple FastAPI-based task management API for storing and managing tasks in memory. It supports reading task details, adding new tasks, updating existing tasks, and deleting tasks.

## Install and run

From the project folder, run this single command:

```bash
python -m pip install -r requirements.txt && python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open the Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Returns API name, version, and available task endpoints |
| GET | /health | Checks whether the API is running |
| GET | /tasks/{id} | Retrieves a task by its ID |
| POST | /tasks | Creates a new task |
| PUT | /tasks/:id | Updates an existing task |
| DELETE | /tasks/:id | Deletes a task by its ID |

## Example request

```bash
curl -i http://127.0.0.1:8000/health
```

Example response:

```http
HTTP/1.1 200 OK
date: Sun, 02 Aug 2026 19:31:42 GMT
server: uvicorn
content-length: 15
content-type: application/json

{"status":"ok"}
```
