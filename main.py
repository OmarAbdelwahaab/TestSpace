import requests
import uvicorn
import random
from typing import Annotated
from fastapi import FastAPI, HTTPException, Query, Response



app = FastAPI()

items_db = []

t1 = [1 , "clean room" , True]
t2 = [2 , "Cooking a meal" , False]
t3 = [3 , "go to the gym" , True]

tasks = [t1 , t2 ,t3]

@app.get("/")
def Details():
    return { "name": "Task API", "version": "1.0", "endpoints":  ["/tasks"] }

@app.get("/health")
def CheckHealth():
    return { "status": "ok" }

@app.get("/tasks/{id}")
def Get_Tasks(id: int):
    if id == 1:
        return t1
    elif id == 2:
        return t2
    elif id == 3:
        return t3
    else:
        return("status_code=404", { "error": f"Task {id} not found" })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)