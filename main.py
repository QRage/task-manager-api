from fastapi import FastAPI, HTTPException, status
from typing import List, Dict
from datetime import datetime
from contextlib import asynccontextmanager

from models import TaskCreate, TaskPut, TaskPatch, TaskInDB


app = FastAPI(title="Task Management API", version="1.0.0")

fake_db: Dict[int, TaskInDB] = {}
next_id = 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application startup and shutdown events.
    Clears the in-memory database on shutdown.
    """
    global next_id
    yield
    fake_db.clear()


app = FastAPI(title="Task Manager API", lifespan=lifespan)


@app.get("/")
async def root():
    """
    Returns a welcome message and directs to API documentation.

    :return: A dictionary containing a welcome message.
    :rtype: Dict[str, str]
    """
    return {"message": "Welcome to the Task Management API! Check /docs for API documentation."}


@app.get("/tasks", response_model=List[TaskInDB], summary="Get all tasks")
async def get_all_tasks():
    """
    Retrieves a list of all tasks stored in the system.

    :return: A list of TaskInDB objects.
    :rtype: List[TaskInDB]
    """
    return list(fake_db.values())


@app.get("/tasks/{task_id}", response_model=TaskInDB, summary="Get a task by ID")
async def get_task(task_id: int):
    """
    Retrieves a single task by its unique identifier.

    :param task_id: The unique integer ID of the task to retrieve.
    :type task_id: int
    :raises HTTPException: 404 Not Found, if a task with the specified ID does not exist.
    :return: A TaskInDB object representing the found task.
    :rtype: TaskInDB
    """
    if task_id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return fake_db[task_id]


@app.post("/tasks", response_model=TaskInDB, status_code=status.HTTP_201_CREATED, summary="Create a new task")
async def create_task(task: TaskCreate):
    """
    Creates a new task in the system.

    The task includes:
    - **title**: The title of the task (required, string).
    - **description**: An optional description of the task (string).
    - **completed**: The completion status (optional, boolean, defaults to False).

    :param task: A TaskCreate object containing the data for the new task.
    :type task: models.TaskCreate
    :return: The newly created task, including its ID and timestamps.
    :rtype: TaskInDB
    """
    global next_id
    current_time = datetime.now()
    new_task = TaskInDB(
        id=next_id,
        created_at=current_time,
        updated_at=current_time,
        title=task.title,
        description=task.description,
        completed=task.completed
    )
    fake_db[new_task.id] = new_task
    next_id += 1
    return new_task


@app.put("/tasks/{task_id}", response_model=TaskInDB, summary="Update a task by ID")
async def update_task(task_id: int, task: TaskPut):
    """
    Completely updates an existing task identified by its ID.

    This method requires the provision of a complete task object,
    as it replaces the existing resource entirely.

    :param task_id: The unique integer ID of the task to update.
    :type task_id: int
    :param task: A TaskPut object containing all updated data for the task.
    :type task: models.TaskPut
    :raises HTTPException: 404 Not Found, if a task with the specified ID does not exist.
    :return: The fully updated task.
    :rtype: TaskInDB
    """
    if task_id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    existing_task = fake_db[task_id]

    updated_task_obj = TaskInDB(
        id=task_id,
        created_at=existing_task.created_at,
        updated_at=datetime.now(),
        title=task.title,
        description=task.description,
        completed=task.completed
    )

    fake_db[task_id] = updated_task_obj
    return updated_task_obj


@app.patch("/tasks/{task_id}", response_model=TaskInDB, summary="Partially update a task by ID")
async def partial_update_task(task_id: int, task_update: TaskPatch):
    """
    Partially updates an existing task identified by its ID.

    This method allows updating only specific fields of a task,
    without requiring a full object replacement.

    :param task_id: The unique integer ID of the task to partially update.
    :type task_id: int
    :param task_update: A TaskPatch object containing the fields to update.
                        Only specified fields will be modified.
    :type task_update: models.TaskPatch
    :raises HTTPException: 404 Not Found, if a task with the specified ID does not exist.
    :return: The partially updated task.
    :rtype: TaskInDB
    """
    if task_id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    existing_task = fake_db[task_id]

    update_data = task_update.model_dump(exclude_unset=True)
    updated_task_data = existing_task.model_copy(update=update_data)
    
    updated_task_data.updated_at = datetime.now()
    fake_db[task_id] = updated_task_data
    return updated_task_data


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task by ID")
async def delete_task(task_id: int):
    """
    Deletes a task identified by its unique ID.

    :param task_id: The unique integer ID of the task to delete.
    :type task_id: int
    :raises HTTPException: 404 Not Found, if a task with the specified ID does not exist.
    :return: No content is returned (204 No Content) upon successful deletion.
    :rtype: None
    """
    if task_id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    del fake_db[task_id]
    return
