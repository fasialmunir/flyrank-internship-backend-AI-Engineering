from fastapi import FastAPI ,HTTPException,status,Response
from pydantic import BaseModel,Field
import copy
import sqlite3

DATABASE_FILE = "tasks.db"

def get_db():
    conn=sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

app=FastAPI()

class TaskCreate(BaseModel):
    title: str
    done: bool = False

class TaskUpdate(BaseModel):
    title: str | None = None 
    done: bool | None = None

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        conn.commit() 

def seed_tasks():
    with get_db() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        if count == 0:
            TASKS_DATA = [
                {"title": "Learn FastAPI", "done": False},
                {"title": "Learn SQLite", "done": True},
                {"title": "Read book", "done": True}
            ]

            for task in TASKS_DATA:
                conn.execute(
                    "INSERT INTO tasks (title, done) VALUES (?, ?)",
                    (task["title"], task["done"])
                )

            conn.commit()         

       
# initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()    
    seed_tasks()       

@app.get("/")
async def root():
    return {"message":"Hello Server"}

@app.get("/health")
async def health():
    return {"status":"ok"} 

@app.get("/tasks")
def get_tasks():
    with get_db() as conn:
        rows= conn.execute("SELECT * FROM tasks")
        tasks=[dict(row) for row in rows]
        return tasks     

 