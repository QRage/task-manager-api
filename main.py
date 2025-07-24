from fastapi import FastAPI, HTTPException, status
from typing import List, Dict
from datetime import datetime
from contextlib import asynccontextmanager
import uuid

from models import TaskCreate, TaskUpdate, TaskInDB


app = FastAPI(title="Task Management API", version="1.0.0")

fake_db: Dict[int, TaskInDB] = {}
next_id = 1


initial_tasks_data = [
    {"title": "Learn SOLID", "completed": False},
    {"title": "Create presentation", "description": "Create a presentation for the team meeting", "completed": False},
    {"title": "Learn FastAPI", "description": "Study the FastAPI documentation", "completed": True},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global next_id
    for task_data in initial_tasks_data:
        task = TaskInDB(
            id=next_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **task_data
        )
        fake_db[next_id] = task
        next_id += 1
    yield
    fake_db.clear()


app = FastAPI(title="Task Manager API", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Welcome to the Task Management API! Check /docs for API documentation."}


@app.get("/tasks", response_model=List[TaskInDB], summary="Get all tasks")
async def get_all_tasks():
    return list(fake_db.values())


@app.get("/tasks/{task_id}", response_model=TaskInDB, summary="Get a task by ID")
async def get_task(task_id: int):
    if task_id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return fake_db[task_id]


@app.post("/tasks", response_model=TaskInDB, status_code=status.HTTP_201_CREATED, summary="Create a new task")
async def create_task(task: TaskCreate):
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
async def update_task(task_id: int, task: TaskUpdate):
    if task_id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    current_time = datetime.now()
    update_task = TaskInDB(
        id=task_id,
        created_at=fake_db[task_id].created_at,
        updated_at=current_time,
        title=task.title,
        description=task.description,
        completed=task.completed
    )
    fake_db[task_id] = update_task
    return update_task


@app.patch("/tasks/{task_id}", response_model=TaskInDB, summary="Partially update a task by ID")
async def partial_update_task(task_id: int, task_update: TaskUpdate):
    if task_id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    existing_task = fake_db[task_id]
    update_date = task_update.model_dump(exclude_unset=True)
    
    for key, value in update_date.items():
        setattr(existing_task, key, value)
    
    existing_task.updated_at = datetime.now()
    fake_db[task_id] = existing_task

    return existing_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task by ID")
async def delete_task(task_id: int):
    if task_id not in fake_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    del fake_db[task_id]
    return