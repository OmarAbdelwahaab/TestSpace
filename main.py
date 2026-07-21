import uvicorn
import random
from typing import Annotated
from fastapi import FastAPI, HTTPException, Query



app = FastAPI()

items_db = []


@app.get("/")
def Details():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
def CheckHealth():
    return { "status": "ok" }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)