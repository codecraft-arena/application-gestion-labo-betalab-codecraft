# 🏗️ BetaLab - Application de Gestion de Laboratoire

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/zaz/Application-gestion-labo)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node-18+-orange.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](#)

> **Application web complète de gestion de laboratoire collaboratif**  
> Développée avec FastAPI (Backend) + React 19 (Frontend) + MySQL (DB)

---

## 🎯 Vue d'ensemble

**BetaLab** est une plateforme collaborative pour gérer:
- ✅ **Utilisateurs** avec rôles et validations
- ✅ **Activités** avec workflow d'approbation
- ✅ **Événements** organisés par l'équipe
- ✅ **Questions/Réponses** avec modération
- ✅ **Suggestions** d'améliorations
- ✅ **Contact** direct avec l'équipe

---

## 🚀 Démarrage rapide (5 min)

### 1. **Cloner le projet**
```bash
git clone https://github.com/zaz/Application-gestion-labo.git
cd Application-gestion-labo
```

### 2. **Configurer l'environnement**
```bash
# Backend (Python)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt

# Frontend (Node.js)
cd frontend-react
npm install
cd ..
```

### 3. **Configurer la base de données**
```bash
# Créer fichier .env
cat > .env << 'EOF'
DB_USER=betalab_user
DB_PASSWORD=betalab_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=betalab_db
EOF

# Se connecter à MySQL et créer la base
mysql -u root -p << 'SQL'
CREATE DATABASE betalab_db;
CREATE USER 'betalab_user'@'localhost' IDENTIFIED BY 'betalab_password';
GRANT ALL PRIVILEGES ON betalab_db.* TO 'betalab_user'@'localhost';
FLUSH PRIVILEGES;
SQL
```

### 4. **Lancer l'application**
```bash
# Terminal 1: Backend (FastAPI)
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2: Frontend (React)
cd frontend-react
npm run dev
```

### 5. **Accéder**
- 🌐 **Frontend:** http://localhost:5173
- 🔙 **Backend:** http://127.0.0.1:8000
- 📚 **API Docs:** http://127.0.0.1:8000/docs
- 🔐 **Admin login:**
  - Email: `admin@betalab.fr`
  - Password: `admin123` (changer immédiatement!)

---

## 📚 Documentation complète

### Pour développeurs
→ Lire **[DOCUMENTATION.md](./DOCUMENTATION.md)**
- Architecture détaillée
- Installation pas à pas
- API endpoints
- Configuration
- Dépannage technique

### Pour utilisateurs finaux
→ Lire **[GUIDE_UTILISATEUR.md](./GUIDE_UTILISATEUR.md)**
- Comment s'inscrire
- Comment utiliser les fonctionnalités
- Comment poser des questions
- FAQ et aide

### Pour administrateurs
→ Lire **[GUIDE_ADMIN.md](./GUIDE_ADMIN.md)**
- Comment valider utilisateurs
- Comment modérer le contenu
- Gestion des événements
- Paramètres système
- Sécurité et logs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│        Frontend (React 19 + Vite)       │
│   http://localhost:5173                 │
└────────────────┬────────────────────────┘
                 │ REST API / JSON
┌────────────────┴────────────────────────┐
│       Backend (FastAPI - Python)        │
│   http://127.0.0.1:8000                 │
│  • /api/admin     → Gestion admin       │
│  • /api/user      → Profil utilisateur  │
│  • /api/shared    → Questions/Sugg      │
│  • /connexion     → Authentification    │
└────────────────┬────────────────────────┘
                 │ SQLAlchemy ORM
┌────────────────┴────────────────────────┐
│      Base de Données (MySQL)            │
│   localhost:3306/betalab_db             │
└─────────────────────────────────────────┘
```

---

## 📁 Structure du projet

```
Application-gestion-labo/
├── main.py                    # Point d'entrée FastAPI
├── models.py                  # Modèles de données
├── database.py                # Configuration MySQL
├── requirements.txt           # Dépendances Python
│
├── endpoints/                 # Endpoints organisés
│   ├── admin/                 # Gestion administrative
│   ├── user/                  # Profil utilisateur
│   └── shared/                # Q&A, suggestions
│
├── frontend-react/            # Application React
│   ├── src/
│   │   ├── pages/             # Pages de l'app
│   │   ├── components/        # Composants React
│   │   └── styles/            # Styles CSS
│   └── package.json
│
├── migrations/                # Migrations SQL
├── DOCUMENTATION.md           # 📖 Doc technique complète
├── GUIDE_UTILISATEUR.md       # 👥 Guide utilisateur
├── GUIDE_ADMIN.md             # 🛡️ Guide admin
└── README.md                  # Ce fichier
```

---

## ✨ Fonctionnalités principales

| Fonctionnalité | Utilisateurs | Admin |
|---|---|---|
| **Authentification** | ✅ Inscription/Login | ✅ Gestion admins |
| **Profil** | ✅ Modifier (avec approbation) | ✅ Approuver modifications |
| **Activités** | ✅ Participer / Créer* | ✅ Approuver/Rejeter |
| **Événements** | ✅ S'inscrire | ✅ Créer/Approuver inscriptions |
| **Questions** | ✅ Poser | ✅ Modérer/Répondre |
| **Suggestions** | ✅ Proposer | ✅ Modérer |
| **Dashboard** | ✅ Mes données | ✅ Statistiques système |

*Rôle "Chercheur" ou supérieur

---

## 🔐 Rôles utilisateurs

```
👤 Membre (par défaut)
   ├─ Consulter activités
   ├─ S'inscrire aux événements
   ├─ Poser questions
   └─ Faire suggestions

🔬 Chercheur
   ├─ Tous droits du Membre +
   ├─ Créer/Modifier activités
   └─ Être responsable

👔 Responsable
   ├─ Tous droits du Chercheur +
   └─ Modérer Q&A

🛡️ Admin
   └─ Tous les droits du système
```

---

## 🛠️ Stack technologique

```
Frontend:
  • React 19           - UI framework
  • Vite              - Build tool
  • React Router 7    - Routing
  • Lucide React      - Icons
  • CSS               - Styling

Backend:
  • FastAPI           - Web framework
  • SQLAlchemy        - ORM
  • Pydantic          - Validation
  • PyMySQL           - MySQL driver
  • Bcrypt/Argon2     - Password hashing
  • python-dotenv     - Configuration

Database:
  • MySQL 8.0+        - SQL database
  • Migrations        - Schema versioning

Sécurité:
  • CSRF tokens       - CSRF protection
  • Sessions BD       - Persistent sessions
  • Rate limiting     - Protection abus
  • HTTPS ready       - SSL/TLS support
```

---

## 📊 Commandes utiles

### Backend

```bash
# Lancer le serveur (développement)
uvicorn main:app --reload

# Lancer en production
uvicorn main:app --host 0.0.0.0 --port 8000

# Tester les endpoints
curl http://127.0.0.1:8000/docs

# Vérifier la base de données
mysql -u betalab_user -p betalab_db -e "SHOW TABLES;"
```

### Frontend

```bash
# Développement (hot reload)
npm run dev

# Build pour production
npm run build

# Lint (vérifier code)
npm run lint

# Prévisualiser build
npm run preview
```

### Base de données

```bash
# Sauvegarde
mysqldump -u betalab_user -p betalab_db > backup.sql

# Restauration
mysql -u betalab_user -p betalab_db < backup.sql

# Supprimer et recréer
mysql -u betalab_user -p -e "DROP DATABASE betalab_db; CREATE DATABASE betalab_db;"
```

---

## 🐛 Dépannage rapide

| Problème | Solution |
|---|---|
| **"ModuleNotFoundError"** | Activer venv: `source venv/bin/activate` |
| **"Connection refused" DB** | Lancer MySQL: `sudo systemctl start mysql` |
| **"Port already in use"** | Changer port: `uvicorn main:app --port 8001` |
| **"npm install error"** | Nettoyer: `npm cache clean --force` |
| **"CORS error"** | Vérifier `allow_origins` dans `main.py` |

Pour plus d'aide → Voir [DOCUMENTATION.md - FAQ](./DOCUMENTATION.md#-faq--dépannage)

---

## 🚀 Déploiement

### Options gratuites

| Service | Frontend | Backend | DB |
|---|---|---|---|
| **Vercel** | ✅ | ❌ | ❌ |
| **Netlify** | ✅ | ❌ | ❌ |
| **Railway** | ✅ | ✅ | ✅ |
| **Fly.io** | ❌ | ✅ | ❌ |
| **PlanetScale** | ❌ | ❌ | ✅ |

### Checklist pré-déploiement

- [ ] Changer mot de passe admin
- [ ] Mettre à jour `.env` (credentials sécurisés)
- [ ] Tester HTTPS
- [ ] Configurer domaine
- [ ] Activer backups automatiques
- [ ] Documenter accès d'urgence
- [ ] Configurer monitoring

---

## 📞 Support & Contribution

### Besoin d'aide?

1. 📖 Consulter la [documentation complète](./DOCUMENTATION.md)
2. 📧 Email: admin@betalab.fr
3. 🐛 [Signaler un bug](https://github.com/zaz/Application-gestion-labo/issues)
4. 💬 [Discussions](https://github.com/zaz/Application-gestion-labo/discussions)

### Contribuer

Les contributions sont bienvenues!

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

> Consultez [CONTRIBUTING.md](./CONTRIBUTING.md) pour plus de détails

---

## 📋 Prérequis

- **Python** 3.10+ ([installer](https://www.python.org/downloads/))
- **Node.js** 18+ ([installer](https://nodejs.org/))
- **MySQL** 8.0+ ([installer](https://dev.mysql.com/downloads/))
- **Git** ([installer](https://git-scm.com/))

Vérifier l'installation:
```bash
python3 --version  # 3.10+
node --version     # v18+
mysql --version    # 8.0+
git --version
```

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](./LICENSE) pour plus de détails.

---

## 🎓 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Vite Guide](https://vitejs.dev/guide/)

---

## 👥 Équipe

**BetaLab** est développé et maintenu par l'équipe BetaLab.

- 📧 Contact: admin@betalab.fr
- 🌐 Site: [betalab.fr](https://betalab.fr)
- 📍 Localisation: France

---

## 🗂️ Fichiers importants

| Fichier | Description |
|---|---|
| **DOCUMENTATION.md** | 📖 Documentation technique complète (DEV) |
| **GUIDE_UTILISATEUR.md** | 👥 Guide d'utilisation pour les utilisateurs |
| **GUIDE_ADMIN.md** | 🛡️ Guide de gestion pour administrateurs |
| **requirements.txt** | 📦 Dépendances Python |
| **frontend-react/package.json** | 📦 Dépendances Node.js |
| **.env** | ⚙️ Configuration (ne pas committer!) |
| **models.py** | 🗂️ Modèles SQLAlchemy |
| **main.py** | 🚀 Point d'entrée FastAPI |

---

## ⭐ Statistiques

```
📊 Code Statistics:
  ├─ Lines Backend:      ~2000+
  ├─ Lines Frontend:     ~1500+
  ├─ Lines Database:     ~20 tables
  ├─ API Endpoints:      ~40+
  └─ Composants React:   ~15+

📈 Engagement:
  ├─ Utilisateurs: Production-ready
  ├─ Activités: Modulaire et scalable
  ├─ Sécurité: Protection CSRF, Hashage fort
  └─ Performance: Optimisée
```

---

## 🎯 Roadmap

### V2.0.0 (Actuelle) ✅
- ✅ Authentification robuste
- ✅ Workflow d'approvals
- ✅ Gestion complète utilisateurs
- ✅ Questions/Réponses
- ✅ Suggestions
- ✅ Événements

### V2.1.0 (À venir)
- 🔄 Notifications en temps réel
- 🔄 Export de données
- 🔄 API GraphQL
- 🔄 Dashboard analytics avancé

### V3.0.0 (Futur)
- 🚀 Application mobile
- 🚀 Machine learning recommendations
- 🚀 Intégrations externes
- 🚀 Multilingue

---

## ✅ Checklist de démarrage

- [ ] Clone le repo
- [ ] Installe Python 3.10+
- [ ] Installe Node.js 18+
- [ ] Installe MySQL 8.0+
- [ ] Configure le `.env`
- [ ] Crée la base de données
- [ ] Installe dépendances: `pip install -r requirements.txt`
- [ ] Installe dépendances frontend: `npm install`
- [ ] Lance backend: `uvicorn main:app --reload`
- [ ] Lance frontend: `npm run dev`
- [ ] Accède à http://localhost:5173
- [ ] Change mot de passe admin
- [ ] Lis la documentation
- [ ] Crée ton premier utilisateur

---

## 📞 Questions?

👉 **Voir la [documentation complète](./DOCUMENTATION.md)** pour réponses détaillées!

```
📧 Email:     admin@betalab.fr
🌐 Web:       localhost:5173
📚 Docs:      ./DOCUMENTATION.md
👥 Users:     ./GUIDE_UTILISATEUR.md
🛡️ Admin:     ./GUIDE_ADMIN.md
🐛 Issues:    https://github.com/zaz/Application-gestion-labo/issues
```

---

**Prêt à commencer? → [Démarrage rapide](#-démarrage-rapide-5-min) ↑**

```
╔════════════════════════════════════════╗
║    Bienvenue sur BetaLab v2.0.0! 🚀   ║
║                                        ║
║  Pour commencer, lisez:                ║
║  1. Ce fichier (README.md)             ║
║  2. DOCUMENTATION.md (détails tech)    ║
║  3. GUIDE_UTILISATEUR.md (utiliser)    ║
║  4. GUIDE_ADMIN.md (administrer)       ║
║                                        ║
║  Bon développement! 💻               ║
╚════════════════════════════════════════╝
```

---

**V2.0.0** • **March 2026** • **Production Ready** ✅  
*Last updated: 2026-03-25*

Made with ❤️ by **BetaLab Team**
