import pytest
from src.app import app
import src.app as app_module  # ajouter en haut de votre fichier test


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_get_todos_initially(client):
    response = client.get("/todos")
    assert response.status_code == 200

    data = response.get_json()
    assert "todos" in data
    assert isinstance(data["todos"], list)
    assert "count" in data
    assert "total_requests" in data


def test_create_todo(client):
    response = client.post(
        "/todos",
        json={"title": "CI/CD test todo"}
    )
    assert response.status_code == 201

    data = response.get_json()
    assert data["title"] == "CI/CD test todo"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.get_json()
    assert "total_requests" in data
    assert "total_todos" in data
    assert "completed_todos" in data
    assert "pending_todos" in data

def test_create_todo_missing_title(client):
    response = client.post("/todos", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Title is required"

def test_get_todo_by_id_success(client):
    # Créer une tâche
    response = client.post("/todos", json={"title": "Test"})
    todo_id = response.get_json()["id"]

    # Récupérer par ID
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == todo_id
    assert data["title"] == "Test"

def test_get_todo_by_id_not_found(client):
    response = client.get("/todos/nonexistent-id")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Todo not found"

def test_delete_todo_success(client):
    # Créer une tâche
    response = client.post("/todos", json={"title": "Delete me"})
    todo_id = response.get_json()["id"]

    # Supprimer
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Todo deleted successfully"

def test_delete_todo_not_found(client):
    response = client.delete("/todos/nonexistent-id")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Todo not found"

def test_metrics_counts(client):
    # Réinitialiser la base
    app_module.todos.clear()
    app_module.request_count = 0

    # Créer 2 tâches
    client.post("/todos", json={"title": "Task 1"})
    client.post("/todos", json={"title": "Task 2", "completed": True})

    response = client.get("/metrics")
    data = response.get_json()
    assert data["total_todos"] == 2
    assert data["completed_todos"] == 1
    assert data["pending_todos"] == 1
    assert data["total_requests"] >= 3

def test_index_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["service"] == "Todo API"
    assert data["status"] == "running"
    assert "endpoints" in data

def test_trace_id_in_response(client):
    response = client.get("/health")
    assert "X-Trace-ID" in response.headers
    assert len(response.headers["X-Trace-ID"]) > 0
