# Task API

This is a simple FastAPI-based task management API backed by SQLite. It supports reading task details, adding new tasks, updating existing tasks, and deleting tasks.

## Why SQLite

SQLite was chosen because it is a single-file embedded database with zero setup, it persists data across process restarts, and it keeps the project lightweight without requiring a separate database server.

## Database file

The database is stored in `tasks.db` at the project root. It is created automatically when the app starts, and it is typically git-ignored so each fresh clone begins with a clean database.

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
| GET | /tasks | Returns all tasks |
| GET | /tasks/{id} | Retrieves a task by its ID |
| POST | /tasks | Creates a new task |
| PUT | /tasks/{id} | Updates an existing task |
| DELETE | /tasks/{id} | Deletes a task by its ID |
| POST | /sql | Executes a SQL query against `tasks.db` |

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

## Example SQL

One example SQL query run in Stage 4:

```sql
UPDATE tasks SET done = 1;
```
