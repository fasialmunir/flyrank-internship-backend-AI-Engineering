from fastapi import FastAPI ,HTTPException,status
from pydantic import BaseModel

class TaskCreate(BaseModel):
        title: str | None = None
        done: bool = False

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello Server"}

tasks=[
  {
    "id": 1,
    "title": "Database Migration",
     "done": False
  },
  {
    "id": 2,
    "title": "User Authentication",
    "done": True
  },
  {
    "id": 3,
    "title": "API Documentation",
    "done": True
  },
  {
    "id": 4,
    "title": "Unit Testing",
    "done": False
  },
  {
    "id": 5,
    "title": "Dockerize Application",
    "done": False
  }
]

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/tasks/{id}")
def get_task_by_id(id:int):
    for task in tasks:
        if task["id"]==id:
            return task
    raise HTTPException(status_code=404,detail= {"error":f"Task {id} not found"})  


# @app.post("/tasks",status_code=201)
# def create_task(title:str,done:bool=False):
#     new_id = len(tasks)+1
#     new_task = {"id":new_id,"title":title,"done":done}
#     tasks.append(new_task)
#     return new_task 
     
@app.post("/tasks",status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400,detail={"error":"Title is required"})
    new_id = len(tasks) + 1
    new_task = {"id": new_id, **task.model_dump()}
    tasks.append(new_task)
    return new_task
    