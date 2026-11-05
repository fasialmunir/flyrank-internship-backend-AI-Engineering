import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env", override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")


def get_db():
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)


def seed_tasks():
    with get_db() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()["count"]

        if count == 0:
            tasks_data = [
                {"title": "Learn FastAPI", "done": False},
                {"title": "Learn PostgreSQL", "done": False},
                {"title": "Read Book", "done": True}
            ]

            with conn.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    [
                        (task["title"], task["done"])
                        for task in tasks_data
                    ]
                )
