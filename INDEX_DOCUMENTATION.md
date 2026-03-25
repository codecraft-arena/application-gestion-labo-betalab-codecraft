# 📚 Index de Documentation - BetaLab

> **Sélectionnez votre profil pour accéder à la documentation appropriée**

---

## 🎯 Sélectionnez votre rôle

### 👨‍💻 Je suis un **Développeur**
*Vous voulez installer, configurer et comprendre le code technique*

**→ Lire:** [📖 DOCUMENTATION.md](./DOCUMENTATION.md)

**Contenu:**
- Architecture complète du projet
- Installation pas à pas (Backend + Frontend)
- Configuration de la base de données
- Comment lancer l'application
- Structure détaillée des dossiers
- Endpoints API complets
- Authentification et sécurité
- FAQ technique & dépannage

**Snippets utiles:**
```bash
# Installation rapide
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install
uvicorn main:app --reload
```

---

### 👥 Je suis un **Utilisateur final**
*Vous voulez utiliser l'application (vous inscrire, participer, etc.)*

**→ Lire:** [👤 GUIDE_UTILISATEUR.md](./GUIDE_UTILISATEUR.md)

**Contenu:**
- Comment s'inscrire et se connecter
- Navigation de l'application
- Créer et participer aux activités
- Poser des questions
- Faire des suggestions
- Consulter mon profil
- Paramètres de sécurité
- FAQ utilisateurs

**Schéma rapide:**
```
1. S'inscrire (formulaire)
   ↓
2. Attendre validation (1-2 jours)
   ↓
3. Se connecter
   ↓
4. Compléter profil
   ↓
5. Explorez & participez!
```

---

### 🛡️ Je suis un **Administrateur**
*Vous gérez les utilisateurs, approuvez le contenu et maintenez le système*

**→ Lire:** [🛡️ GUIDE_ADMIN.md](./GUIDE_ADMIN.md)

**Contenu:**
- Accès et sécurité du compte admin
- Validation des utilisateurs
- Attribution des rôles
- Approbation des activités
- Modération des questions/suggestions
- Gestion des événements
- Paramètres système
- Logs de sécurité
- Troubleshooting admin
- Checklists quotidienne/hebdomadaire/mensuelle

**Vue d'ensemble dashboard:**
```
Dashboard Admin
├─ 📊 Statistiques en temps réel
├─ ⚠️  Éléments urgents
├─ 👥 Utilisateurs à valider
├─ 📋 Contenu à modérer
└─ ⚙️  Configuration système
```

---

### 🌐 Je veux juste **commencer rapidement**
*Vous avez 5 minutes et voulez lancer le projet tout de suite*

**→ Lire:** [📖 README_COMPLET.md](./README_COMPLET.md) (section "Démarrage rapide")

**Résumé au format condensé:**
1. Clone: `git clone ...`
2. Installe: `pip install -r requirements.txt && npm install`
3. Configure `.env` avec BD
4. Lance: `uvicorn main:app --reload` et `npm run dev`
5. Va sur http://localhost:5173

---

## 📚 Tous les guides disponibles

| Document | Pour qui? | Contenu |
|---|---|---|
| **README_COMPLET.md** | 🌐 Tous | Vue d'ensemble, démarrage rapide, stack tech |
| **DOCUMENTATION.md** | 👨‍💻 Dev | Tech complète, API, installation détaillée |
| **GUIDE_UTILISATEUR.md** | 👥 Users | Utilisation de l'app, FAQ, bonnes pratiques |
| **GUIDE_ADMIN.md** | 🛡️ Admin | Gestion système, modération, sécurité |
| **INDEX_DOCUMENTATION.md** | 📚 Tous | Ce fichier - navigation centrale |

---

## 🗺️ Carte de navigation

```
Nouveau sur le projet?
    ├─ Développeur?
    │   └─→ Voir "DOCUMENTATION.md"
    │       ├─ Installation
    │       ├─ Architecture
    │       └─ API Endpoints
    │
    ├─ Utilisateur?
    │   └─→ Voir "GUIDE_UTILISATEUR.md"
    │       ├─ S'inscrire
    │       ├─ Utiliser les features
    │       └─ FAQ
    │
    └─ Administrateur?
        └─→ Voir "GUIDE_ADMIN.md"
            ├─ Dashboard admin
            ├─ Modération
            └─ Sécurité
```

---

## 🎯 Parcours recommandés

### Parcours: Je suis un nouveau développeur

```
1. Lisez README_COMPLET.md (vue générale)
2. Consultez DOCUMENTATION.md (section Architecture)
3. Suivez Installation (section 3-4)
4. Lancez Démarrage (section 5)
5. Explorez API Endpoints
6. Posez questions si besoin
```

### Parcours: Je suis un nouvel utilisateur

```
1. Accédez à http://localhost:5173 (ou l'URL du site)
2. Cliquez "S'inscrire"
3. Remplissez formulaire
4. Lisez GUIDE_UTILISATEUR.md (navigation)
5. Explorez l'application
6. Contactez support si problème
```

### Parcours: Je suis un nouvel administrateur

```
1. Authentifiez-vous (admin@betalab.fr / admin123)
2. ⚠️ CHANGEZ le mot de passe immédiatement
3. Lisez GUIDE_ADMIN.md (section Accès admin)
4. Suivez Tableau de bord admin
5. Validez utilisateurs en attente
6. Approuvez contenu
7. Consultez FAQ admin
```

---

## 🔍 Chercher une réponse rapide?

### Utilisateur - Questions courantes

| Question | Réponse |
|---|---|
| Comment m'inscrire? | [GUIDE_UTILISATEUR > S'inscrire](./GUIDE_UTILISATEUR.md#-sinscrire) |
| Je ne peux pas me connecter | [GUIDE_UTILISATEUR > FAQ](./GUIDE_UTILISATEUR.md#-aide--faq) |
| Comment créer une activité? | [GUIDE_UTILISATEUR > Activités](./GUIDE_UTILISATEUR.md#-activités) |
| Où poser mes questions? | [GUIDE_UTILISATEUR > Q&A](./GUIDE_UTILISATEUR.md#-questions--réponses) |
| Comment puis-je vous contacter? | [GUIDE_UTILISATEUR > Contact](./GUIDE_UTILISATEUR.md#-contacter-léquipe) |

### Admin - Questions courantes

| Question | Réponse |
|---|---|
| Comment valider un utilisateur? | [GUIDE_ADMIN > Gestion utilisateurs](./GUIDE_ADMIN.md#-gestion-des-utilisateurs) |
| Comment approuver une activité? | [GUIDE_ADMIN > Gestion activités](./GUIDE_ADMIN.md#-gestion-des-activités) |
| Comment modérer une question? | [GUIDE_ADMIN > Modération](./GUIDE_ADMIN.md#-modération-du-contenu) |
| Quels rôles existent? | [GUIDE_ADMIN > Rôles](./GUIDE_ADMIN.md#-gestion-des-utilisateurs) |
| Comment créer un événement? | [GUIDE_ADMIN > Événements](./GUIDE_ADMIN.md#-gestion-des-événements) |

### Dev - Questions courantes

| Question | Réponse |
|---|---|
| Comment installer? | [DOCUMENTATION > Installation](./DOCUMENTATION.md#-installation) |
| Architecture du projet? | [DOCUMENTATION > Architecture](./DOCUMENTATION.md#-architecture) |
| Quels sont les endpoints? | [DOCUMENTATION > API Endpoints](./DOCUMENTATION.md#-api-endpoints) |
| Comment fonctionne l'auth? | [DOCUMENTATION > Authentification](./DOCUMENTATION.md#-authentification--rôles) |
| Erreur de connexion DB | [DOCUMENTATION > FAQ](./DOCUMENTATION.md#-faq--dépannage) |

---

## 🆘 Besoin d'aide?

### Parcours de support

```
Je ne trouve pas de réponse?
    ├─ Vérifier tous les guides
    ├─ Consulter FAQ du guide correspondant
    ├─ Chercher dans documentation officielle
    └─ Contacter admin@betalab.fr si toujours pas résolu
```

### Canaux de support

| Canal | Temps de réponse |
|---|---|
| 📧 Email: admin@betalab.fr | 24-48h |
| 📋 Formulaire Contact (dans app) | 24-48h |
| 📞 Téléphone (sur demande) | 2-3 jours |
| 💬 Chat support (si en ligne) | Temps réel |

---

## 📖 Guide de chaque section

### 📖 DOCUMENTATION.md

**Structure:**
1. Vue d'ensemble → Comprendre le projet
2. Architecture → Voir comment c'est organisé
3. Prérequis → Vérifier votre setup
4. Installation → Installer pas à pas
5. Configuration → Configurer la BD et l'env
6. Démarrage → Lancer l'application
7. Structure → Comprendre les dossiers
8. Fonctionnalités → Voir ce que fait l'app
9. API Endpoints → Tous les endpoints
10. Authentification → Systèmes de rôles
11. Flux de travail → Comment ça marche
12. FAQ & Troubleshooting → Résoudre problèmes

**Quand le lire:** Toujours en tant que développeur

---

### 👤 GUIDE_UTILISATEUR.md

**Structure:**
1. Accéder au site → Naviguer
2. S'inscrire → Créer un compte
3. Se connecter → Se logger in
4. Dashboard → Voir votre espace
5. Profil → Gérer vos données
6. Activités → Créer/participer
7. Événements → S'inscrire
8. Q&A → Poser questions
9. Suggestions → Donner feedback
10. Contact → Nous joindre
11. Sécurité → Protéger votre compte
12. FAQ → Réponses rapides

**Quand le lire:** Toujours en tant qu'utilisateur

---

### 🛡️ GUIDE_ADMIN.md

**Structure:**
1. Accès admin → Connexion
2. Tableau bord → Vue principale
3. Utilisateurs → Gérer users
4. Activités → Approuver contenu
5. Événements → Créer/gérer
6. Modération → Approuver Q&A
7. Approvals workflow → Comprendre flux
8. Statistiques → Voir rapports
9. Paramètres → Configurer système
10. Sécurité → Logs et protection
11. Dépannage → Résoudre problèmes admin
12. Checklists → Tâches quotidiennes

**Quand le lire:** Toujours en tant qu'admin

---

### 📖 README_COMPLET.md

**Sections principales:**
- Vue d'ensemble → Qu'est-ce que BetaLab?
- Démarrage rapide → 5 min pour commencer
- Documentation → Liens vers guides
- Architecture → Schéma visuel
- Stack technologique → Tech utilisée
- Commandes utiles → Code à copier
- Dépannage → Problèmes courants
- Déploiement → Options hosting
- Support → Comment obtenir aide
- Roadmap → Évolutions futures

**Quand le lire:** Première visite ou overview rapide

---

## 📊 Statistiques des documents

```
📖 DOCUMENTATION.md
   • Sections: 12
   • Contenu: 2000+ lignes
   • Copies: Code & configurations
   • Tables: 20+
   • Diagrammes: 5+
   • Audience: Développeurs 👨‍💻

👤 GUIDE_UTILISATEUR.md
   • Sections: 12
   • Contenu: 1500+ lignes
   • Screenshots: Décrits
   • Tables: 10+
   • FAQ: 15+ questions
   • Audience: Utilisateurs finaux 👥

🛡️ GUIDE_ADMIN.md
   • Sections: 11
   • Contenu: 1800+ lignes
   • Workflows: 4+ diagrammes
   • Checklists: 3 (quotidien/hebdo/mensuel)
   • FAQ: 10+ questions
   • Audience: Administrateurs 🛡️

📖 README_COMPLET.md
   • Sections: 20
   • Contenu: 800+ lignes
   • Badges: 4
   • Commandes: 30+
   • Ressources: 10+
   • Audience: Tous 🌐
```

---

## 📝 Notes importantes

### ⚠️ Sécurité

- **Ne JAMAIS committer** le fichier `.env`
- **Changer mot de passe admin** immédiatement après installation
- **Utiliser HTTPS** en production
- **Backup régulière** de la base de données

### 📌 Avant de déployer

- Lisez "DOCUMENTATION.md" section "Déploiement"
- Consultez "GUIDE_ADMIN.md" pour sécurité système
- Configurez monitoring et backaups
- Testez sur environnement de staging

### 🔔 Maintenant à jour avec

- **Version:** 2.0.0
- **Date:** Mars 2026
- **Python:** 3.10+
- **Node.js:** 18+
- **MySQL:** 8.0+
- **React:** 19.2.4
- **FastAPI:** 0.110.0

---

## 🚀 Plan d'action par profil

### Développeur: Jour 1

```
✅ Lire README_COMPLET.md (15 min)
✅ Lire Architecture dans DOCUMENTATION.md (15 min)
✅ Cloner et setup initial (10 min)
✅ Configurer la BD (10 min)
✅ Lancer backend et frontend (10 min)
✅ Tester sur browser (5 min)
→ Total: ~1 heure
```

### Utilisateur: Jour 1

```
✅ Naviguer sur le site (5 min)
✅ S'inscrire (5 min)
✅ Lire section "Navigation" du GUIDE (10 min)
✅ Compléter profil (5 min)
✅ Explorer features (15 min)
→ Total: ~40 minutes
```

### Admin: Jour 1

```
✅ Se logger (admin/admin123)
✅ Changer mot de passe
✅ Lire section "Accès Admin" du GUIDE (10 min)
✅ Consulter Dashboard Admin (10 min)
✅ Valider premiers utilisateurs (15 min)
✅ Explorer modération (15 min)
→ Total: ~1 heure
```

---

## 🎓 Ressources externes

### Frameworks utilisés

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [MySQL Manual](https://dev.mysql.com/doc/)
- [Vite Guide](https://vitejs.dev/)

### Hébergement

- [Vercel](https://vercel.com) - Frontend
- [Railway](https://railway.app) - Backend + DB
- [PlanetScale](https://planetscale.com) - MySQL

### Outils

- [Postman](https://www.postman.com/) - Tester API
- [MySQL Workbench](https://www.mysql.com/products/workbench/) - Gérer DB
- [VS Code](https://code.visualstudio.com/) - Éditeur

---

## 📞 Contact support

**Besoin d'aide?**

1. Consulter le guide correspondant à votre profil (voir au-dessus)
2. Vérifier section FAQ du guide
3. Si toujours sans réponse:

📧 **Email:** admin@betalab.fr  
💬 **Formulaire contact:** Dans l'application  
📞 **Téléphone:** Sur demande via email  

---

## ✨ Bienvenue sur BetaLab!

Choisissez votre rôle ci-dessus et commencez! 👆

```
╔════════════════════════════════════════════╗
║         🎉 BIENVENUE SUR BETALAB! 🎉     ║
║                                           ║
║  Sélectionnez votre rôle:                ║
║  • 👨‍💻 Développeur → DOCUMENTATION.md      ║
║  • 👥 Utilisateur → GUIDE_UTILISATEUR.md ║
║  • 🛡️ Administrateur → GUIDE_ADMIN.md    ║
║  • 🌐 Vue générale → README_COMPLET.md  ║
║                                           ║
║  Questions? → Voir FAQ dans votre guide  ║
║                                           ║
║           Bon développement! 🚀          ║
╚════════════════════════════════════════════╝
```

---

**V2.0.0** • **Mars 2026** • **Production Ready** ✅  
*Dernière mise à jour: 2026-03-25*

---

**[⬆ Retour au haut](#-index-de-documentation---betalab)** | **[Vers README](./README_COMPLET.md)**
