# Utiliser une image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail dans le container
WORKDIR /app

# Copier le fichier requirements.txt
COPY src/requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ .

# Exposer le port 5000
EXPOSE 5000

# Variable d'environnement
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Commande pour lancer l'application
CMD ["python", "app.py"]