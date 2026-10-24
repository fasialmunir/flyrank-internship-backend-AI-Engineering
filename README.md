 

## Assignment 1: In-Memory Tasks CRUD API

A task-management API built with **Python** and **FastAPI**, using an in-memory list of task dictionaries.

### 🚀 How to Install & Run

You can get this API running locally in under 2 minutes:

```bash

# Install the required packages

pip install fastapi uvicorn

# Start the local development server

uvicorn main:app --reload

```

Once started, open your browser and go to:

* **Interactive Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 📋 API Endpoints Table

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | Returns a system welcome message Hello Server | `200 OK` |
| **GET** | `/health` | Returns the status of the server status:ok | `200 OK` |
| **GET** | `/tasks` | Retrieves the full list of all saved tasks | `200 OK` |
| **GET** | `/tasks/{id}` | Retrieves details of a single task using its unique ID | `200 OK` / `404 Not Found` |
| **POST** | `/tasks` | Creates a brand new task item | `201 Created` |
| **PUT** | `/tasks/{id}` | Replaces a task's title and/or status | `200 OK` / `400 Bad Request` / `404 Not Found` |
| **DELETE**| `/tasks/{id}` | Permanently removes a task (Empty body) | `204 No Content` / `404 Not Found` |

---

### 📸 Swagger UI Dashboard

FastAPI automatically generates this interactive dashboard from our codebase:

![Swagger UI Dashboard](./images/swagger-ui.png)

---

### 💻 Sample `curl -i` Response Example

Here is what our `DELETE` route looks like when tested via terminal tools (showing the empty body with a `204` header status):

```http

HTTP/1.1 204 No Content

date: Tue, 20 Oct 2026 06:02:54 GMT 

server: uvicorn 

```

### ⚠️ The Mortality Experiment

After restarting the server, newly created tasks disappeared, and the original tasks reappeared. This happened because tasks are stored in an in-memory Python list, which resets when the server restarts.

### AI vs me

#### My first prompt

```text
The following records my first prompt and its status-code mistakes. These instructions and results belong to the earlier in-memory assignment.

I am currently building an assignment on how to build FastAPI. Now we are working with five endpoints. Let's create code that meets my requirements.

First endpoint: @app.GET("/tasks")

This endpoint returns all the data stored in my list of dictionaries. The list variable is named tasks, which is actually a list containing task objects.

Each task contains:

id (number)

title (text)

done (True/False)

This will help you understand the data format and sequence.

Second endpoint: @app.GET("/tasks/{id}")

This endpoint returns a single record if the ID matches.

If no task matches the ID, return status code 404 with the error message {"error": "task 99 not found"}.

Third endpoint: @app.POST("/tasks")

Add a new task to the list. Your server should assign the next available ID, set done to False by default, and return the created task with status code 201.

Valid input: If the title is missing or empty, return status code 404 Bad Request with a JSON body explaining what went wrong.

Fourth endpoint: @app.PUT("/tasks/{id}")

Replace the task's title and/or done value with the values provided in the request body. Return the updated task.

If the ID is unknown, return 404. If the request body is empty or invalid, return 401.

Fifth endpoint: @app.DELETE("/tasks/{id}")

Remove the task and return 204 with an empty response body. If the ID is unknown, return 404.
```
#### First AI version: test results

 These are the results I observed while testing the first AI version:

| Check | Result |
| --- | --- |
| GET returns all tasks | Passed. |
| Unknown task ID returns `404` | Passed. |
| POST generates an ID automatically | Passed, but it used a separate `next_id` variable rather than calculating from existing IDs. |
| Empty title returns an error | Passed according to my original prompt, which incorrectly requested `404` instead of `400`. |
| POST body works conveniently in Swagger | Problem: Swagger showed only `"string"`; I had to replace it manually with a JSON object containing `title` and `done`. |
| PUT body works conveniently in Swagger | Same request-body display problem as POST. |
| DELETE returns `204` with an empty body | Passed. |

#### Concrete differences I found

- POST request body: The first AI version did not display the structured request body I wanted in Swagger. I had to type the JSON object manually.

- PUT request body: The update endpoint had the same Swagger problem, making it harder to enter title and done.

- ID generation: The AI used a separate next_id variable. I wanted the new ID calculated from existing IDs: if the highest existing ID is 2, the next ID should be 3.

- Code complexity: My handwritten logic was simpler. The first AI version added a custom request-validation handler and other logic that I had not asked for and found unnecessary for this assignment.

#### What did AI do better?

I did not find the first AI version better overall than my handwritten version. Several endpoints worked, but the additional complexity made the code harder for me to understand.

#### What did AI get wrong or ignore?

It followed the status codes written in my first prompt, but did not provide the Swagger request-body structure I expected for POST and PUT. Its ID-generation approach also differed from what I wanted.

#### What did my prompt forget or get wrong?

The mistake I identified in my prompt was requesting 404 instead of 400 for a missing or empty POST title. The AI followed that incorrect instruction. My original prompt also did not explicitly describe how the request-body fields should appear in Swagger, so the result exposed an assumption I needed to make clearer.

#### My second prompt

```text
You do not understand what I mean. There is no need to handle malformed JSON and other request validation errors.

The GET all tasks, GET task by ID, and DELETE endpoints are working correctly, so they should remain unchanged.

The changes are needed in the other two endpoints. Let's handle them one by one.

In the POST endpoint, the ID should be generated automatically, meaning the user does not need to enter an ID as input. The ID should automatically increase for every new task created. Set done to False by default.

Replace this code:

 
if not isinstance(title, str) or not title.strip():

    return JSONResponse(

        status_code=404,

        content={"error": "title is required and must be non-empty text"},

    )


with an HTTP exception.

When I try to enter data in Swagger UI, it only shows "string" in the request body. The same problem occurs in the PUT method. This is not what I want. I also want to be able to change done to True directly in Swagger UI.

The same requirements apply to the PUT endpoint.

Also, why did you use next_id? You used an increment based on the existing IDs. For example, if there are already two tasks with IDs 1 and 2, the ID of the new task should automatically be 3.
```
#### In this follow-up, I asked AI to:

- Keep GET all tasks, GET by ID, and DELETE unchanged.

- Remove the custom request-validation handler.

- Use HTTPException for the POST title error instead of the manual JSONResponse check.

- Show a structured request body in Swagger for POST and PUT.

- Allow me to set done to true, while keeping its POST default as false.

- Generate an ID from the existing task IDs rather than maintaining a separate next_id variable.

#### Second AI version: test results

| Check | Result |
| --- | --- |
| Keep GET, GET by ID, DELETE unchanged | Passed. |
| Remove custom request-validation handler | Passed. |
| Use HTTPException for missing title | Passed. |
| Show structured request body in Swagger | Passed. |
| Allow setting done=true in request body | Passed. |
| Generate ID from existing IDs | Passed. |

I then tested the revised version and confirmed that it worked properly like my handwritten code.

#### What changed:

The revised version displayed structured POST and PUT bodies in Swagger, allowed me to set done, and generated IDs from existing tasks without the unnecessary custom validation handler.

#### Status-code note:

I identified 404 instead of 400 for an invalid POST title as a mistake in my first prompt, but the follow-up prompt above does not explicitly correct that code; it should not be taken as evidence that the revised version returns 400.

#### What I learned:

I need to describe requirements clearly and check the generated code myself. Working endpoints alone do not guarantee that the code matches my intended behavior or is easy for me to understand.

---

## Assignment 2: Connecting the CRUD API to SQLite

The second assignment replaces the in-memory list with SQLite. Saved tasks now remain available after application restarts. This section includes the database work and today's SQLite AI comparison.

### Install and run the database version

Use Python 3.10 or newer. From the folder containing `main.py`, install the packages if needed:

```bash
pip install fastapi uvicorn
```

Start the application:

```bash
uvicorn main:app --reload
```

Open [Swagger UI](http://127.0.0.1:8000/docs). Python includes `sqlite3`; no separate database server or SQLite Python package is needed.

### API endpoints

| Method | Endpoint | Purpose | Responses |
| --- | --- | --- | --- |
| GET | `/` | Return a welcome message. | `200` |
| GET | `/health` | Return server status. | `200` |
| GET | `/tasks` | Return every stored task. | `200` |
| GET | `/tasks/{id}` | Return a task by ID. | `200`, `404` |
| POST | `/tasks` | Create a task with an automatic ID. | `201`, `400` |
| PUT | `/tasks/{id}` | Update the title, done value, or both. | `200`, `400`, `404` |
| DELETE | `/tasks/{id}` | Delete a task with an empty success response. | `204`, `404` |
| GET | `/stats` | Return total, completed, and open task counts. | `200` |

GET `/tasks` intentionally returns all tasks without search or completion filters. Filtering, a reset endpoint, and restarting IDs at 1 are not requirements for this version.

FastAPI's default validation can also return `422` for invalid field types, malformed JSON, missing required request bodies, or invalid path parameters.

#### Create a task

POST `/tasks` accepts:

```json
{
  "title": "Developer",
  "done": false
}
```

The user does not provide an ID. SQLite generates it automatically. If `done` is omitted, it defaults to `false`. It can also be set to `true`.

A missing, empty, or whitespace-only title returns `400`.

#### Update a task

PUT `/tasks/{id}` accepts either field or both:

```json
{
  "done": true
}
```

An empty object, blank or null title, or null completion value returns `400`. An unknown ID with a valid update body returns `404`.

#### Error format

The application uses `HTTPException` with an error dictionary inside `detail`. For example:

```json
{
  "detail": {
    "error": "Task 99 not found"
  }
}
```

### Why SQLite was chosen

SQLite keeps the database in one file and does not need a separate database server. It is easy to run locally and preserves saved task data across application restarts, making it suitable for this assignment.

### Database location and schema

The database file is `tasks.db`, stored beside `main.py`. Its location is set using:

```python
DATABASE = Path(__file__).with_name("tasks.db")
```

The application creates this table if it does not already exist:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
);
```

| Column | Purpose |
| --- | --- |
| `id` | Automatically generated primary key. |
| `title` | Task title stored as text. |
| `done` | Completion status stored as `0` or `1`. |

API responses convert the stored completion value into JSON `false` or `true`.

The generated database file has been added to `.gitignore`:

```gitignore
tasks.db
```

### Automatic startup and seed data

The application startup lifespan calls `create_table()` and then `seed()` once per startup.

The `seed()` function counts the rows in `tasks`. If the count is zero, it inserts these three predefined tasks:

| Title | done |
| --- | --- |
| Database Migration | false |
| User Authentication | true |
| API Documentation | true |

If the table already contains data, seeding does not insert anything. No manual table creation or SQL import is required.

Because the condition is an empty table, deleting all tasks and restarting the application inserts the predefined tasks again. Ordinary restarts preserve existing rows without multiplying the seed tasks.

#### Database screenshot

![Tasks database in DB Browser for SQLite](<./images/DB Browser.png>)

### Stage 4: Exploring SQLite

I used this query to retrieve completed tasks:

```sql
SELECT * FROM tasks WHERE done = 1;
```

The query returns all columns from rows where the task is marked as completed.

![SQL query showing completed tasks](<./images/SQL query.png>)

### Extra feature: Task statistics

GET `/stats` calculates total, completed, and open task counts directly in SQLite using aggregate functions.

Example request:

```http
GET /stats
```

Example response for a database containing four tasks, two completed:

```json
{
  "total": 4,
  "done": 2,
  "open": 2
}
```

This lets the database calculate counts without fetching every task into Python first.

### Stage 5: Fresh-database checkpoint

Use the following steps to verify automatic setup and persistence:

1. Start with a clean clone, or stop the server and move the existing database aside to preserve its data.
2. Install the dependencies and run `uvicorn main:app --reload`.
3. Confirm that `tasks.db` is created beside `main.py`.
4. Call GET `/tasks` and confirm that a fresh database contains the three predefined tasks.
5. Create another task, restart the server, and confirm that the new task remains saved.
6. Confirm that restarting does not add duplicate seed tasks.

These are verification instructions, not a claim that the checks were executed during this README update.

### Stage 6: AI vs me — SQLite migration

**Review date: 24 October 2026.**

#### My migration prompt

I supplied my existing in-memory source code with the following migration instructions:

```text
this is my exiting code where used list for memory so now we replace it as sqlite database name tasks and table name also tasks it chech first if the the tasks table is not exist the create a table name tasks
id int primarykey autto increament ,
title text ,
done as bollean

also add a seed which if in table data count is zero insert three predefine tasks in table
```

#### My improved migration prompt

I supplied the original source again and clarified the startup and function requirements:

```text
this is my exiting code where used list for memory so now we replace it as sqlite database name tasks and table name also tasks it chech first if the the tasks table is not exist the create a table name tasks
id int primarykey autto increament ,
title text ,
done as bollean

also add a function name  seed which  run only once application restart if in table data count is zero insert three predefine tasks in table
```

These excerpts record the migration instructions shared in the conversation. They do not reproduce all my instructions or the original source supplied with them. Other details, including null handling, were covered elsewhere.

**What changed after the rematch:** The revised AI version used a separate `seed()` function called during application startup after creating the table.

#### What did AI do better?

The latest code supplied as the AI version and the code supplied as my handwritten version are identical, so I cannot identify an improvement over that handwritten copy.

Both versions use a connection helper, parameterized queries, automatic table creation, and conditional seeding. I can explain these features: `get_db()` commits successful changes, rolls back failed transactions, and closes the connection; `?` placeholders pass values separately from SQL commands; and `seed()` inserts the initial tasks only when the table is empty.

#### What did AI get wrong or ignore?

I did not identify any mistakes or ignored requirements in the revised AI version during my review against my stated requirements. GET `/tasks` returns every stored task, as required. Search, completion filters, reset functionality, and resetting IDs were not requirements, so their absence is not an error.


#### What did my prompt forget to specify?

The excerpts above do not contain all my instructions. Details such as handling null values were covered elsewhere, so their absence from these excerpts does not mean I forgot to specify them. I have not identified a missing requirement to report.

#### Comparison of the supplied versions

| Area | AI version | Handwritten version supplied |
| --- | --- | --- |
| Database connection and transaction handling | Uses `get_db()`. | Identical. |
| Table creation and seeding | Creates the table if missing; seeds when empty at startup. | Identical. |
| Parameterized SQL | Uses `?` placeholders for input values. | Identical. |
| Endpoints and validation | Same routes, response handling, and validation logic. | Identical. |

These are comparison observations, not differences. The assignment asks for at least three concrete differences; the identical code copies supplied do not establish any. That part of the checkpoint requires the actual distinct versions, if there are any. The assignment also asks for the full prompt; the excerpts should be supplemented with the remaining original instructions before submission.

#### Runtime checks to record

- [ ] The application starts and creates a missing `tasks.db` automatically.
- [ ] A fresh database contains exactly three predefined tasks.
- [ ] Restarting with existing rows does not duplicate seeds.
- [ ] Created and updated tasks remain saved after restarting.
- [ ] GET, POST, PUT, and DELETE return the expected responses.
- [ ] Blank titles return `400`; unknown task IDs return `404` for otherwise valid requests.
- [ ] DELETE returns `204` with an empty response body.

 

#### Code separation and commit

We have keept the AI implementation in `ai-version/`folder. We have Preserve the handwritten implementation as the main submission. The database path is relative to each Python file, so copies in separate folders use separate database files.

 

#### What I learned

Clear instructions help AI generate the intended implementation. Reviewing code means checking it against the actual requirements, understanding its decisions, and recording real differences and test results accurately.
