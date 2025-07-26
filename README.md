This project is a simple RESTful API for a task manager, developed using FastAPI and Python. It demonstrates the implementation of basic CRUD (Create, Read, Update, Delete) operations for the "Task" resource, using data stored in the server's memory.

🌟 Key Features
**RESTful Principles**: The API is built following REST principles, ensuring predictable and standardized interactions.

**FastAPI**: Using a modern, fast and powerful framework to create APIs in Python.

**CRUD** Operations: Full support for create, read, update and delete tasks.

**Pydantic Models**: Leveraging Pydantic to clearly define data models, including **distinct models for full (PUT) and partial (PATCH) updates**, ensuring robust validation and serialization.

**In-memory "Database"**: For simplicity and demonstration purposes, task data is stored in the server's memory. This means that the data is not persisted across server restarts.

**Automatic Documentation**: FastAPI automatically generates interactive API documentation using Swagger UI and ReDoc, available under /docs and /redoc respectively.

**Testing**: Pytest integration is planned for writing unit and integration tests, ensuring the API is robust and correct.

🚀 Getting Started
These instructions will help you get up and running a copy of the project on your local machine for development and testing.

Prerequisites
Before you begin, make sure you have:  
Python 3.9+ (3.10 or later recommended)
pip (Python package manager)

Installation
Clone the repository:

```
git clone https://github.com/YOUR_GITHUB_NICKNAME/task-manager-api.git

cd task-manager-api
```
(Remember to replace YOUR_GITHUB_NICKNAME with your actual nickname!)

Create and activate a virtual environment:
```
python -m venv venv
```
For Windows:

```
.\venv\Scripts\activate
```
For macOS / Linux:
```
source venv/bin/activate
```
Install dependencies:
```
pip install -r requirements.txt
```
Start the API
Start the server Uvicorn:
```
uvicorn main:app --reload
```
The server will be available at http://127.0.0.1:8000. The --reload flag will automatically reload the server when changes are made to the code files.

🗺️ API Endpoints
After starting the server, you can access the interactive API documentation at the following links:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

Here is an overview of the available endpoints:

| Method  | Endpoint | Descriptionr | Input (Body) | Response |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| GET  | /  | API Greeting  | - | JSON  |
| GET  | /tasks  | Get all tasks  | - | List[TaskInDB]  |
| GET  | /tasks/{task_id}  | Get tasks by ID  | - | TaskInDB  |
| POST  | /tasks  | Create a new task  | TaskCreate  | TaskInDB  |
| PUT  | /tasks/{task_id}  | Fully update a task by ID  | **TaskPut**  | TaskInDB  |
| PATCH  | /tasks/{task_id}  | Partially update a task by ID  | **TaskPatch**  | TaskInDB  |
| DELETE  | /tasks/{task_id}  | Content Cell  | - | 204 No Content  |

### 🧪 Testing

The project utilizes **Pytest** for comprehensive unit and integration testing of all API endpoints, ensuring reliability and correctness.

**To run the tests:**

1.  Make sure you have installed all dependencies (including `pytest` and `httpx`).
2.  From the project root directory, activate your virtual environment.
3.  Run Pytest:
    ```bash
    python -m pytest -vv
    ```
All defined API endpoints (GET, POST, PUT, PATCH, DELETE) have dedicated test cases covering various scenarios including successful operations, invalid input, and handling of non-existent resources.

🤝 Contribution
Contributions are welcome! If you have suggestions for improvements or want to add new features, please open an Issue or Pull Request.

📞 Contact  
[QRage](https://github.com/QRage/)