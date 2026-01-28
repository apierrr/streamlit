# 🛡️ Le Gardien
## 📊 Description
Dashboard de supervision pour serveur Docker. L'application permet de monitorer la santé des conteneurs (CPU, RAM, Logs) et de les piloter (Start/Stop) via une interface web fluide et sécurisée.

## 🎯 Parcours
Parcours B : Projet Personnel (Monitoring Infrastructure)

## 📁 Dataset
Source : Données temps réel extraites du socket Docker. Stockage : Fichier CSV rotatif généré par un script backend. Variables : Timestamp, Nom, CPU (%), RAM (Mo), Statut.

## 🚀 Fonctionnalités
Monitoring : Graphiques interactifs de consommation et indicateurs d'état (Vert/Rouge).

Logs : Visualisation en direct des 50 dernières lignes de journaux.

Actions : Boutons de contrôle rapide (Démarrer / Arrêter) pour chaque conteneur.

## 🛠️ Technologies Utilisées
Python 3.14

Streamlit

Docker SDK

Pandas

## 📦 Installation Locale
### Cloner et lancer via Docker Compose (Recommandé)
```bash
git clone https://github.com/apierrr/le-gardien.git
cd le-gardien
docker compose up -d --build
```
##🌐 Déploiement
Application déployée via Cloudflare Zero Trust : 👉 https://gardien.apierrr.com

##👥 Équipe
Apierrr - Lead Developer

##📝 Notes
Architecture découplée pour la performance : un service "Logger" collecte les métriques en arrière-plan pendant que le service "Web" affiche l'interface sans latence.
