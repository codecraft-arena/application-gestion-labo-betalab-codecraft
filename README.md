# Application-gestion-labo

Application de gestion de laboratoire développée avec **FastAPI**.

---

## Prérequis

- Python **3.10+** installé sur votre machine
- `git` installé
- `pip` disponible

---

## Installation et exécution

### 1. Cloner le dépôt

```bash
git clone https://github.com/zaz/Application-gestion-labo.git
cd Application-gestion-labo
```

---

### 2. Créer et activer un environnement virtuel

> ⚠️ **Ne jamais installer les dépendances directement dans le Python système. Toujours utiliser un `venv`.**

**Linux / macOS :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

Une fois activé, votre terminal affiche `(venv)` en début de ligne.

---

### 3. Installer les dépendances

> ⚠️ **Le fichier `requirements.txt` liste toutes les dépendances nécessaires. Ne pas sauter cette étape.**

```bash
pip install -r requirements.txt
```

Pour vérifier que toutes les dépendances sont bien installées :
```bash
pip list
```

---

### 4. Lancer l'application FastAPI

```bash
uvicorn main:app --reload
```

- `main` correspond au fichier `main.py` (point d'entrée de l'application)
- `app` est l'instance FastAPI dans ce fichier
- `--reload` active le rechargement automatique lors des modifications (mode développement uniquement)

L'application sera accessible à l'adresse : [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 5. Documentation interactive

FastAPI génère automatiquement une documentation interactive :

| Interface | URL |
|-----------|-----|
| Swagger UI | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| ReDoc | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) |

---

### 6. Désactiver l'environnement virtuel

Une fois votre session de travail terminée :
```bash
deactivate
```

---

## Structure du projet (exemple)

```
Application-gestion-labo/
├── venv/                  # Environnement virtuel (ne pas committer)
├── main.py                # Point d'entrée FastAPI
├── requirements.txt       # Dépendances du projet
└── README.md
```

> 💡 Le dossier `venv/` doit être présent dans le fichier `.gitignore` pour ne pas être poussé sur le dépôt.
