#REAME.md -DevopsProject

1.2 Objectifs
-Développer une API REST fonctionnelle 
-Mettre en place un workflow Git professionnel avec issues et pull requests
-Containeriser l'application avec Docker
-Automatiser le build et le déploiement avec CI/CD
-Implémenter l'observabilité (logs, métriques, tracing)
-Intégrer des tests de sécurité (SAST et DAST)
-Déployer l'application sur Kubernetes

1.3 Application Développée
Todo API : Une API REST de gestion de tâches permettant de créer, lire, modifier et supprimer des tâches. L'application expose également des endpoints pour la santé de l'application et les métriques.

2. Architecture du Projet
┌─────────────┐
│  Developer  │
└──────┬──────┘
       │ git push
       ▼
┌─────────────────┐
│  GitHub Repo    │
│  - Source Code  │
│  - Issues/PRs   │
└────────┬────────┘
         │ trigger
         ▼
┌──────────────────┐
│  GitHub Actions  │
│  - Build         │
│  - Test          │
│  - Security Scan │
│  - Docker Build  │
└────────┬─────────┘
         │ push
         ▼
┌─────────────────┐
│   Docker Hub    │
│  (Image Repo)   │
└────────┬────────┘
         │ pull
         ▼
┌─────────────────┐
│   Kubernetes    │
│  - Deployment   │
│  - Service      │
│  - Monitoring   │
└─────────────────┘

3. Technologies Utilisées
3.1 Backend et Framework
Langage : Python 3.11
Framework : Flask 3.0.0
Justification : Flask est léger, simple à apprendre, et parfait pour créer des APIs REST rapidement

3.2 Containerisation
Docker : Containerisation de l'application
Docker Hub : Registry pour stocker les images

3.3 Orchestration
Kubernetes (Minikube) : Orchestration et déploiement des containers
kubectl : Outil CLI pour gérer Kubernetes

3.4 CI/CD
GitHub Actions : Pipeline d'intégration et déploiement continu
Workflows automatisés : Build, test, scan de sécurité, et push vers Docker Hub

3.5 Observabilité
Prometheus Client : Exposition de métriques
------a-http_requests_total (Counter)Type : Counter (compteur qui ne fait qu'augmenter)
Description : Compte le nombre total de requêtes HTTP reçues par l'APILabels (dimensions) : method : GET, POST, DELETE, etc.
endpoint : /todos, /health, /metrics, etc.
pourquoi cette metrique?
✅ Mesurer le trafic : Savoir combien de requêtes reçoit l'API
✅ Détecter les anomalies : Un pic soudain peut indiquer un problème
✅ Identifier les endpoints populaires : Quels endpoints sont les plus utilisés
✅ Surveiller les erreurs : Combien de 404, 500, etc.

-------http_request_duration_seconds (Histogram)
Type : Histogram (histogramme des durées)
Description : Mesure le temps de réponse de chaque requête HTTP
Labels :method : GET, POST, DELETE  endpoint : /todos, /health, etc.
pourquoi cette metrique ?
✅ Performance : Savoir si l'API est rapide ou lente
✅ SLA : Vérifier qu'on respecte nos objectifs (ex: 95% des requêtes < 100ms)
✅ Dégradation : Détecter si les temps de réponse augmentent
✅ Optimisation : Identifier les endpoints lents à optimiser

Logging structuré : Logs en format JSON
Tracing : Trace ID unique par requête

3.6 Sécurité
Bandit : Analyse statique du code Python (SAST)
OWASP ZAP : Scan dynamique de sécurité (DAST)

4. Fonctionnalités de l'API
4.1 Endpoints Disponibles
/health → montre que l’API fonctionne
/todos → CRUD sur les tâches
/traces → JSON listant les requêtes et leurs traces
/metrics → texte avec métriques Prometheus (http_requests_total, http_request_duration_seconds)--- Prometheus va scrapper ce endpoint périodiquement pour stocker et analyser les métriques.

5. Workflow Git et GitHub
5.1 Gestion des Issues
Méthodologie adoptée :
Création de 5 issues principales correspondant aux grandes étapes du projet
Chaque issue décrit clairement les tâches à accomplir
Utilisation des labels pour catégoriser (feature)

Issues créées :
Issue #1 : Setup Docker containerization
Issue #2 : Setup CI/CD Pipeline with GitHub Actions
Issue #3 : Add observability (metrics, logs, tracing)
Issue #4 : Add security scanning (SAST + DAST)
Issue #5 : Kubernetes deployment setup

5.2 Workflow Branches et Pull Requests
Stratégie de branches :
Branch main : Code stable et testé
Branches feature/* : Une par fonctionnalité/issue

6. Containerisation avec Docker
6.1 Dockerfile
Stratégie :
Image de base légère : python:3.11-slim
Installation des dépendances en cache pour accélérer les builds
Exposition du port 5000
Utilisation de variables d'environnement

Optimisations appliquées :
.dockerignore pour exclure les fichiers inutiles


6.3 Publication sur Docker Hub
Image publiée :
URL : [boumaizamayssa]/todo-api:latest

Commandes utilisées :
bash : docker build -t todo-api:latest .
docker tag todo-api:latest [boumaizamayssa]/todo-api:latest
docker push [boumaizamayssa]/todo-api:latest

7. Pipeline CI/CD
7.1 GitHub Actions Workflow
Fichier : .github/workflows/ci-cd.yml
Jobs configurés :
Test Job
Installation de Python
Installation des dépendances
Exécution des tests (pytest)

Build Job
Build de l'image Docker
Login vers Docker Hub
Push de l'image

Security SAST
Scan avec Bandit
Upload des résultats comme artifacts

Security DAST
Scan avec OWASP ZAP
Génération de rapport(json)

Triggers :
Sur chaque push vers main
Sur chaque pull_request vers main

7.2 Secrets GitHub
Secrets configurés :
DOCKER_USERNAME : Nom d'utilisateur Docker Hub
DOCKER_PASSWORD : Token d'accès Docker Hub généré dans dockerhub

7.3 Résultats du Pipeline
Temps d'exécution moyen 
Statut : ✅ Toutes les étapes passent avec succès

8. Observabilité
8.1 Logs Structurés
Implémentation :
Format JSON pour faciliter le parsing
Informations incluses : timestamp, level, message, trace_id

Exemple de log :
json{
  "timestamp": "2026-01-15T10:30:00.123456", "level": "INFO","message": "Request completed","trace_id": "abc-123-def-456","method": "POST","path":"/todos",
  "status": 201,
  "duration": 0.045
}

8.3 Tracing
Implémentation :
Génération d'un Trace ID unique (UUID) pour chaque requête
Header X-Trace-ID dans toutes les réponses
Endpoint /traces pour visualiser l'historique

Utilité :
Suivi des requêtes à travers le système
Debugging facilité
Corrélation des logs

9. Sécurité
9.1 SAST (Static Application Security Testing)
Outil utilisé : Bandit
Configuration :
bash: bandit -r src/ -f json -o bandit-report.json
Résultats :

Nombre de fichiers analysés : 1
Vulnérabilités critiques : 0
Vulnérabilités moyennes : 0
Vulnérabilités faibles : 1 (app.run avec debug=True)

Actions correctives :
Désactivation du mode debug en production
Utilisation de variables d'environnement pour la configuration

9.2 DAST (Dynamic Application Security Testing)
Outil utilisé : OWASP ZAP
Tests effectués :

Scan de baseline sur tous les endpoints
Détection des vulnérabilités OWASP Top 10
Test d'injection SQL, XSS, etc.

Résultats :

Alertes de risque élevé : 0
Alertes de risque moyen : 0
Recommandations : Ajouter des headers de sécurité (CSP, X-Frame-Options)

10. Déploiement Kubernetes
10.1 Configuration Kubernetes
Environnement utilisé : Minikube (local)
Manifests créés :
Deployment (k8s/deployment.yaml)
Service (k8s/service.yaml)

10.2 Commandes de Déploiement
bash# Démarrer Minikube
minikube start

# Appliquer les manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Vérifier le déploiement
kubectl get pods
kubectl get services

# Accéder à l'application
minikube service todo-api-service --url

10.3 Résultats
État du déploiement :
NAME                        READY   STATUS    RESTARTS   AGE
todo-api-6c8d9f5b4c-abc12   1/1     Running   0          2m
todo-api-6c8d9f5b4c-def34   1/1     Running   0          2m

11. Résultats et Démonstration
11.1 Fonctionnalités Démontrées
✅ API fonctionnelle
Tous les endpoints répondent correctement
Validation des données
Gestion des erreurs

✅ Docker
Image construite et publiée
Application fonctionne dans un container
docker-compose opérationnel

✅ CI/CD
Pipeline s'exécute automatiquement
Build et tests réussis
Image poussée vers Docker Hub

✅ Observabilité
Logs structurés visibles
Métriques exposées et consultables
Tracing fonctionnel

✅ Sécurité
Scans SAST et DAST effectués
Rapports générés
Vulnérabilités identifiées et corrigées

✅ Kubernetes
Déploiement réussi sur Minikube
2 replicas en cours d'exécution
Service accessible


13. Leçons Apprises
13.1 Compétences Techniques Acquises
Git et GitHub :

Maîtrise du workflow branches/PR/merge
Importance des messages de commit clairs
Valeur du peer review

Docker :
Optimisation des images Docker
Utilisation de .dockerignore
Docker Compose pour le développement local

CI/CD :
Automatisation complète du pipeline
Gestion des secrets
Intégration de tests de sécurité

Kubernetes :
Concepts de Pods, Deployments, Services
Configuration des health checks
Gestion des ressources

Observabilité :
Importance des logs structurés
Exposition de métriques
Tracing pour le debugging

13.2 Compétences Transversales
Organisation :
Découpage du travail en tâches (issues)
Planification et priorisation
Documentation continue

13.3 Bonnes Pratiques DevOps
✅ Infrastructure as Code : Tous les configs en fichiers versionnés
✅ Automatisation : Minimiser les actions manuelles
✅ Monitoring : Observer ce qui se passe en production
✅ Sécurité : Intégrer tôt dans le cycle (shift-left)
✅ Documentation : README clair pour faciliter l'onboarding

14. Conclusion
14.1 Objectifs Atteints
Ce projet a permis de mettre en pratique l'ensemble de la chaîne DevOps de manière concrète :
✅ Développement d'une API REST fonctionnelle et bien structurée
✅ Mise en place d'un workflow Git professionnel avec issues, branches et PR
✅ Containerisation complète avec Docker et publication sur Docker Hub
✅ Pipeline CI/CD automatisé avec GitHub Actions
✅ Observabilité avec logs structurés, métriques et tracing
✅ Sécurité avec scans SAST et DAST intégrés
✅ Déploiement réussi sur Kubernetes (Minikube)
✅ Documentation complète et claire
14.2 Améliorations Futures
Court terme :

Ajouter plus de tests unitaires et d'intégration
Implémenter une vraie base de données (PostgreSQL)
Ajouter des tests de charge (JMeter, k6)

Moyen terme :

Déploiement sur un cloud public (AWS, GCP, Azure)
Mise en place d'un monitoring avec Grafana + Prometheus
Configuration d'alertes automatiques

B. Commandes Utiles
bash# Lancer l'API localement
python src/app.py

# Build Docker
docker build -t todo-api .


# Tests
pytest tests/

# Déployer sur Kubernetes
kubectl apply -f k8s/
kubectl get deployments
kubectl get services
kubectl get deploy
# Vérifier les pods
kubectl get pods
kubectl get nodes
# Voir les logs
kubectl logs -f <pod-name>

minikube service todo-api-service --url
$ curl http://127.0.0.1:50547/health

$ curl http://127.0.0.1:50547/todos

$ curl -X POST http://127.0.0.1:50547/todos \
-H "Content-Type: application/json" \
-d '{"title":"Mon premier todo"}'

$ curl http://127.0.0.1:50547/todos/9363d8ee-ea0a-4e0d-932c-3e03b04df9b3

$ curl -X DELETE http://127.0.0.1:50547/todos/9363d8ee-ea0a-4e0d-932c-3e03b04df9b3 

$curl http://127.0.0.1:50547/traces
$curl http://127.0.0.1:50547/metrics



C. Glossaire
CI/CD : Continuous Integration / Continuous Deployment
SAST : Static Application Security Testing
DAST : Dynamic Application Security Testing
API : Application Programming Interface
REST : Representational State Transfer
Pod : Unité de base dans Kubernetes
Deployment : Ressource Kubernetes pour gérer les réplicas
Service : Expose un ensemble de Pods dans Kubernetes