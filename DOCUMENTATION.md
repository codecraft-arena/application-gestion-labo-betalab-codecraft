# 📋 Documentation Complète - Application de Gestion de Laboratoire BetaLab

> **Dernière mise à jour:** Mars 2026
> **Version:** 2.0.0
> **Statut:** Production

---

## 🎯 Table des matières

1. [Vue d'ensemble](#-vue-densemble)
2. [Architecture](#-architecture)
3. [Prérequis](#-prérequis)
4. [Installation](#-installation)
5. [Configuration](#-configuration)
6. [Démarrage](#-démarrage)
7. [Structure du projet](#-structure-du-projet)
8. [Fonctionnalités](#-fonctionnalités)
9. [API Endpoints](#-api-endpoints)
10. [Authentification & Rôles](#-authentification--rôles)
11. [Flux de travail](#-flux-de-travail)
12. [FAQ & Dépannage](#-faq--dépannage)

---

## 🏢 Vue d'ensemble

**BetaLab** est une application web complète de gestion de laboratoire développée avec les technologies modernes:

- **Backend:** FastAPI (Python)
- **Frontend:** React 19 + Vite
- **Base de données:** MySQL
- **Authentification:** Session-based avec sécurité CSRF

### Objectifs principaux

✅ Gérer les utilisateurs et leurs rôles  
✅ Organiser les activités et événements  
✅ Collecter questions et suggestions  
✅ Assurer un flux d'approbation pour le contenu utilisateur  
✅ Fournir un tableau de bord intuitif pour administrateurs et utilisateurs  

---

## 🏗️ Architecture

### Schéma global

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React 19)                   │
│  • Dashboard Utilisateur      • Dashboard Admin         │
│  • Authentification           • Gestion du contenu      │
│  • Profil utilisateur         • Approbations           │
└────────────────┬──────────────────────────┬─────────────┘
                 │                          │
                 │  HTTP / REST / JSON      │
                 │                          │
┌────────────────┴──────────────────────────┴─────────────┐
│              BACKEND (FastAPI - Python)                  │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │           Endpoints Organisés                    │   │
│  │  • /api/admin/    → Gestion administrative      │   │
│  │  • /api/user/     → Profil & contributions      │   │
│  │  • /api/shared/   → Questions, suggestions      │   │
│  │  • /connexion     → Authentification            │   │
│  └─────────────────────────────────────────────────┘   │
│                       │                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Services Métier                         │   │
│  │  • Session Manager      • Admin Auth Manager    │   │
│  │  • Email Service        • CSRF Manager          │   │
│  │  • Security & Hashing   • Rate Limiting         │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────┬──────────────────────────┬─────────────┘
                 │                          │
                 │   SQLAlchemy ORM         │
                 │                          │
┌────────────────┴──────────────────────────┴─────────────┐
│              BASE DE DONNÉES (MySQL)                    │
│  • users                • activities                   │
│  • admin_users          • events                       │
│  • sessions             • questions, suggestions      │
│  • csrf_tokens          • profile_modification_request │
│  • invitation_tokens    • *_approval_workflow tables  │
└─────────────────────────────────────────────────────────┘
```

### Architecture modulaire

```
Backend:
endpoints/
├── admin/           → Endpoints administrateur
├── user/            → Endpoints utilisateur
└── shared/          → Endpoints communs (Q/A)

Frontend:
src/
├── pages/           → Composants de pages
├── components/      → Composants réutilisables
├── api/             → Client API
└── styles/          → Styles globaux
```

---

## 📋 Prérequis

### Environnement système

- **OS:** Linux, macOS, ou Windows (WSL2 recommandé)
- **Python:** 3.10+ (vérifier avec `python3 --version`)
- **Node.js:** 18+ (vérifier avec `node --version`)
- **MySQL:** 8.0+ (local ou distant)
- **Git:** Installé et configuré

### Vérifier l'installation

```bash
# Python
python3 --version  # Doit afficher 3.10+

# Node.js
node --version     # Doit afficher v18+
npm --version      # Doit afficher 9+

# MySQL (s'il est installé localement)
mysql --version    # Optionnel mais recommandé

# Git
git --version
```

### Installation des outils

**Linux (Debian/Ubuntu):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm git mysql-server
```

**macOS (avec Homebrew):**
```bash
brew install python@3.11 node git mysql
```

**Windows:**
- Télécharger Python depuis [python.org](https://www.python.org/downloads/)
- Télécharger Node.js depuis [nodejs.org](https://nodejs.org/)
- Télécharger MySQL depuis [mysql.com](https://dev.mysql.com/downloads/mysql/)
- Télécharger Git depuis [git-scm.com](https://git-scm.com/)

---

## 📦 Installation

### Étape 1: Cloner et organiser le projet

```bash
# Cloner le dépôt
git clone https://github.com/zaz/Application-gestion-labo.git
cd Application-gestion-labo

# Vérifier la structure
ls -la
```

### Étape 2: Configurer le backend (Python)

#### 2a. Créer l'environnement virtuel

```bash
# Créer le répertoire venv
python3 -m venv venv

# Activer l'environnement virtuel
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

> ⚠️ **Important:** Ne jamais installer les dépendances dans le Python système!

#### 2b. Installer les dépendances

```bash
# S'assurer que pip est à jour
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

### Étape 3: Configurer le frontend (Node.js)

```bash
# Aller dans le dossier frontend
cd frontend-react

# Installer les dépendances
npm install

# Vérifier l'installation
npm list react react-dom react-router-dom

# Revenir au dossier racine
cd ..
```

---

## ⚙️ Configuration

### Configuration 1: Base de données MySQL

#### Option A: Base locale (recommandé pour développement)

**1. Démarrer MySQL:**
```bash
# Linux/macOS
mysql.server start

# Windows
net start MySQL80  # ou le nom de votre service
```

**2. Se connecter à MySQL:**
```bash
mysql -u root -p
# Entrer le mot de passe root
```

**3. Créer la base de données et l'utilisateur:**
```sql
-- Créer la base de données
CREATE DATABASE betalab_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur
CREATE USER 'betalab_user'@'localhost' IDENTIFIED BY 'betalab_secure_password_2024';

-- Accorder les permissions
GRANT ALL PRIVILEGES ON betalab_db.* TO 'betalab_user'@'localhost';
FLUSH PRIVILEGES;

-- Vérifier
SHOW DATABASES;
EXIT;
```

#### Option B: Base distante (production)

Adaptez les paramètres selon votre provider cloud (AWS RDS, DigitalOcean, etc.)

### Configuration 2: Variables d'environnement

**1. Créer le fichier `.env` à la racine du projet:**
```bash
cat > .env << 'EOF'
# ============================================
# Base de données MySQL
# ============================================
DB_USER=betalab_user
DB_PASSWORD=betalab_secure_password_2024
DB_HOST=localhost
DB_PORT=3306
DB_NAME=betalab_db

# ============================================
# EmailService (optionnel)
# ============================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@betalab.fr

# ============================================
# Security (optionnel, le backend a des defaults)
# ============================================
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
EOF
```

**2. Vérifier le fichier `.env`:**
```bash
cat .env
```

> ⚠️ **Sécurité:** Ne JAMAIS committer le `.env` en production. Ajouter dans `.gitignore`:
```
.env
.env.local
.env.*.local
```

### Configuration 3: Base de données (création des tables)

Les tables se créent automatiquement au démarrage du backend grâce à SQLAlchemy.

Si vous avez besoin de migrations spéciales, consultez les fichiers SQL dans le dossier `migrations/`:
- `002_add_approval_workflow_clean.sql`
- `003_add_approval_columns.sql`
- etc.

Pour importer une migration:
```bash
mysql -u betalab_user -p betalab_db < migrations/002_add_approval_workflow_clean.sql
```

---

## 🚀 Démarrage

### Option 1: Démarrage manuel (développement)

#### Terminal 1: Backend FastAPI

```bash
# S'assurer que venv est activé
source venv/bin/activate  # Linux/macOS
# ou: venv\Scripts\activate  # Windows

# Lancer le serveur FastAPI
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Le backend est maintenant accessible à:
- **API:** http://127.0.0.1:8000
- **Documentation Swagger:** http://127.0.0.1:8000/docs
- **Documentation ReDoc:** http://127.0.0.1:8000/redoc

#### Terminal 2: Frontend Vite

```bash
# Aller dans le dossier frontend
cd frontend-react

# Lancer le serveur de développement
npm run dev
```

Le frontend est maintenant accessible à:
- **Site:** http://127.0.0.1:5173 ou http://localhost:5173

### Option 2: Démarrage avec scripts

**Linux/macOS:**
```bash
# Créer un script de démarrage
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Démarrage de BetaLab..."

# Backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "✅ Backend démarré (PID: $BACKEND_PID)"

# Frontend
cd frontend-react
npm run dev &
FRONTEND_PID=$!
cd ..
echo "✅ Frontend démarré (PID: $FRONTEND_PID)"

echo "🌐 Accédez à l'application sur http://localhost:5173"
echo "📊 Documentation API sur http://localhost:8000/docs"

wait
EOF

chmod +x start.sh
./start.sh
```

### Vérifier que tout fonctionne

```bash
# Test du backend
curl http://127.0.0.1:8000/docs

# Test du frontend
curl http://127.0.0.1:5173

# Test de la base de données
mysql -u betalab_user -p betalab_db -e "SHOW TABLES;"
```

---

## 📂 Structure du projet

### Organisation backend

```
Application-gestion-labo/
│
├── main.py                     # Point d'entrée FastAPI
├── models.py                   # Modèles SQLAlchemy
├── schemas.py                  # Schémas Pydantic
├── database.py                 # Connexion MySQL
├── dependencies.py             # Dépendances injectées
│
├── auth.py                     # Authentification utilisateur
├── admin_auth.py               # Authentification admin
├── security.py                 # CSRF, Rate limiting
├── session_manager.py          # Gestion des sessions
├── email_service.py            # Service d'email
│
├── endpoints/                  # Endpoints organisés
│   ├── admin/                  # Endpoints admin
│   │   ├── admin_auth.py
│   │   ├── admin_users.py      # Gestion utilisateurs
│   │   ├── admin_activities.py # Gestion activités
│   │   ├── admin_events.py     # Gestion événements
│   │   └── approvals.py        # Workflow d'approbation
│   │
│   ├── user/                   # Endpoints utilisateur
│   │   ├── user_auth.py
│   │   ├── user_profile.py     # Profil utilisateur
│   │   ├── user_contributions.py
│   │   └── profile_modifications.py
│   │
│   └── shared/                 # Endpoints communs
│       ├── shared_contact.py   # Formulaire contact
│       ├── shared_questions.py # Questions/réponses
│       └── shared_suggestions.py # Suggestions
│
├── migrations/                 # Migrations SQL
│   ├── 002_add_approval_workflow_clean.sql
│   ├── 003_add_approval_columns.sql
│   └── ...
│
├── requirements.txt            # Dépendances Python
├── .env                        # Variables d'environnement (git ignored)
└── venv/                       # Environnement virtuel (git ignored)
```

### Organisation frontend

```
frontend-react/
│
├── src/
│   ├── main.jsx                # Point d'entrée
│   ├── App.jsx                 # Composant racine
│   │
│   ├── pages/                  # Pages/vues
│   │   ├── Home.jsx            # Accueil
│   │   ├── APropos.jsx         # À propos
│   │   ├── Activites.jsx       # Activités
│   │   ├── Blog.jsx            # Blog
│   │   ├── Contact.jsx         # Formulaire contact
│   │   ├── FAQ.jsx             # FAQ
│   │   ├── Fondateurs.jsx      # Fondateurs
│   │   ├── Login.jsx           # Connexion utilisateur
│   │   ├── AdminLogin.jsx      # Connexion admin
│   │   ├── DashUser.jsx        # Dashboard utilisateur
│   │   └── DashAdmin.jsx       # Dashboard admin
│   │
│   ├── components/             # Composants réutilisables
│   │   ├── Navbar.jsx          # Barre de navigation
│   │   ├── Footer.jsx          # Pied de page
│   │   ├── Layout.jsx          # Mise en page
│   │   ├── HeroSlideshow.jsx   # Carrousel héro
│   │   ├── NeuralCanvas.jsx    # Animation canvas
│   │   └── ...
│   │
│   ├── api/
│   │   └── client.js           # Client API (axios/fetch)
│   │
│   └── styles/
│       └── global.css          # Styles globaux
│
├── public/                     # Assets statiques
│   ├── about/
│   ├── fondateurs/
│   └── ...
│
├── index.html                  # Entry point HTML
├── vite.config.js              # Configuration Vite
├── eslint.config.js            # Configuration ESLint
├── package.json                # Dépendances Node
└── node_modules/               # Dépendances installées (git ignored)
```

---

## ✨ Fonctionnalités

### 1. 👤 Gestion des utilisateurs

| Fonctionnalité | Description |
|---|---|
| **Inscription** | Formulaire d'adhésion avec validation |
| **Authentification** | Login/logout avec sessions persistantes |
| **Rôles** | 4 rôles: `membre`, `chercheur`, `responsable`, `admin` |
| **Profil** | Modification du profil (soumise à approbation admin) |
| **Suspension** | Admin peut suspendre les comptes |
| **Validation** | Les comptes nouveaux doivent être validés par admin |

### 2. 📅 Gestion des activités

| Fonctionnalité | Description |
|---|---|
| **Création** | Utilisateurs créent des activités |
| **Approbation** | Admin approuve/rejette les activités |
| **Liste** | Utilisateurs voient toutes les activités approuvées |
| **Participation** | Les utilisateurs peuvent participer aux activités |
| **Modification** | Modification soumise à approbation |
| **Statut** | en attente, en cours, terminée, etc. |

### 3. 🎪 Gestion des événements

| Fonctionnalité | Description |
|---|---|
| **Création (Admin)** | Administrateurs créent des événements |
| **Inscription** | Les utilisateurs s'inscrivent aux événements |
| **Approbation** | Admin approuve les inscriptions |
| **Détails** | Titre, description, date, lieu |
| **Statuts** | pending, accepted, rejected |
| **Notifications** | Les utilisateurs reçoivent des confirmations |

### 4. ❓ Questions & Réponses

| Fonctionnalité | Description |
|---|---|
| **Poser question** | Les utilisateurs posent des questions |
| **Modération** | Les questions subissent une approbation |
| **Répondre** | Les administrateurs répondent aux questions |
| **Visible** | Les questions approuvées sont visibles à tout |
| **Historique** | Garder l'historique des questions/réponses |

### 5. 💡 Système de suggestions

| Fonctionnalité | Description |
|---|---|
| **Soumission** | Les utilisateurs soumettent des suggestions |
| **Notation** | Note de 1 à 10 pour chaque suggestion |
| **Modération** | Admin approuve/rejette les suggestions |
| **Visibilité** | Suggestions approuvées visibles au public |
| **Feedback** | Admin peut laisser des commentaires |

### 6. 📧 Formulaire de contact

| Fonctionnalité | Description |
|---|---|
| **Email** | Formulaire de contact simple |
| **Sujet** | Catégorisation des messages |
| **Priority** | Marquer comme urgent si nécessaire |
| **Notifications** | Admin reçoit les messages |
| **Réponse auto** | Confirmation à l'utilisateur |

### 7. 🔐 Sécurité & Authentification

| Feature | Description |
|---|---|
| **Hashing** | Bcrypt + Argon2 pour les mots de passe |
| **Sessions** | Persistantes en BD avec expiration |
| **CSRF** | Tokens CSRF pour protéger les formulaires |
| **Rate Limiting** | Protection contre les abus |
| **Cookies** | HttpOnly, Secure, SameSite |

### 8. 🎨 Interface utilisateur

| Composant | Description |
|---|---|
| **Dashboard** | Tableaux de bord pour user et admin |
| **Navigation** | Menu responsive et intuitif |
| **Animations** | Canvas IA, carousels, transitions |
| **Responsive** | Design mobile-first |
| **Thème** | Cohérent avec la charte BetaLab |

---

## 🔌 API Endpoints

### Base URL: `http://127.0.0.1:8000`

### Authentification `/connexion`

```
POST /connexion                    # Connexion utilisateur
POST /admin-login                  # Connexion administrateur
GET  /logout                       # Déconnexion
GET  /csrf-token                   # Obtenir token CSRF
```

### API Utilisateur `/api/user`

```
GET    /api/user/profile                      # Récupérer profil
PUT    /api/user/profile/update               # Modifier profil
PUT    /api/user/profile/change-password      # Changer mot de passe
GET    /api/user/dashboard                    # Tableau de bord
GET    /api/user/contributions                # Mes contributions
GET    /api/user/events                       # Mes événements
```

### API Admin `/api/admin`

#### Gestion utilisateurs
```
GET    /api/admin/users                       # Liste tous utilisateurs
GET    /api/admin/users/{email}               # Détails utilisateur
PUT    /api/admin/users/{email}/validate      # Valider un compte
PUT    /api/admin/users/{email}/suspend       # Suspendre un compte
PUT    /api/admin/users/{email}/role          # Modifier le rôle
DELETE /api/admin/users/{email}               # Supprimer utilisateur
```

#### Gestion activités
```
GET    /api/admin/activities                  # Liste activités
GET    /api/admin/activities/{id}             # Détails activité
POST   /api/admin/activities/{id}/approve     # Approuver activité
POST   /api/admin/activities/{id}/reject      # Rejeter activité
DELETE /api/admin/activities/{id}             # Supprimer activité
```

#### Gestion événements
```
GET    /api/admin/events                      # Liste événements
POST   /api/admin/events                      # Créer événement
GET    /api/admin/events/{id}                 # Détails événement
PUT    /api/admin/events/{id}                 # Modifier événement
DELETE /api/admin/events/{id}                 # Supprimer événement
POST   /api/admin/events/{id}/participants/{email}/approve   # Approuver participant
```

#### Modération
```
GET    /api/admin/approvals                        # Liste approbations
POST   /api/admin/approvals/questions/{id}/approve # Approuver question
POST   /api/admin/approvals/suggestions/{id}/approve # Approuver suggestion
POST   /api/admin/approvals/profiles/{id}/approve  # Approuver modification profil
```

### API Questions `/api/questions`

```
POST   /api/questions                         # Créer question
GET    /api/questions                         # Lister les approuvées
GET    /api/questions/user/{email}            # Questions de l'utilisateur
GET    /api/questions/{id}/responses          # Réponses à la question
POST   /api/admin/questions/{id}/answer       # Admin répond
DELETE /api/admin/questions/{id}              # Supprimer question
```

### API Suggestions `/api/suggestions`

```
POST   /api/suggestions                       # Créer suggestion
GET    /api/suggestions                       # Lister les approuvées
GET    /api/suggestions/user/{email}          # Suggestions de l'utilisateur
DELETE /api/admin/suggestions/{id}            # Supprimer suggestion
```

### API Contact `/api/contact`

```
POST   /api/contact                           # Envoyer message
GET    /api/admin/contact-messages            # Récupérer messages (admin)
```

---

## 🔐 Authentification & Rôles

### Rôles disponibles

| Rôle | Permissions |
|---|---|
| **membre** | Consulter, poser questions, suggérer |
| **chercheur** | Membre + créer/modifier activités |
| **responsable** | Chercheur + modérer contenu Q/A |
| **admin** | Tous les droits |

### Hiérarchie de rôles

```
❌ Non authentifié
  ├─ Voir page d'accueil
  └─ S'enregistrer / Se connecter

✅ Membre (utilisateur standard)
  ├─ Consulter activités
  ├─ S'inscrire aux événements
  ├─ Poser questions
  ├─ Faire suggestions
  └─ Modifier profil*
     (*soumis à approbation admin)

🔬 Chercheur (niveau intermédiaire)
  ├─ Tous les droits du Membre
  ├─ Créer activités*
  ├─ Modifier activités*
  └─ Être responsable d'activités
     (*soumis à approbation admin)

👔 Responsable (superviseur)
  ├─ Tous les droits du Chercheur
  ├─ Modérer questions
  ├─ Modérer suggestions
  └─ Approuver modifications

🛡️ Admin (administrateur)
  ├─ Tous les droits
  ├─ Valider/suspendre comptes
  ├─ Gérer rôles
  ├─ Approuver contenu
  ├─ Créer événements
  ├─ Gérer utilisateurs
  └─ Accéder à tous les tableaux de bord
```

### Flux d'authentification

```
1. Utilisateur saisit email + mot de passe
                    ↓
2. Backend vérifie les identifiants
                    ↓
3. Si valide et compte activé:
   - Créer Session en BD
   - Émettre Cookie de session (HttpOnly)
   - Retourner User data au frontend
                    ↓
4. Frontend stocke session en cookie
                    ↓
5. À chaque requête: Includer cookie dans headers
                    ↓
6. Backend valide le cookie et la session en BD
                    ↓
7. Si session expirée: Rediriger vers login
```

---

## 🔄 Flux de travail

### Workflow d'approbation - Création d'activité

```
Utilisateur crée activité
        ↓
Soumise en BD avec status = "pending_submission"
        ↓
Admin voit l'activité dans le tableau d'approbation
        ↓
Admin choisit: Approuver ✅ ou Rejeter ❌
        ↓
[Si approuvé]           [Si rejeté]
Status = "approved"     Status = "rejected"
Admin notes (optionnel) Admin notes (optionnel)
Visible au public       Visible seulement au créateur
        ↓
Utilisateur peut créer  Utilisateur doit corriger
événements inclus
```

### Workflow d'approbation - Modification de profil

```
Utilisateur modifie profil
        ↓
Demande soumise en BD
        ↓
L'ancienne valeur est gardée
La nouvelle valeur est en attente
        ↓
Admin voit la demande
        ↓
Admin approuve ✅ ou rejette ❌
        ↓
[Si approuvé]                   [Si rejeté]
Profil mis à jour              Profil remain unchanged
Utilisateur notifié            Utilisateur notifié
Ancien log gardé               Ancien log gardé
```

### Workflow d'approbation - Question/Suggestion

```
Utilisateur pose question/suggère
        ↓
Soumise avec visibility = "pending"
        ↓
Admin voit dans tableau de modération
        ↓
Admin approuve ✅ ou rejette ❌
        ↓
[Si approuvé]           [Si rejeté]
Visible au public       Visible seulement au créateur
Peut recevoir réponses  Reste en attente
```

### Workflow d'événement

```
Admin crée événement
        ↓
Utilisateur s'inscrit
        ↓
Inscription = status "pending"
        ↓
Admin approuve ✅ ou rejette ❌
        ↓
[Si approuvé]           [Si rejeté]
status = "accepted"     status = "rejected"
Utilisateur notifié     Utilisateur notifié
Compte inclus           Compte exclu
```

---

## 🛠️ FAQ & Dépannage

### Problèmes courants

#### 1. "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
# Vérifier que venv est activé
source venv/bin/activate  # Linux/macOS

# Réinstaller les dépendances
pip install -r requirements.txt
```

#### 2. "Connection refused" (Base de données)

**Vérifications:**
```bash
# 1. Vérifier que MySQL est lancé
sudo systemctl status mysql  # Linux
brew services list | grep mysql  # macOS

# 2. Vérifier les identifiants .env
cat .env

# 3. Tester la connexion manuelle
mysql -u betalab_user -p -h localhost betalab_db

# 4. Redémarrer MySQL si nécessaire
sudo systemctl restart mysql  # Linux
```

#### 3. "CORS error" au frontend

**Solution:**
Vérifier dans `main.py` que le frontend URL est dans `allow_origins`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],  # Ajouter votre URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. "Port already in use"

**Solution:**
```bash
# Trouver le processus qui utilise le port
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# Tuer le processus
kill -9 <PID>

# Ou utiliser un autre port
uvicorn main:app --port 8001 --reload
```

#### 5. "Compilation error" au frontend

**Solution:**
```bash
cd frontend-react

# Nettoyer les dépendances
rm -rf node_modules
npm cache clean --force

# Réinstaller
npm install

# Redémarrer
npm run dev
```

#### 6. "Mot de passe incorrect" mais je suis sûr

**Vérifier:**
```bash
# 1. Les comptes par défaut
# Username: admin
# Password: admin123

# 2. Réinitialiser mot de passe du compte admin
# Supprimer la table session et se reconnecter

# 3. Regarder les logs du backend (uvicorn)
# Les erreurs d'authentification y sont affichées
```

### Questions fréquentes

**Q: Quelle est la version Python requise?**  
A: Python 3.10+ minimum.

**Q: Puis-je utiliser une base de données autre que MySQL?**  
A: Oui, SQLAlchemy supporte PostgreSQL, SQLite, etc. Modifier `database.py` en conséquence.

**Q: Comment sauvegarder la base de données?**  
A: Utiliser `mysqldump`:
```bash
mysqldump -u betalab_user -p betalab_db > backup.sql
```

**Q: Puis-je déployer en production?**  
A: Oui, consultez la section [Déploiement](#déploiement).

**Q: Comment hoster le site gratuitement?**  
A: Options gratuites:
- Frontend: Vercel, Netlify
- Backend: Render, Railway, Fly.io
- DB: MySQL gratuit chez PlanetScale, AWS RDS tier gratuit

---

## 📋 Checklist de démarrage

Avant de lancer l'application, vérifiez:

- [ ] Python 3.10+ installé
- [ ] Node.js 18+ installé
- [ ] MySQL 8.0+ installé et lancé
- [ ] Git installé
- [ ] Dépôt cloné: `git clone ...`
- [ ] Environnement virtuel créé: `python3 -m venv venv`
- [ ] Env virtuel activé: `source venv/bin/activate`
- [ ] Dépendances Python installées: `pip install -r requirements.txt`
- [ ] Fichier `.env` créé et configuré
- [ ] Base de données créée et utilisateur configuré
- [ ] Dépendances frontend installées: `npm install`
- [ ] Backend lancé: `uvicorn main:app --reload`
- [ ] Frontend lancé: `npm run dev`
- [ ] Accessible sur http://localhost:5173
- [ ] Documentation API sur http://localhost:8000/docs

---

## 🚀 Prochaines étapes

### Après l'installation

1. **Se connecter en admin:**
   - Email: `admin@betalab.fr`
   - Mot de passe: `admin123`
   - ⚠️ Changer immédiatement en production

2. **Créer des utilisateurs de test**
   - Utiliser le formulaire d'adhésion
   - Valider dans le dashboard admin
   - Tester les différents rôles

3. **Tester les fonctionnalités:**
   - Créer activités
   - Poser questions
   - Faire suggestions
   - Approuver/rejeter contenu

4. **Personnaliser:**
   - Modifier les couleurs/logos
   - Ajouter du contenu (pages À propos, etc.)
   - Configurer email service
   - Ajouter des événements

5. **Héberger:**
   - Déployer backend
   - Déployer frontend
   - Configurer domaine
   - Configurer SSL/HTTPS

---

## 📚 Ressources supplémentaires

### Documentation officielle

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Vite Guide](https://vitejs.dev/guide/)
- [MySQL Manual](https://dev.mysql.com/doc/mysql-en/)

### Outils recommandés

- **Postman** ou **Insomnia**: Tester les APIs
- **MySQL Workbench**: Gérer la BD
- **VS Code**: Éditeur de code
- **Git**: Contrôle de version
- **Docker**: Containerisation

### Communauté & Support

- 📧 Email: admin@betalab.fr
- 🐛 Issues GitHub: Signaler bugs
- 💬 Discussions: Questions et suggestions
- 📖 Wiki: Documentation collaborative

---

## 📝 Licence et Crédits

**Projet:** Application de Gestion de Laboratoire BetaLab  
**Version:** 2.0.0  
**Date:** Mars 2026  
**Auteurs:** Équipe BetaLab  

### Stack technologique

- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Frontend:** React 19, Vite, React Router
- **Base de données:** MySQL
- **Sécurité:** Bcrypt, Argon2, CSRF Tokens
- **Hébergement:** À définir

---

**Dernière mise à jour:** Mars 2026  
**Statut:** Production Ready ✅  
**Support:** En cours  

Pour toute question ou problème, contactez l'équipe BetaLab à admin@betalab.fr
