# Tasks CRUD API

A clean and fast RESTful CRUD API built with **Python** and **FastAPI** to manage everyday tasks.

## 🚀 How to Install & Run

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

## 📋 API Endpoints Table

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

## 📸 Swagger UI Dashboard

FastAPI automatically generates this interactive dashboard from our codebase:

![Swagger UI Dashboard](./images/swagger-ui.png)

---

## 💻 Sample `curl -i` Response Example

Here is what our `DELETE` route looks like when tested via terminal tools (showing the empty body with a `204` header status):

```http
HTTP/1.1 204 No Content
date: Tue, 20 Oct 2026 06:02:54 GMT 
server: uvicorn 
```


## ⚠️ The Mortality Experiment

After restarting the server, newly created tasks disappeared, and the original tasks reappeared. This happened because tasks are stored in an in-memory Python list, which resets when the server restarts.



## AI vs me

### My first prompt
The following is the original prompt I used, including its wording and status-code mistakes:

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
 

### First AI version: test results
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

### Concrete differences I found
- POST request body: The first AI version did not display the structured request body I wanted in Swagger. I had to type the JSON object manually.
- PUT request body: The update endpoint had the same Swagger problem, making it harder to enter title and done.
- ID generation: The AI used a separate next_id variable. I wanted the new ID calculated from existing IDs: if the highest existing ID is 2, the next ID should be 3.
- Code complexity: My handwritten logic was simpler. The first AI version added a custom request-validation handler and other logic that I had not asked for and found unnecessary for this assignment.

### What did AI do better?
I did not find the first AI version better overall than my handwritten version. Several endpoints worked, but the additional complexity made the code harder for me to understand.

### What did AI get wrong or ignore?
It followed the status codes written in my first prompt, but did not provide the Swagger request-body structure I expected for POST and PUT. Its ID-generation approach also differed from what I wanted.

### What did my prompt forget or get wrong?
The mistake I identified in my prompt was requesting 404 instead of 400 for a missing or empty POST title. The AI followed that incorrect instruction. My original prompt also did not explicitly describe how the request-body fields should appear in Swagger, so the result exposed an assumption I needed to make clearer.

### My second prompt
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

### In this follow-up, I asked AI to:

- Keep GET all tasks, GET by ID, and DELETE unchanged.
- Remove the custom request-validation handler.
- Use HTTPException for the POST title error instead of the manual JSONResponse check.
- Show a structured request body in Swagger for POST and PUT.
- Allow me to set done to true, while keeping its POST default as false.
- Generate an ID from the existing task IDs rather than maintaining a separate next_id variable.

### Second AI version: test results

| Check | Result |
| --- | --- |
| Keep GET, GET by ID, DELETE unchanged | Passed. |
| Remove custom request-validation handler | Passed. |
| Use HTTPException for missing title | Passed. |
| Show structured request body in Swagger | Passed. |
| Allow setting done=true in request body | Passed. |
| Generate ID from existing IDs | Passed. |

I then tested the revised version and confirmed that it worked properly like my handwritten code.

### What changed:

The revised version displayed structured POST and PUT bodies in Swagger, allowed me to set done, and generated IDs from existing tasks without the unnecessary custom validation handler.

### Status-code note:

I identified 404 instead of 400 for an invalid POST title as a mistake in my first prompt, but the follow-up prompt above does not explicitly correct that code; it should not be taken as evidence that the revised version returns 400.

### What I learned:

I need to describe requirements clearly and check the generated code myself. Working endpoints alone do not guarantee that the code matches my intended behavior or is easy for me to understand.

 

## Stage 4: Explored SQLite

#### SQL query:

SELECT * FROM tasks WHERE done = 1;

Result: This query returned all tasks marked as completed (done = 1) in the SQLite database. The same results were visible through the FastAPI GET /tasks endpoint when using the appropriate filter.


## SQLite database

### Why SQLite was chosen

SQLite stores the database in a single file and does not require a separate database server. It needs no manual database-service setup and keeps saved tasks after the application restarts. This makes it suitable for this small learning project.

### Database location and startup

The database file is `tasks.db` in the project root. Run the application from that folder using this single startup command:

```bash
uvicorn main:app --reload
```

The required startup behavior is to create `tasks.db`, create the `tasks` table, and insert the three example tasks automatically when initializing a fresh database. Existing data should remain intact on later restarts, without adding duplicate seed tasks. No manual table creation or SQL import should be needed.

The database file tasks.db is excluded from Git through .gitignore. Each person who clones the project gets a fresh database when they start the application.

### Database screenshot

The following screenshot shows the database opened in DB Browser for SQLite:

![Tasks database opened in DB Browser for SQLite](<./images/DB Browser.png>)

## Stage 4: Exploring SQLite

I ran this query to retrieve completed tasks:

```sql
SELECT * FROM tasks WHERE done = 1;
```

`SELECT *` returns all columns, `FROM tasks` selects the tasks table, and `WHERE done = 1` keeps only completed tasks.

The query returned the tasks marked as completed in the database.

![Completed tasks SQL query and results](<./images/SQL query.png>)

 
###Extra Feature: Task Statistics

Added GET /stats to calculate the total, completed, and pending task counts directly in SQLite using SQL aggregate functions.

Example request:

GET /stats


Example response:

{
  "total": 4,
  "done": 2,
  "open": 2
}


This feature demonstrates how SQL can calculate statistics efficiently without fetching every task into Python first.
 

 