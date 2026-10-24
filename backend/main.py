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

@app.get("/tasks/{id}")
def get_task_by_id(id:int):
    """
    Retrieve a specific task from the system by its unique ID.
    """
    with get_db() as conn:
        task = conn.execute("SELECT * FROM tasks WHERE id = ?",(id,)).fetchone()
        if task is None:
            raise HTTPException(status_code=404,detail= {"error":f"Task {id} not found"})  
        return dict(task)   

@app.post('/tasks',status_code=201)
def create_task(task: TaskCreate): 
    """
    Create a new task with a title and completion status.
    """
    with get_db() as conn:
        if not task.title or not task.title.strip():
            raise HTTPException(status_code=400, detail= {"error":"Title is required"})
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task.title, task.done)
        )
        conn.commit()
        new_id = cursor.lastrowid
        return {"id": new_id, **task.dict()}



 
@app.put("/tasks/{id}",status_code=200 )
def update_task(id:int,task:TaskUpdate):
    """
    Update a task's title and/or status by its unique ID.
    """
    update_task=task.model_dump(exclude_unset=True)
    if not update_task:  
      raise HTTPException (status_code=400,detail={"error":"body is required"})
    with  get_db() as conn:
        query=""" UPDATE tasks SET title = COALESCE (?,title),done=COALESCE(?,done)
                        WHERE id=? """
        cursor=conn.execute(query,(task.title,task.done,id))
        conn.commit()
        if cursor.rowcount==0:
            raise HTTPException(status_code=404,detail={"error":f"task {id} not found"})  
        return get_task_by_id(id)     

        

 
@app.delete("/tasks/{id}",status_code=204,response_class=Response)
def delete_task(id:int):
    """
    Permanently delete a task from the system using its ID.
    """
    with get_db() as conn:
        query="""delete from tasks where id=?"""
        cursor=conn.execute(query,(id,))
        conn.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        if cursor.rowcount==0:
            raise HTTPException(status_code=404,detail={"error":f"task {id} not found"})              

          
@app.get("/stats")
def get_stats():
    """
    Retrieve statistics about the tasks in the system.
    """
    with get_db() as conn:
       query="""SELECT  COUNT(*) from tasks"""
       cursor=conn.execute(query).fetchone()
       total=cursor["COUNT(*)"]
       query="""SELECT COUNT(*) FROM tasks WHERE done = 1"""
       cursor=conn.execute(query).fetchone()
       done=cursor["COUNT(*)"]
       open=total-done
       return {"total":total,"done":done,"open":open}
