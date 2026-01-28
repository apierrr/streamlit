FROM python:3.14-slim

WORKDIR /app

# Dépendances
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source
COPY app/ .

# Volume de données
VOLUME /app/data

CMD ["python", "--version"]