import sqlite3
from pathlib import Path
from contextlib import contextmanager, asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel


DATABASE = Path(__file__).with_name("tasks.db")


class TaskCreate(BaseModel):
    title: str | None = None
    done: bool = False


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


# Open, commit or roll back, and close the database connection
@contextmanager
def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        with connection:
            yield connection
    finally:
        connection.close()


# Create the table only if it does not exist
def create_table():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
                    CHECK (done IN (0, 1))
            )
        """)


# Insert predefined tasks only when the table is empty
def seed():
    with get_db() as db:
        count = db.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        if count == 0:
            db.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Database Migration", False),
                    ("User Authentication", True),
                    ("API Documentation", True),
                ],
            )


# Run these functions once per application startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    seed()
    yield


app = FastAPI(lifespan=lifespan)


# Convert a database row into a dictionary
def task_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


@app.get("/")
def root():
    return {"message": "Hello Server"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    query = "SELECT * FROM tasks"

    with get_db() as db:
        rows = db.execute(query).fetchall()

    return [task_to_dict(row) for row in rows]


@app.get("/tasks/{id}")
def get_task_by_id(id: int):
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Task {id} not found"},
        )

    return task_to_dict(row)


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail={"error": "Title is required"},
        )

    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task.title.strip(), task.done),
        )

        row = db.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return task_to_dict(row)


@app.put("/tasks/{id}")
def update_task(id: int, data: TaskUpdate):
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=400,
            detail={"error": "Request body is required"},
        )

    if "title" in changes:
        if not changes["title"] or not changes["title"].strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "Title cannot be empty"},
            )

        changes["title"] = changes["title"].strip()

    if "done" in changes and changes["done"] is None:
        raise HTTPException(
            status_code=400,
            detail={"error": "done must be true or false"},
        )

    with get_db() as db:
        row = db.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail={"error": f"Task {id} not found"},
            )

        title = changes.get("title", row["title"])
        done = changes.get("done", row["done"])

        db.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (title, done, id),
        )

        updated_row = db.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (id,),
        ).fetchone()

    return task_to_dict(updated_row)


@app.delete("/tasks/{id}", status_code=204, response_class=Response)
def delete_task(id: int):
    with get_db() as db:
        cursor = db.execute(
            "DELETE FROM tasks WHERE id = ?",
            (id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail={"error": f"Task {id} not found"},
            )

    return Response(status_code=204)


@app.get("/stats")
def get_stats():
    with get_db() as db:
        row = db.execute("""
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(done), 0) AS done
            FROM tasks
        """).fetchone()

    return {
        "total": row["total"],
        "done": row["done"],
        "open": row["total"] - row["done"],
    }