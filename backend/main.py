from fastapi import FastAPI ,HTTPException,status,Response
from pydantic import BaseModel,Field
import copy


class TaskCreate(BaseModel):
        title: str | None = None
        done: bool = False

class TaskUpdate(BaseModel):
        title: str | None =  None 
        done: bool | None = None

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
  }
   
]

BACKUP_TASKS = copy.deepcopy(tasks)

@app.get("/tasks")
def get_tasks(done:bool | None=None ,search: str | None=None):
    """
    Retrieve the full list of all saved tasks.
    """
    tasks_list = tasks
    if done is not None:
        tasks_list = [task for task in tasks_list if task["done"] == done]
    if search: 
        tasks_list = [task for task in tasks_list if search.lower() in task.get("title", "").lower()]
    return tasks_list

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/tasks/{id}")
def get_task_by_id(id:int):
    """
    Retrieve a specific task from the system by its unique ID.
    """
    for task in tasks:
        if task["id"]==id:
            return task
    raise HTTPException(status_code=404,detail= {"error":f"Task {id} not found"})  

     
@app.post("/tasks",status_code=201)
def create_task(task: TaskCreate):
    """
    Create a new task with a title and completion status.
    """
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400,detail={"error":"Title is required"})
    new_id = len(tasks) + 1
    new_task = {"id": new_id, **task.model_dump()}
    tasks.append(new_task)
    return new_task

 
@app.put("/tasks/{id}",status_code=200 )
def update_task(id:int,data:TaskUpdate):
    """
    Update a task's title and/or status by its unique ID.
    """
    update_task=data.model_dump(exclude_unset=True)
    if not update_task:
      raise HTTPException(status_code=400,detail={"error":"request body is required"})
    for task in tasks:
       if task["id"]==id:
        task.update(update_task)
        return task
    raise HTTPException(status_code=404,detail= {"error":f"Task {id} not found"})  


@app.delete("/tasks/{id}",status_code=204, response_class=Response) 
def delete_task(id: int):
    """
    Permanently delete a task from the system using its ID.
    """
    for task in tasks: 
        if task["id"] == id:
            tasks.remove(task)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail={"error": f"Task {id} not found"})

@app.get("/stats")
def get_stats():
    total=len(tasks)
    done=len([task for task in tasks if task["done"]==True])
    open=len([task for task in tasks if task["done"]==False])
    return {"total":total,"done":done,"open":open}

@app.post("/reset",status_code=200)
def reset():
    """
    Reset the tasks list to its initial state.
    """
    global tasks
    tasks=list(BACKUP_TASKS)

    return {"message":"Tasks reset successfully"}
