from fastapi import FastAPI 
 
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
        