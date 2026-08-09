import uvicorn, requests, sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

tid = 1

tasks = [
    [1, "clean room", True],
    [2, "Cooking a meal", False],
    [3, "go to the gym", True],
]

tid = 3

EXAMPLE_TASKS = [
    (tasks[0][1], 1),
    (tasks[1][1], 0),
    (tasks[2][1], 1),
]


connection = sqlite3.connect('tasks.db')
c = connection.cursor()



def init_db():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        
        c.execute("DROP TABLE IF EXISTS tasks")
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
    for task in tasks:
        if task[0] == id:
            conn = sqlite3.connect('tasks.db')
            c = conn.cursor()
            c.execute("SELECT * FROM tasks WHERE id = (?)", (id,))
            item = c.fetchall()
            return(item)
    raise HTTPException(status_code=404, detail=f"Task {id} not found")


@app.post("/tasks", description="Add a new task")
def add_task(task: TaskCreate):
    global tid
    if task.title == "":
        raise HTTPException(status_code=404)
    tid += 1
    new_task = [tid, task.title, False]
    tasks.append(new_task)
    return tasks



@app.put("/tasks/:id", description="Update a task")
def update_task(task : TaskCreate ,tid : int):
    
    if tid > len(tasks) or tid == 0:
            raise HTTPException(status_code=404)
        
    elif (task.title == "") or (task.state is None):
        raise HTTPException(status_code=400, detail="Empty/Invalid body")
        
    else:
        tid -= 1 
        updatedTask = [tasks[tid][0], task.title, task.state]
        tasks[tid] = updatedTask
        return updatedTask

@app.delete("/tasks/:id", description="Delete a task")
def delete_task(tid: int):
    
    if tid > len(tasks) or tid == 0:
            raise HTTPException(status_code=404, detail=f"Task {tid} not found")
            
    index = tid - 1
    del tasks[index]        
    raise HTTPException(status_code=204)
  
    
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)