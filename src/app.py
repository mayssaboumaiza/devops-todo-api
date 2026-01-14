
from flask import Flask, request, jsonify
import time
import logging
import json
from datetime import datetime, UTC
import uuid
import os

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from flask import Flask, request, make_response


# Créer l'application Flask
app = Flask(__name__)

@app.after_request
def set_security_headers(response):
    # Content Security Policy
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'"

    # Permissions Policy
    response.headers['Permissions-Policy'] = "camera=(), microphone=(), geolocation=()"

    # Anti MIME-sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Server header suppression
    response.headers['Server'] = 'SecureServer'

    # Cache control pour éviter la mise en cache non sécurisée
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)



HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["path", "method", "status"]
)
# Base de données en mémoire (simple pour commencer)
todos = []
trace_ids = {}
request_count = 0


# Fonction pour créer des logs structurés
def log_structured(level, message, **kwargs):
    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    logger.info(json.dumps(log_entry))

# Middleware : s'exécute avant chaque requête
@app.before_request
def before_request():
    global request_count
    request_count += 1  # incrémente toutes les requêtes
    request.trace_id = str(uuid.uuid4())
    request.start_time = time.time()
    log_structured("INFO", "Request started",
                   trace_id=request.trace_id,
                   method=request.method,
                   path=request.path)
    trace_ids[request.trace_id] = {
        "trace_id": request.trace_id,
        "method": request.method,
        "path": request.path,
        "start_time": datetime.now(UTC).isoformat()
    }



# Middleware : s'exécute après chaque requête
@app.after_request
def after_request(response):
    duration = time.time() - request.start_time

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        path=request.path,
        status=response.status_code
    ).inc()

    HTTP_REQUEST_DURATION.labels(
        path=request.path,
        method=request.method,
        status=response.status_code
    ).observe(duration)

    # Compléter la trace
    trace_ids[request.trace_id]["status"] = response.status_code
    trace_ids[request.trace_id]["duration"] = round(duration, 3)

    # Limiter à 100 traces (éviter fuite mémoire)
    if len(trace_ids) > 100:
        trace_ids.pop(next(iter(trace_ids)))

    log_structured(
        "INFO",
        "Request completed",
        trace_id=request.trace_id,
        method=request.method,
        path=request.path,
        status=response.status_code,
        duration=round(duration, 3)
    )

    response.headers["X-Trace-ID"] = request.trace_id
    return response


# ENDPOINT 1 : Vérifier si l'API fonctionne
@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé pour vérifier que l'API fonctionne"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat()
    }), 200

# ENDPOINT 2 : Récupérer toutes les tâches
@app.route('/todos', methods=['GET'])
def get_todos():
    global request_count
    request_count += 1

    return jsonify({
        "todos": todos,
        "count": len(todos),
        "total_requests": request_count
    }), 200


# ENDPOINT 3 : Créer une nouvelle tâche
@app.route('/todos', methods=['POST'])
def create_todo():
    """Crée une nouvelle tâche"""
    try:
        data = request.json
        
        # Validation
        if not data or 'title' not in data:
            log_structured("ERROR", "Invalid request",
                        trace_id=request.trace_id,
                        method=request.method,
                        path=request.path,
                        status=400,
                        error="Missing title")

            return jsonify({"error": "Title is required"}), 400
        
        # Créer la nouvelle tâche
        todo = {
            "id": str(uuid.uuid4()),
            "title": data.get("title"),
            "completed": data.get("completed", False),
            "created_at": datetime.now(UTC).isoformat()
        }
        
        todos.append(todo)
        
        log_structured("INFO", "Todo created",
                      trace_id=request.trace_id,
                      todo_id=todo['id'])
        
        return jsonify(todo), 201
    
    except Exception as e:
        log_structured("ERROR", "Failed to create todo",
                      trace_id=request.trace_id,
                      error=str(e))
        return jsonify({"error": "Internal server error"}), 500

# ENDPOINT 4 : Récupérer une tâche spécifique
@app.route('/todos/<string:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = next((t for t in todos if t['id'] == todo_id), None)

    if not todo:
        return jsonify({"error": "Todo not found"}), 404

    return jsonify(todo), 200


# ENDPOINT 5 : Supprimer une tâche
@app.route('/todos/<string:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Supprime une tâche"""
    global todos
    initial_length = len(todos)
    todos = [t for t in todos if t['id'] != todo_id]
    
    if len(todos) == initial_length:
        return jsonify({"error": "Todo not found"}), 404
    
    log_structured("INFO", "Todo deleted",
                  trace_id=request.trace_id,
                  todo_id=todo_id)
    
    return jsonify({"message": "Todo deleted successfully"}), 200


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "Todo API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "todos": "/todos",
            "metrics": "/metrics"
        }
    }), 200

@app.route('/traces', methods=['GET'])
def get_traces():
    return jsonify(list(trace_ids.values())), 200

@app.route("/todos")
def get_todos():
    todos = [{"id": 1, "task": "Buy milk"}]
    return {"todos": todos}

 

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

# Point d'entrée de l'application
if __name__ == '__main__':
    print("🚀 Starting Todo API...")
    print("📍 API available at: http://localhost:5000")
    print("📊 Metrics at: http://localhost:5000/metrics")
    print("💚 Health check at: http://localhost:5000/health")
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)