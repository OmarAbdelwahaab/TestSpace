import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


class TaskCreate(BaseModel):
    title: str

tasks = [
    [1, "clean room", True],
    [2, "Cooking a meal", False],
    [3, "go to the gym", True],
]

tid = 3


@app.get("/")
def Details():
    return { "name": "Task API", "version": "1.0", "endpoints":  ["/tasks"] }

@app.get("/health")
def CheckHealth():
    return { "status": "ok" }

@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task[0] == id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {id} not found")


@app.post("/tasks")
def add_task(task: TaskCreate):
    global tid
    if task.title == "":
        raise HTTPException(status_code=404)
    tid += 1
    new_task = [tid, task.title, False]
    tasks.append(new_task)
    return tasks



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)