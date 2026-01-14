# DevOps Todo API

API REST simple pour la gestion de tâches avec DevOps complet.

## Technologies
- Python 3.11
- Flask
- Docker
- Kubernetes

## Installation et Utilisation

### Prérequis
- Python 3.11+
- Docker
- Docker Compose

### Option 1 : Lancer localement (sans Docker)
```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API
python src/app.py
```

### Option 2 : Lancer avec Docker



# Ou manuellement
docker build -t todo-api .
docker run -p 5000:5000 todo-api
```

## Endpoints API

- `GET /health` - Health check
- `GET /todos` - Récupérer toutes les tâches
- `POST /todos` - Créer une nouvelle tâche
- `GET /todos/<id>` - Récupérer une tâche spécifique
- `DELETE /todos/<id>` - Supprimer une tâche
- `GET /metrics` - Métriques de l'application

## Exemple d'utilisation
```bash
# Health check
curl http://localhost:5000/health

# Créer une tâche
curl.exe -X POST http://localhost:5000/todos `
  -H "Content-Type: application/json" `
  -d '{"title":"Ma première tâche"}'


# Voir toutes les tâches
curl.exe http://localhost:5000/todos
```

## Développement en cours

- [x] API REST basique
- [x] Dockerisation
- [ ] CI/CD Pipeline
- [ ] Observabilité
- [ ] Sécurité (SAST/DAST)
- [ ] Déploiement Kubernetes