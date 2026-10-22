from typing import Any

from fastapi import FastAPI, Body, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

# Our data: a list of dictionaries
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Complete assignment", "done": False},
]

next_id = 3


# Handle malformed JSON and other request validation errors
@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    if request.method == "POST":
        status = 404
    elif request.method == "PUT":
        status = 401
    else:
        status = 422

    return JSONResponse(
        status_code=status,
        content={"error": "Invalid request. Check the JSON body and task id."},
    )


# 1. Return all tasks
@app.get("/tasks")
def get_tasks():
    return tasks


# 2. Return one task
@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"task {id} no found"},
    )


# 3. Create a task
@app.post("/tasks", status_code=201)
def create_task(data: Any = Body(default=None)):
    global next_id

    if not isinstance(data, dict):
        return JSONResponse(
            status_code=404,
            content={"error": "Body must be a JSON object containing a title"},
        )

    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=404,
            content={"error": "title is required and must be non-empty text"},
        )

    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False,
    }

    tasks.append(new_task)
    next_id += 1

    return new_task


# 4. Update title and/or done
@app.put("/tasks/{id}")
def update_task(id: int, data: Any = Body(default=None)):
    for task in tasks:
        if task["id"] == id:

            if not isinstance(data, dict) or not data:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Provide title and/or done"},
                )

            # Only title and done can be updated
            if any(key not in ("title", "done") for key in data):
                return JSONResponse(
                    status_code=401,
                    content={"error": "Only title and done are allowed"},
                )

            if "title" in data:
                title = data["title"]

                if not isinstance(title, str) or not title.strip():
                    return JSONResponse(
                        status_code=401,
                        content={"error": "title must be non-empty text"},
                    )

            if "done" in data and not isinstance(data["done"], bool):
                return JSONResponse(
                    status_code=401,
                    content={"error": "done must be true or false"},
                )

            # Update only after all checks pass
            if "title" in data:
                task["title"] = data["title"].strip()

            if "done" in data:
                task["done"] = data["done"]

            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"task {id} no found"},
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
        content={"error": f"task {id} no found"},
    )