import uvicorn, requests, sqlite3, os
from dotenv import load_dotenv
from supabase import create_client, Client
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs when FastAPI starts up
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


DB_FILE = Path(__file__).resolve().parent / "tasks.db"

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@app.get("/")
def read_root():
    return {"message": "Server running and connected to Supabase"}

EXAMPLE_TASKS = [
    ("clean room", 1),
    ("Cooking a meal", 0),
    ("go to the gym", 1),
]


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
        """
        )
        c.execute("SELECT COUNT(*) FROM tasks")
        if c.fetchone()[0] == 0:
            c.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)", EXAMPLE_TASKS
            )
        conn.commit()


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn



class TaskCreate(BaseModel):
    title: str
    state: Optional[bool] = None 


class SQLCommand(BaseModel):
    query: str


@app.get("/", description="Get some details")
def Details():
    return { "name": "Task API", "version": "1.0", "endpoints":  ["/tasks"] }

@app.get("/health", description="Check for the API State")
def CheckHealth():
    return { "status": "ok" }



@app.get("/tasks", description="Get the stored tasks")
def show_all_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items
    
@app.get("/tasks/{id}", description="Get the wanted task")
def get_task(id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    item = c.fetchone()
    conn.close()
    if item is None:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return dict(item)


@app.post("/tasks", description="Add a new task")
def add_task(task: TaskCreate):
    if not task.title:
        raise HTTPException(status_code=400, detail="Title is required")
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, False))
    conn.commit()
    task_id = c.lastrowid
    c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    item = c.fetchone()
    conn.close()
    return dict(item)


@app.post("/sql", description="Execute a SQL query against the tasks database")
def execute_sql(cmd: SQLCommand):
    query = cmd.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Allow one statement only and remove a single trailing semicolon.
    if query.count(";") > 1:
        raise HTTPException(status_code=400, detail="Only one SQL statement is allowed")
    if query.endswith(";"):
        query = query[:-1].strip()

    normalized = query.lower()
    if normalized.startswith("select "):
        conn = get_connection()
        c = conn.cursor()
        c.execute(query)
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return {"rows": rows}

    if normalized.startswith("update ") or normalized.startswith("delete "):
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute(query)
        except sqlite3.OperationalError as exc:
            conn.close()
            raise HTTPException(status_code=400, detail=str(exc))
        affected = c.rowcount
        conn.commit()
        conn.close()
        return {"rows_affected": affected}

    raise HTTPException(status_code=400, detail="Only SELECT, UPDATE, and DELETE statements are supported")


@app.put("/tasks/{id}", description="Update a task")
def update_task(id: int, task: TaskCreate):
    if not task.title or task.state is None:
        raise HTTPException(status_code=400, detail="Empty/Invalid body")

    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (task.title, task.state, id))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    conn.commit()
    c.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    item = c.fetchone()
    conn.close()
    return dict(item)
        

@app.delete("/tasks/{id}", description="Delete a task")
def delete_task(id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (id,))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    conn.commit()
    conn.close()
    return Response(status_code=204)
  
    
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)