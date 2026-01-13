
from flask import Flask, request, jsonify
import time
import logging
import json
from datetime import datetime, UTC
import uuid
import os
# Créer l'application Flask
app = Flask(__name__)

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Base de données en mémoire (simple pour commencer)
todos = []
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
    request.trace_id = str(uuid.uuid4())
    request.start_time = time.time()
    log_structured("INFO", "Request started",
                   trace_id=request.trace_id,
                   method=request.method,
                   path=request.path)

# Middleware : s'exécute après chaque requête
@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    log_structured("INFO", "Request completed",
                   trace_id=request.trace_id,
                   method=request.method,
                   path=request.path,
                   status=response.status_code,
                   duration=round(duration, 3))
    response.headers['X-Trace-ID'] = request.trace_id
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

# ENDPOINT 6 : Métriques simples
@app.route('/metrics', methods=['GET'])
def metrics():
    """Endpoint pour exposer des métriques basiques"""
    return jsonify({
        "total_requests": request_count,
        "total_todos": len(todos),
        "completed_todos": sum(1 for t in todos if t.get('completed')),
        "pending_todos": sum(1 for t in todos if not t.get('completed'))
    }), 200

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


# Point d'entrée de l'application
if __name__ == '__main__':
    print("🚀 Starting Todo API...")
    print("📍 API available at: http://localhost:5000")
    print("📊 Metrics at: http://localhost:5000/metrics")
    print("💚 Health check at: http://localhost:5000/health")
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)