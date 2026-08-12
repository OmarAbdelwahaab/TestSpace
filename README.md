# Task API (Containerized PostgreSQL Stack)

A lightweight FastAPI service for managing task records running against a PostgreSQL database in Docker, fully orchestrated with Docker Compose[cite: 1, 6].

## What this project is

This project exposes a REST API for task management[cite: 6]. Tasks are stored in a PostgreSQL database container with volume persistence[cite: 1]. The entire stack (FastAPI app + PostgreSQL) starts with a single command[cite: 1].

## Quick Start (One Command)

1. Clone the repository and navigate into the project root[cite: 1].
2. Copy `.env.example` to create your local `.env` file[cite: 1, 3]:
   ```bash
   cp .env.example .env
   ```
3. Start the entire application stack[cite: 1]:
   ```bash
   docker compose up --build
   ```

The API will be available at `http://localhost:8000`[cite: 1]. Interactive OpenAPI docs are available at `http://localhost:8000/docs`.

## Environment Variables

The application relies on variables defined in `.env`[cite: 1, 3, 6]:

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:dev@db:5432/tasks`[cite: 1] |
| `SUPABASE_URL` | Supabase API URL | `[https://your-project.supabase.co](https://your-project.supabase.co)`[cite: 3] |
| `SUPABASE_KEY` | Supabase API Key | `your-supabase-key`[cite: 3] |

## API Endpoints

| Endpoint | Method | Description | Status Codes |
|---|---|---|---|
| `/health` | GET | Basic health check | `200` |
| `/tasks` | GET | List all tasks | `200`[cite: 1] |
| `/tasks/{id}` | GET | Fetch a specific task by ID | `200`, `404`[cite: 1] |
| `/tasks` | POST | Create a new task | `201`, `400`[cite: 1] |
| `/tasks/{id}` | PUT | Update an existing task | `200`, `400`, `404`[cite: 1] |
| `/tasks/{id}` | DELETE | Delete a task | `204`, `404`[cite: 1] |

## Sample `curl` Output

```bash
$ curl -i http://localhost:8000/tasks

HTTP/1.1 200 OK
date: Wed, 12 Aug 2026 09:00:00 GMT
server: uvicorn
content-length: 142
content-type: application/json

[
  {"id": 1, "title": "clean room", "done": true},
  {"id": 2, "title": "Cooking a meal", "done": false},
  {"id": 3, "title": "go to the gym", "done": true}
]
```

## Database Inspection Proof

To query the database inside the container directly[cite: 1]:

```bash
docker exec -it testspace-db-1 psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```
```text
 id |     title      | done 
----+----------------+------
  1 | clean room     | t
  2 | Cooking a meal | f
  3 | go to the gym  | t
(3 rows)
```