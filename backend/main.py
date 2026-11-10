from fastapi import FastAPI ,HTTPException,status,Response
from pydantic import BaseModel,Field 
import psycopg
import sqlite3
from repository import get_db, init_db, seed_tasks
from supabase_client import supabase
from fastapi.responses import JSONResponse
# from gotrue.errors import AuthApiError
from supabase_auth.errors import AuthApiError


app=FastAPI()

class TaskCreate(BaseModel):
    title: str
    done: bool = False

class AuthRequest(BaseModel):
    email: str | None= None
    password: str | None= None

class TaskUpdate(BaseModel):
    title: str | None = None 
    done: bool | None = None
         
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



@app.post("/auth/signup", status_code=201)
def signup(auth: AuthRequest):

    # Validate email and password
    if not auth.email or not auth.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    try:
        # Register user with Supabase
        response = supabase.auth.sign_up({
            "email": auth.email,
            "password": auth.password
        })

        # Return the registered user
        return JSONResponse(
            status_code=201,
            content=response.user.model_dump(mode="json")
        )

    except AuthApiError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )

@app.post("/auth/login", status_code=200)
def login(auth: AuthRequest):

    # Validate email and password
    if not auth.email or not auth.password:
        raise HTTPException(
            status_code=400,
            detail={"error": "Email and password are required"}
        )

    try:
        # Authenticate user with Supabase
        response = supabase.auth.sign_in_with_password({
            "email": auth.email,
            "password": auth.password
        })

        # Return access and refresh tokens
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except AuthApiError:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid login credentials"}
        )

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
        task = conn.execute("SELECT * FROM tasks WHERE id = %s", (id,)).fetchone() 
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
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
            (task.title, task.done)
        )
        conn.commit()
        new_id = cursor.fetchone()["id"]
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
        query=""" UPDATE tasks SET title = COALESCE (%s,title),done=COALESCE(%s,done)
                        WHERE id=%s"""
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
        query="""delete from tasks where id=%s"""
        cursor=conn.execute(query,(id,))
        conn.commit()
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
