# Task API

A lightweight FastAPI service for managing task records with a local SQLite database and Supabase authentication.

## What this project is

This project exposes a simple REST API for task management. It stores task data in a local `tasks.db` SQLite file and uses Supabase for user signup, login, and protected endpoints.

The service includes:
- task listing and retrieval
- task creation, update, and deletion
- a health check endpoint
- Supabase-based authentication for protected routes

## Environment variables

This app loads environment variables from a `.env` file. Create the file from the included example:

```bash
copy .env.example .env
```

Then open `.env` and replace the placeholder values:

```env
SUPABASE_URL=https://your-supabase-project-url.supabase.co
SUPABASE_KEY=your-supabase-api-key
```

## Run the application

From the project root, use this single command:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Once running, the automatic API docs are available at:

```text
http://127.0.0.1:8000/docs
```

## API reference

| Endpoint | Method | Description | Auth required |
|---|---|---|---|
| `/` | GET | Returns API metadata and available routes | No |
| `/health` | GET | Returns a basic health status | No |
| `/tasks` | GET | Lists all tasks | No |
| `/auth/login` | POST | Authenticates a user and returns a bearer token | No |
| `/protected/profile` | GET | Returns the authenticated user profile | Yes |

### Notes

- Use `Authorization: Bearer <token>` for endpoints that require auth.
- The `/auth/login` endpoint returns `access_token`, `refresh_token`, and `token_type`.
- The `tasks.db` file is created automatically in the project root on first startup.

## Notes on the database

The SQLite database is stored in `tasks.db` at the project root and is created automatically when the app starts. This file should not be checked into source control.
