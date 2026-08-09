import uvicorn, requests, sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional

EXAMPLE_TASKS = [
    ("clean room", 1),
    ("Cooking a meal", 0),
    ("go to the gym", 1),
]


def init_db():
    with sqlite3.connect("tasks.db") as conn:
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs when FastAPI starts up
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


class TaskCreate(BaseModel):
    title: str
    state: Optional[bool] = None 
    
    


@app.get("/", description="Get some details")
def Details():
    return { "name": "Task API", "version": "1.0", "endpoints":  ["/tasks"] }

@app.get("/health", description="Check for the API State")
def CheckHealth():
    return { "status": "ok" }



@app.get("/tasks", description="Get the stored tasks")
def show_all_tasks():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")
    items = c.fetchall()
    return(items)
    
@app.get("/tasks/{id}", description="Get the wanted task")
def get_task(id: int):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    item = c.fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return item


@app.post("/tasks", description="Add a new task")
def add_task(task: TaskCreate):
    if not task.title:
        raise HTTPException(status_code=400, detail="Title is required")
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, False))
    conn.commit()
    task_id = c.lastrowid
    c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    return c.fetchone()


@app.put("/tasks/{id}", description="Update a task")
def update_task(id: int, task: TaskCreate):
    if not task.title or task.state is None:
        raise HTTPException(status_code=400, detail="Empty/Invalid body")

    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (task.title, task.state, id))
    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    conn.commit()
    c.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    return c.fetchone()
        

@app.delete("/tasks/{id}", description="Delete a task")
def delete_task(id: int):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (id,))
    if c.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    conn.commit()
    return Response(status_code=204)
  
    
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)