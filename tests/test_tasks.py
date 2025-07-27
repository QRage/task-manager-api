from fastapi.testclient import TestClient
import pytest
from datetime import datetime
import json

from main import app, fake_db, next_id
from models import TaskInDB


@pytest.fixture(name="client")
def client_fixture():
    """
    Pytest fixture to provide a test client for the FastAPI application.
    It clears the fake_db and resets next_id before each test to ensure a clean state.

    :yield: A TestClient instance for making requests to the FastAPI app.
    :rtype: TestClient
    """
    fake_db.clear()
    global next_id
    next_id = 1
    with TestClient(app) as client:
        yield client


def test_get_all_tasks_empty_db(client):
    """
    Tests retrieving all tasks when the database is empty.
    Expects an empty list and a 200 OK status.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


# --- Tests for GET /tasks with data ---
def test_get_all_tasks_with_data(client):
    """
    Tests retrieving all tasks when the database contains multiple tasks.
    Verifies the correct number of tasks and their content.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    task_1_obj = TaskInDB(
        id=1,
        title="Test Task 1",
        description="Description 1",
        completed=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    task_2_obj = TaskInDB(
        id=2,
        title="Test Task 2",
        description=None,
        completed=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    fake_db[task_1_obj.id] = task_1_obj
    fake_db[task_2_obj.id] = task_2_obj

    global next_id
    next_id = 3

    response = client.get("/tasks")

    assert response.status_code == 200
    
    response_json = response.json()
    assert len(response_json) == 2

    sorted_response = sorted(response_json, key=lambda x: x["id"])

    assert sorted_response[0]["id"] == task_1_obj.id
    assert sorted_response[0]["title"] == task_1_obj.title
    assert sorted_response[0]["description"] == task_1_obj.description
    assert sorted_response[0]["completed"] == task_1_obj.completed
    assert "created_at" in sorted_response[0] and isinstance(sorted_response[0]["created_at"], str)
    assert "updated_at" in sorted_response[0] and isinstance(sorted_response[0]["updated_at"], str)

    assert sorted_response[1]["id"] == task_2_obj.id
    assert sorted_response[1]["title"] == task_2_obj.title
    assert sorted_response[1]["description"] == task_2_obj.description
    assert sorted_response[1]["completed"] == task_2_obj.completed
    assert "created_at" in sorted_response[1] and isinstance(sorted_response[1]["created_at"], str)
    assert "updated_at" in sorted_response[1] and isinstance(sorted_response[1]["updated_at"], str)


# --- Tests for POST /tasks ---
def test_create_task_success(client):
    """
    Tests successful creation of a new task via POST /tasks.
    Verifies 201 Created status and correct task data in response and in DB.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    task_data = {
        "title": "New Task Title",
        "description": "This is a new task",
        "completed": False
    }
    response = client.post("/tasks", json=task_data)

    assert response.status_code == 201

    response_json = response.json()

    assert "id" in response_json
    assert isinstance(response_json["id"], int)
    assert response_json["id"] > 0

    assert "created_at" in response_json and isinstance(response_json["created_at"], str)
    assert "updated_at" in response_json and isinstance(response_json["updated_at"], str)

    created_task_id = response_json["id"]
    get_response = client.get(f"/tasks/{created_task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == task_data["title"]


def test_create_task_invalid_data(client):
    """
    Tests creating a task with invalid data (e.g., missing required fields).
    Expects a 422 Unprocessable Entity status and a Pydantic validation error.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    invalid_task_data = {
        "description": "This task has no title."
    }
    response = client.post("/tasks", json=invalid_task_data)

    assert response.status_code == 422

    response_json = response.json()
    # print("\n--- Pydantic Validation Error Detail ---")
    # print(response_json) # DEBUG
    # print("--------------------------------------\n")

    assert "detail" in response_json
    assert isinstance(response_json["detail"], list)

    assert any(error.get("type") == "missing" and "title" in error.get("loc", []) for error in response_json["detail"])


# --- Tests for GET /tasks/{task_id} ---
def test_get_task_by_id_successfuly(client):
    """
    Tests successful retrieval of a task by its ID.
    Verifies 200 OK status and correct task data.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    task_data = {
        "title": "Task to Retrieve",
        "description": "This task will be retrieved by ID",
        "completed": False
    }
    create_response = client.post("/tasks", json=task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 200

    retrieved_task = get_response.json()
    assert retrieved_task["id"] == task_id
    assert retrieved_task["title"] == task_data["title"]
    assert retrieved_task["description"] == task_data["description"]
    assert retrieved_task["completed"] == task_data["completed"]
    assert "created_at" in retrieved_task
    assert "updated_at" in retrieved_task


def test_get_task_by_id_not_found(client):
    """
    Tests retrieving a task with a non-existent ID.
    Expects a 404 Not Found status.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    non_existent_id = 999
    response = client.get(f"/tasks/{non_existent_id}")

    assert response.status_code == 404

    response_json = response.json()
    assert "detail" in response_json
    assert response_json["detail"] == "Task not found"


# --- Tests for PUT /tasks/{task_id} ---
def test_update_task_success(client):
    """
    Tests successful full update of a task via PUT /tasks/{task_id}.
    Verifies 200 OK status, updated data, and unchanged creation timestamp.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    initial_task_data = {
        "title": "Old Title",
        "description": "Old Description",
        "completed": False
    }
    create_response = client.post("/tasks", json=initial_task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    updated_task_data = {
        "title": "Updated Title",
        "description": "New Description for the task.",
        "completed": True
    }
    update_response = client.put(f"/tasks/{task_id}", json=updated_task_data)

    assert update_response.status_code == 200

    response_json = update_response.json()
    assert response_json["id"] == task_id
    assert response_json["title"] == updated_task_data["title"]
    assert response_json["description"] == updated_task_data["description"]
    assert response_json["completed"] == updated_task_data["completed"]
    assert response_json["created_at"] == created_task["created_at"]
    assert response_json["updated_at"] != created_task["updated_at"]

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    assert retrieved_task["title"] == updated_task_data["title"]
    assert retrieved_task["description"] == updated_task_data["description"]
    assert retrieved_task["completed"] == updated_task_data["completed"]


def test_update_task_not_found(client):
    """
    Tests updating a task with a non-existent ID.
    Expects a 404 Not Found status.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    non_existent_id = 999
    update_data = {
        "title": "Non-existing Task",
        "description": "Description for a non-existent task.",
        "completed": False
    }
    response = client.put(f"/tasks/{non_existent_id}", json=update_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task_invalid_data(client):
    """
    Tests a full update with invalid data (e.g., missing a required 'title' for PUT).
    Expects a 422 Unprocessable Entity status and unchanged task data.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    initial_task_data = {
        "title": "Task for Invalid Update",
        "description": "Will be updated with bad data.",
        "completed": False
    }
    create_response = client.post("/tasks", json=initial_task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    invalid_update_data = {
        "description": "This should faild as title is missing."
    }
    response = client.put(f"/tasks/{task_id}", json=invalid_update_data)

    assert response.status_code == 422

    response_json = response.json()
    assert "detail" in response_json
    assert isinstance(response_json["detail"], list)
    assert any(error.get("type") == "missing" and "title" in error.get("loc", []) for error in response_json["detail"])
    
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    assert retrieved_task["title"] == initial_task_data["title"]
    assert retrieved_task["description"] == initial_task_data["description"]
    assert retrieved_task["completed"] == initial_task_data["completed"]


# --- Tests for PATCH /tasks/{task_id} ---
def test_patch_task_succesfully(client):
    """
    Tests successful partial update of a task via PATCH /tasks/{task_id}.
    Verifies 200 OK status, partially updated data, and unchanged creation timestamp.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    initial_task_data = {
        "title": "Initial Task Title",
        "description": "This is the original description.",
        "completed": False
    }
    create_response = client.post("/tasks", json=initial_task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]
    initial_created_at = created_task["created_at"]
    initial_updated_at = created_task["updated_at"]

    patch_data = {
        "description": "Updated description via PATCH."
    }
    patch_response = client.patch(f"/tasks/{task_id}", json=patch_data)

    assert patch_response.status_code == 200

    response_json = patch_response.json()
    assert response_json["id"] == task_id
    assert response_json["title"] == initial_task_data["title"]
    assert response_json["description"] == patch_data["description"]
    assert response_json["completed"] == initial_task_data["completed"]
    assert response_json["created_at"] == initial_created_at
    assert response_json["updated_at"] != initial_updated_at

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    assert retrieved_task["description"] == patch_data["description"]
    assert retrieved_task["title"] == initial_task_data["title"]


def test_patch_task_not_found(client):
    """
    Tests partially updating a task with a non-existent ID.
    Expects a 404 Not Found status.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    non_existent_id = 999
    patch_data = {
        "completed": True
    }
    response = client.patch(f"/tasks/{non_existent_id}", json=patch_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_patch_task_invalid_data(client):
    """
    Tests a partial update with invalid data (e.g., 'title' too long).
    Expects a 422 Unprocessable Entity status and unchanged task data.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    initial_task_data = {
        "title": "Short Title",
        "description": "Description.",
        "completed": False
    }
    create_response = client.post("/tasks", json=initial_task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    invalid_patch_data = {
        "title": "a" * 150
    }
    response = client.patch(f"/tasks/{task_id}", json=invalid_patch_data)

    assert response.status_code == 422

    response_json = response.json()
    assert "detail" in response_json
    assert isinstance(response_json["detail"], list)

    assert any(
        "string_too_long" in error.get("type", "") and "title" in error.get("loc", [])
        for error in response_json["detail"]
    )

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    assert retrieved_task["title"] == initial_task_data["title"]


# --- Tests for DELETE /tasks/{task_id} ---
def test_delete_task_successfully(client):
    """
    Tests successful deletion of a task via DELETE /tasks/{task_id}.
    Verifies 204 No Content status and that the task is no longer retrievable.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    initial_task_data = {
        "title": "Task to Delete",
        "description": "This task will be removed.",
        "completed": False
    }
    create_response = client.post("/tasks", json=initial_task_data)
    assert create_response.status_code == 201
    created_task = create_response.json()
    task_id = created_task["id"]

    delete_response = client.delete(f"/tasks/{task_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Task not found"


def test_delete_task_not_found(client):
    """
    Tests attempting to delete a task with a non-existent ID.
    Expects a 404 Not Found status.

    :param client: The FastAPI test client.
    :type client: TestClient
    """
    non_existent_id = 999
    response = client.delete(f"/tasks/{non_existent_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
