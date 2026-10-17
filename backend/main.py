from fastapi import FastAPI ,HTTPException
 
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello Server"}

tasks=[
  {
    "id": 1,
    "title": "Database Migration",
    "country": "United States",
    "is_completed": False
  },
  {
    "id": 2,
    "title": "User Authentication",
    "country": "Germany",
    "is_completed": True
  },
  {
    "id": 3,
    "title": "API Documentation",
    "country": "Japan",
    "is_completed": True
  },
  {
    "id": 4,
    "title": "Unit Testing",
    "country": "Canada",
    "is_completed": False
  },
  {
    "id": 5,
    "title": "Dockerize Application",
    "country": "Australia",
    "is_completed": False
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
