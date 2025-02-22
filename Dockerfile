# Image de base avec Python
FROM python:3.9-slim

# Répertoire de travail
WORKDIR /app

# Installation des dépendances
RUN pip install pandas

# Copie des scripts et fichiers CSV
COPY main.py /app/
COPY products.csv /app/
COPY stores.csv /app/
COPY sales.csv /app/

# Commande par défaut
CMD ["python", "main.py"]