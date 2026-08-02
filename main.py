import uvicorn, requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


class TaskCreate(BaseModel):
    title: str
    state: Optional[bool] = None 
    
    
tid = 1

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



@app.put("/tasks/:id")
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

@app.delete("/tasks/:id")
def delete_task(tid: int):
    
    if tid > len(tasks) or tid == 0:
            raise HTTPException(status_code=404, detail=f"Task {tid} not found")
            
    index = tid - 1
    del tasks[index]        
    raise HTTPException(status_code=204)
  
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)