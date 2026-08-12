import uvicorn, requests, sqlite3, os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Response, status, Request
from pydantic import BaseModel
from typing import Optional

@asynccontextmanager
async def lifespan(app: FastAPI):

    init_db()
    yield


app = FastAPI(lifespan=lifespan)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured in .env")
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    ):

    token = credentials.credentials

    try:
        response = supabase.auth.get_user(jwt=token)
        user = response.user

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        return user

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
        

DB_FILE = Path(__file__).resolve().parent / "tasks.db"

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
def read_root():
    return {"message": "Server running and connected to Supabase"}

EXAMPLE_TASKS = [
    ("clean room", True),
    ("Cooking a meal", False),
    ("go to the gym", True),
]

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Create tasks table if missing
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL DEFAULT FALSE
                );
            """)
            
            # Seed only if empty
            cur.execute("SELECT COUNT(*) FROM tasks;")
            count = cur.fetchone()["count"]
            
            if count == 0:
                cur.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s);",
                    EXAMPLE_TASKS
                )
        conn.commit()

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn



class TaskCreate(BaseModel):
    title: str
    done: Optional[bool] = False

class SQLCommand(BaseModel):
    query: str
    
class TaskUpdate(BaseModel):
    title: str
    done: bool

class AuthCredentials(BaseModel):
    email: str
    password: str


@app.get("/", description="Get some details")
def Details():
    return { "name": "Task API", "version": "1.0", "endpoints":  ["/tasks"] }

@app.get("/health", description="Check for the API State")
def CheckHealth():
    return { "status": "ok" }



@app.get("/tasks", description="Get all stored tasks")
def show_all_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks ORDER BY id ASC;")
            items = cur.fetchall()
    return items


@app.get("/tasks/{id}", description="Get a specific task by ID")
def get_task(id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s;", (id,))
            item = cur.fetchone()

    if item is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return item

@app.post("/tasks", status_code=status.HTTP_201_CREATED, description="Add a new task")
def add_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *;",
                (task.title.strip(), task.done or False)
            )
            new_task = cur.fetchone()
        conn.commit()

    return new_task

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
def update_task(id: int, task: TaskUpdate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *;",
                (task.title.strip(), task.done, id)
            )
            updated_task = cur.fetchone()
        conn.commit()

    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return updated_task
        
@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a task")
def delete_task(id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (id,))
            deleted = cur.fetchone()
        conn.commit()

    if deleted is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
  

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(credentials: AuthCredentials):
  
    if not credentials.email.strip() or not credentials.password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    try:
        
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed"
            )


        return response.user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@app.post("/auth/login")
def login(credentials: AuthCredentials):
    if not credentials.email.strip() or not credentials.password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )
        
        
@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
        )

    parts = auth_header.split(" ")
    if len(parts) != 2 or not parts[1].strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
        )

    token = parts[1].strip()

    try:
        response = supabase.auth.get_user(jwt=token)
        user = response.user

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        return user

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )



@app.get("/protected/profile")
def protected_profile(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email}


@app.get("/protected/dashboard")
def protected_dashboard(user=Depends(get_current_user)):
    return {
        "message": f"Welcome to your dashboard, {user.email}!",
        "user_id": user.id,
    }



@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(user=Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed",
        )
        

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)