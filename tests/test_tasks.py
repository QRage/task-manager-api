from fastapi.testclient import TestClient
import pytest
from datetime import datetime
import json

from main import app, fake_db, next_id
from models import TaskInDB


@pytest.fixture(name="client")
def client_fixture():
    fake_db.clear()
    global next_id
    next_id = 1
    with TestClient(app) as client:
        yield client


def test_get_all_tasks_empty_db(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


# --- Tests for GET /tasks with data ---
def test_get_all_tasks_with_data(client):
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
    invalid_task_data = {
        "description": "This task has no title."
    }
    response = client.post("/tasks", json=invalid_task_data)

    assert response.status_code == 422

    response_json = response.json()
    print("\n--- Pydantic Validation Error Detail ---")
    print(response_json) # DEBUG
    print("--------------------------------------\n")

    assert "detail" in response_json
    assert isinstance(response_json["detail"], list)

    assert any(error.get("type") == "missing" and "title" in error.get("loc", []) for error in response_json["detail"])

