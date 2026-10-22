from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Data stored in a list of dictionaries
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Complete assignment", "done": False}
]


# Request body for POST
class TaskCreate(BaseModel):
    title: str = ""
    done: bool = False


# Request body for PUT
class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


# 1. Get all tasks
@app.get("/tasks")
def get_tasks():
    return tasks


# 2. Get a task by ID
@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"task {id} no found"}
    )


# 3. Create a task
@app.post("/tasks", status_code=201)
def create_task(data: TaskCreate):

    if not data.title.strip():
        raise HTTPException(
            status_code=400,
            detail="title is required and cannot be empty"
        )

    # Highest existing ID + 1; starts at 1 if the list is empty
    new_id = max((task["id"] for task in tasks), default=0) + 1

    new_task = {
        "id": new_id,
        "title": data.title.strip(),
        "done": data.done
    }

    tasks.append(new_task)
    return new_task


# 4. Update title and/or done
@app.put("/tasks/{id}")
def update_task(id: int, data: TaskUpdate):

    for task in tasks:
        if task["id"] == id:

            if data.title is None and data.done is None:
                raise HTTPException(
                    status_code=401,
                    detail="Provide title and/or done"
                )

            if data.title is not None:
                if not data.title.strip():
                    raise HTTPException(
                        status_code=401,
                        detail="title cannot be empty"
                    )

                task["title"] = data.title.strip()

            if data.done is not None:
                task["done"] = data.done

            return task

    raise HTTPException(
        status_code=404,
        detail=f"task {id} no found"
    )


# 5. Delete a task
@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"task {id} no found"}
    )