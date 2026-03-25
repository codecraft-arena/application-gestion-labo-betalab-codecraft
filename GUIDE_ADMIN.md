# 🛡️ Guide Administrateur - BetaLab

> **Guide complet pour les administrateurs**  
> *Comment gérer BetaLab et modérer le contenu*

---

## 📋 Table des matières

1. [Accès admin](#-accès-admin)
2. [Tableau de bord admin](#-tableau-de-bord-admin)
3. [Gestion des utilisateurs](#-gestion-des-utilisateurs)
4. [Gestion des activités](#-gestion-des-activités)
5. [Gestion des événements](#-gestion-des-événements)
6. [Modération du contenu](#-modération-du-contenu)
7. [Approvals workflow](#-approvals-workflow)
8. [Statistiques & Rapports](#-statistiques--rapports)
9. [Paramètres système](#-paramètres-système)
10. [Sécurité & Logs](#-sécurité--logs)
11. [Dépannage admin](#-dépannage-admin)

---

## 🔐 Accès admin

### Connexion administrateur

1. Allez sur la page de **Connexion** → Sélectionnez **"Connexion Admin"**
2. Entrez:
   - **Email:** admin@betalab.fr (par défaut)
   - **Mot de passe:** admin123 (par défaut - **CHANGER IMMÉDIATEMENT**)

### ⚠️ Première connexion - Critique

**VOUS DEVEZ:**

1. **Changer le mot de passe admin immédiatement**
   ```
   Compte → Paramètres → Changer Mot de passe
   
   Ancien: admin123
   Nouveau: Mot de passe fort (16+ caractères, majuscules, minuscules, chiffres, symboles)
   ```

2. **Vérifier la sécurité du serveur**
   - Utiliser HTTPS en production
   - Configurer firewall
   - Utiliser variables d'environnement pour sensibles
   - Activer backups automatiques

3. **Configurer notifications email**
   - Vérifier SMTP_HOST, SMTP_USER, SMTP_PASSWORD dans `.env`
   - Tester en envoyant email test

4. **Créer autres administrateurs** (optionnel)
   - Menu Admins → Créer nouvel admin
   - Donner accès à des départements spécifiques

---

## 📊 Tableau de bord admin

### Accès

Menu → **"Dashboard Admin"** ou **"Administration"**

### Vue d'ensemble

```
╔═══════════════════════════════════════════╗
║          TABLEAU DE BORD ADMIN           ║
╠═══════════════════════════════════════════╣
║                                          ║
║  📊 STATISTIQUES EN TEMPS RÉEL           ║
║  ├─ Utilisateurs actifs: 145             ║
║  ├─ Activités approuvées: 34             ║
║  ├─ Questions en modération: 7           ║
║  └─ Incidents signalés: 2                ║
║                                          ║
║  ⚠️ URGENTS (Derniers 24h)               ║
║  ├─ 12 nouveaux utilisateurs à valider  ║
║  ├─ 5 activités en attente d'approvaluation ║
║  └─ 3 suggestions à modérer             ║
║                                          ║
║  📋 ACTIONS RAPIDES                      ║
║  ├─ Valider utilisateurs                 ║
║  ├─ Approuver contenu                    ║
║  ├─ Créer événement                      ║
║  └─ Voir tous les rapports               ║
║                                          ║
╚═══════════════════════════════════════════╝
```

---

## 👥 Gestion des utilisateurs

### Voir tous les utilisateurs

Menu → **"Gestion Utilisateurs"**

Vous voyez:
- Liste de tous les utilisateurs
- Statut (Validé, En attente, Suspendu)
- Rôle (Membre, Chercheur, Responsable)
- Date d'inscription
- Dernière activité

### Filtrer les utilisateurs

- **Par statut:** Tous, Validés, En attente, Suspendus
- **Par rôle:** Membre, Chercheur, Responsable, Admin
- **Par date:** Récents, Anciens
- **Recherche:** Tapez nom/email

### Valider un nouvel utilisateur

1. Trouvez l'utilisateur avec status **"En attente"**
2. Cliquez sur son email/nom
3. Vérifiez les informations:
   - Email valide
   - Nom et prénom corrects
   - Domaine pertinent
   - Pas de redflags
4. Cliquez **"Valider"**
5. L'utilisateur reçoit email de confirmation

### Rejeter un utilisateur

1. Trouvez l'utilisateur
2. Cliquez sur **"Plus d'options"** → **"Rejeter"**
3. Entrez une raison (optionnel):
   ```
   Exemples:
   - Email invalide
   - Information douteuse
   - Contenu offensif
   - Doublon de compte
   ```
4. Cliquez **"Rejeter"**
5. L'utilisateur est supprimé

### Modifier le rôle d'un utilisateur

```
Utilisateur → Cliquez → "Modifier rôle"

Rôles disponibles:
  👤 Membre (défaut)
     - Consulter activités
     - Poser questions
     - Faire suggestions
     
  🔬 Chercheur
     - Tous droits du Membre +
     - Créer/modifier activités *
     
  👔 Responsable
     - Tous droits du Chercheur +
     - Modérer questions/suggestions
     
  🛡️ Admin
     - Tous les droits
     - Accès panel admin (vous)
```

### Suspendre un utilisateur

**Raisons:**
- Violation du code de conduite
- Spam ou contenu offensif
- Activité suspecte
- Paiement impayé (si applicable)

**Comment:**
1. Utilisateur → **"Suspendre"**
2. Raison: Sélectionnez une raison
3. Durée: Temporaire (7j) ou Permanente
4. Notes (optionnel)
5. L'utilisateur ne peut plus se connecter

### Réactiver un utilisateur suspendu

1. Cliquez sur utilisateur suspendu
2. **"Réactiver"**
3. Optionnel: Modifier raison/durée
4. L'utilisateur peut se reconnecter

### Supprimer un utilisateur

⚠️ **ATTENTION:** Action irréversible!

1. Utilisateur → **"Plus"** → **"Supprimer"**
2. Confirmez deux fois
3. Toutes les données sont supprimées

---

## 🎯 Gestion des activités

### Voir les activités

Menu → **"Gestion Activités"**

Affichage:
- Activités en attente d'approbation
- Activités approuvées
- Activités rejetées
- Activités terminées

### Approuver une activité

1. Trouvez l'activité avec status **"En attente"**
2. Cliquez pour lire:
   - Titre et description
   - Auteur et date de création
   - Domaine/catégorie
   - Raison (si applicable)

3. Vérifiez:
   ✅ Titre clair
   ✅ Description suffisante
   ✅ Domaine approprié
   ✅ Pas de contenu interdit
   ✅ Pas de spam

4. Décision:
   - **"APPROUVER"** → Visible au public
   - **"REJETER"** → Retour à l'auteur avec raison
   - **"DEMANDER MODIFICATION"** → Auteur doit corriger

### Rejeter une activité

1. Activité → **"REJETER"**
2. Raison (obligatoire):
   ```
   Exemples:
   - Description insuffisante
   - Contenu non pertinent
   - Format incorrect
   - Informations douteuses
   - Autre (à spécifier)
   ```
3. Notes (optionnel): Conseils pour améliorer
4. L'auteur reçoit notification

### Modifier une activité (en dernier recours)

1. Si erreur mineure, cliquez **"Éditer"**
2. Corrigez le problème
3. Sauvegardez
4. (Idéalement: demander à l'auteur de corriger)

### Supprimer une activité

Raisons:
- Contenu offensif
- Spam
- Doublon
- Erreur administrative

Comment:
1. Activité → **"Plus"** → **"Supprimer"**
2. Confirmez
3. Notifiez l'auteur (optionnel)

---

## 🎪 Gestion des événements

### Créer un événement

Menu → **"Créer Événement"**

Formulaire:
- **Titre:** Nom de l'événement
- **Description:** Détails du contenu
- **Type:** Conférence, Atelier, Hackathon, etc.
- **Date:** JJ/MM/AAAA
- **Heure:** HH:MM (début et fin)
- **Lieu:** Adresse physique ou "En ligne"
- **Max participants:** Nombre limite (0 = illimité)
- **Image:** Logo/affiche de l'événement

Cliquez **"Créer"** → Événement publié immédiatement

### Voir les événements

Menu → **"Gestion Événements"**

Affichage:
- Tous les événements
- Filtrer par type, date, statut
- Nombre de participants
- Listes d'attente

### Approuver les inscriptions

1. Événement → **"Participants"**
2. Voyez les inscriptions:
   - ✅ Approuvées
   - ⏳ En attente
   - ❌ Refusées

3. En attente → Cliquez
   - **"APPROUVER"** → Confirmé, utilisateur notifié
   - **"REFUSER"** → Raison optionnelle
   - **"LISTE D'ATTENTE"** → Si full

### Envoyer notifications aux participants

1. Événement → **"Notifier participants"**
2. Type de message:
   - Rappel (date en approchant)
   - Changement (date/lieu modifié)
   - Annulation
   - Information supplémentaire
3. Écrivez le message
4. Sélectionnez destinataires:
   - Tous les approuvés
   - Seulement sans réponse
   - Personnalisé (email list)
5. **"ENVOYER"**

### Modifier un événement

1. Événement → **"Modifier"**
2. Changez les détails
3. **"Sauvegarder"**
4. Notifiez participants si changement important

### Annuler un événement

1. Événement → **"Annuler"**
2. Raison: Sélectionnez
3. Message aux participants (optionnel)
4. Tous les participants sont notifiés

### Archiver un événement

Après l'événement:
1. Événement → **"Archiver"**
2. Reste accessible dans historique
3. N'apparaît plus dans liste active

---

## 🎨 Modération du contenu

### Centre de modération

Menu → **"Modération"** ou **"Approvals"**

Voir:
- Questions en attente
- Suggestions en attente
- Commentaires à modérer
- Modifications de profil

### Modérer les questions

```
Liste des questions:
├─ ✅ Approuvées (visibles)
├─ ⏳ En attente (à traiter)
└─ ❌ Rejetées (auteur seulement)
```

**Pour chaque question en attente:**

1. Lisez le titre et la description
2. Vérifiez:
   - ✅ Pas d'insultes
   - ✅ Pas de spam
   - ✅ Pas de contenu interdit
   - ✅ Format acceptable
3. Décision:
   - **"APPROUVER"** → Visible, peut recevoir réponses
   - **"REJETER"** → Retour à l'auteur
   - **"RÉPONDRE"** → Admin répond directement

### Répondre à une question

1. Question → **"RÉPONDRE"**
2. Écrivez votre réponse (Markdown supporté)
3. Optionnel: Mentionner autres admins
4. **"SOUMETTRE RÉPONSE"**
5. Question devient approuvée automatiquement
6. Utilisateur notifié

### Modérer les suggestions

Processus identique aux questions:

1. Suggestion en attente
2. Vérifiez contenu
3. **"APPROUVER"** / **"REJETER"** / **"COMMENTER"**
4. Si rejet: Raison obligatoire
5. Utilisateur notifié

### Approuver les modifications de profil

1. **"Modifications en attente"**
2. Pour chaque modification:
   - Voir l'ancien et nouveau contenu
   - Crédibilité du changement
3. **"ACCEPTER"** → Profil mis à jour
4. **"REJETER"** → Ancien profil conservé

### Supprimer du contenu offensif

**Si contenu violant les règles:**

1. Contenu → **"Supprimer"** / **"Masquer"**
2. Raison (pour logs):
   - Insulte
   - Spam
   - Contenu interdit
   - Autre
3. Optionnel: Sanctionner l'utilisateur
   - Avertissement
   - Suspension
   - Suppression compte

---

## ⚙️ Approvals Workflow

### Comprendre les états

```
CRÉATION D'ACTIVITÉ (flux complet):

┌─ Utilisateur crée activité
│
├─ Soumise → Status = "pending_submission"
│  └─ Admin voit dans "Activités en attente"
│
├─ Admin approuve ✅ → Status = "approved"
│  └─ Devient public, visible à tous
│  └─ Utilisateur notifié
│
├─ Admin rejette ❌ → Status = "rejected"  
│  └─ Reste privé, visible seulement à créateur
│  └─ Utilisateur reçoit raison du rejet
│  └─ Utilisateur peut modifier et réenvoyer
│
└─ Utilisateur modifie (après création)
   └─ Nouvelle soumission
   └─ Retour à Admin approuve/rejette
```

### Tableau d'approbation

Menu → **"Approbations"**

Voir toutes les attentes:

| Élément | État | Auteur | Date | Action |
|---|---|---|---|---|
| Activité X | En attente | Jean | 2026-03-20 | Approuver/Rejeter |
| Question Y | En attente | Marie | 2026-03-21 | Approuver/Répondre |
| Profil mod. | En attente | Pierre | 2026-03-21 | Accepter/Rejeter |

### Filtrer/chercher

- Par type: Activités, Questions, Suggestions, Profils
- Par auteur: Tapez email/nom
- Par date: Aujourd'hui, Cette semaine, Ce mois
- Par statut: En attente, Approuvées, Rejetées

---

## 📊 Statistiques & Rapports

### Tableau de statistiques

Menu → **"Statistiques"** ou **"Rapports"**

Affichage:

```
UTILISATEURS
├─ Nombre total: 450
├─ Actifs (30 jours): 312
├─ Validés: 445
├─ Suspendus: 5
└─ Graphique: Inscription par semaine

ACTIVITÉS
├─ Total: 47
├─ Approuvées: 44
├─ En attente: 2
├─ Rejetées: 1
└─ Participation moyenne: 8.5 par activité

ENGAGEMENT
├─ Questions totales: 156
├─ Questions répondues: 142
├─ Suggestions: 89
├─ Notes moyennes suggestions: 7.2/10

ÉVÉNEMENTS
├─ Événements: 12
├─ Inscriptions totales: 340
├─ Approbation moyenne: 92%
└─ Taux de participation: 87%
```

### Exporter les données

1. Menu → **"Exporter"**
2. Sélectionnez:
   - Plage de dates
   - Type de données
   - Format (CSV, Excel, PDF)
3. **"TÉLÉCHARGER"**

### Générer rapports

1. **"Générer rapport"**
2. Sélectionnez période
3. Paramètres:
   - Statistiques clés
   - Graphiques
   - Analyses
4. **"GÉNÉRER"** → Télécharger PDF

---

## ⚙️ Paramètres système

### Accès

Menu → **"Paramètres"** ou **"Administration"** → **"Paramètres système"**

### Configuration générale

**Informations du site:**
- Nom du site: BetaLab
- URL: http://localhost:5173
- Tagline: "Laboratoire collaboratif"

**Email:**
- Email d'admin: admin@betalab.fr
- Email de notification: noreply@betalab.fr
- Notifications actives: ✅

**Langue & Localisation:**
- Langue par défaut: Français
- Fuseau horaire: Europe/Paris
- Formats de date: JJ/MM/AAAA

### Paramètres de sécurité

**Authentification:**
- Duration session: 24 heures
- Max sessions par utilisateur: 3
- Expiration mot de passe: 90 jours

**Rate Limiting:**
- Tentatives login: 5 par 10 min
- API requests: 1000 par heure
- Uploads: 10MB par fichier

**Cookies:**
- HttpOnly: ✅ Activé
- Secure: ✅ Activé (HTTPS)
- SameSite: Strict

### Paramètres de contenu

**Modération:**
- Modération auto questions: ❌ Désactivée
- Modération auto suggestions: ❌ Désactivée
- Approvals requises: ✅ Activées

**Limites:**
- Activités par utilisateur: Illimité
- Questions par jour: 5
- Suggestions par semaine: 2

**Mots-clés interdits:**
- Ajouter/Modifier liste noire
- Les messages contenant ces mots seront rejetés

### Paramètres SMTP (Email)

> ⚠️ Critique pour notifications

```
SMTP Host: smtp.gmail.com
SMTP Port: 587
SMTP User: your-email@gmail.com
SMTP Password: [app-password]
From Address: noreply@betalab.fr

Test Connection: [TESTER]  ← Cliquez pour tester
```

### Sauvegardes

**Sauvegardes automatiques:**
- Activées: ✅
- Fréquence: Quotidienne (01:00)
- Rétention: 30 derniers jours
- Emplacement: Base de données

**Sauvegardes manuelles:**
- **"Sauvegarder maintenant"**
- Télécharger fichier SQL

---

## 🔐 Sécurité & Logs

### Logs d'activité

Menu → **"Logs"** ou **"Sécurité"** → **"Logs d'activité"**

Voir:
- Toutes les actions admin
- Toutes les connexions utilisateur
- Tentatives de hack
- Changements de configuration

### Filtrer les logs

```
Par type d'action:
├─ Connexion/Déconnexion
├─ Création de contenu
├─ Modification
├─ Suppression
├─ Approbation
└─ Les erreurs

Par utilisateur/Email

Par date/heure

Par erreur:
├─ Info
├─ Avertissement
├─ Erreur
└─ Critique
```

### Logs de sécurité

Voir les incidents:
- Tentatives de connexion échouées
- IP suspectes
- Accès dénié
- Modifications de configuration
- Suppressions importantes

### Auditer les actions admin

1. Votre email → Voir actions
2. Noms des admins et leur historique
3. Toutes les modifications tracées
4. Timestamps précis
5. IP addresses

### Archiver les logs

Logs > 90 jours archivés automatiquement (stockage limité).

Pour audit long-terme:
1. **"Exporter logs"**
2. Sélectionnez plage de dates
3. **"TÉLÉCHARGER"** → Archive ZIP

---

## 🆘 Dépannage admin

### Problème: Utilisateur signale ne pas pouvvoir se connecter

1. Vérifiez si compte existe:
   - Menu Utilisateurs → Cherchez par email
2. Vérifiez statut:
   - Si "En attente": Validez le compte
   - Si "Suspendu": Réactivez
   - Si "Supprimé": Créer nouveau compte
3. Réinitialisez mot de passe (envoyez lien via email)
4. Testez en vous connectant comme l'utilisateur

### Problème: Email non reçu par utilisateur

1. Vérifiez configuration SMTP:
   - Allez Paramètres → Email
   - Test Connection
2. Si erreur: Corrigez identifiants
3. Vérifiez dossier Spam utilisateur
4. Renvoyez l'email

### Problème: Activité n'apparaît pas après approbation

1. Rafraîchissez la page (Ctrl/Cmd + F5)
2. Vérifiez statut de l'activité:
   - Doit être "approved"
3. Vérifiez au frontend:
   - Allez Menu → Activités
4. Si toujours pas: Contactez support technique

### Problème: Utilisateur dit avoir été suspendu par erreur

1. Vérifiez historique du compte:
   - Email → Voir détails
   - Regarder "Raison suspension"
2. Si erreur: Réactivez-le
3. Envoyez email d'excuses et réactivation
4. Documentez dans logs

### Problème: Performance lente

1. Vérifier charge serveur:
   - Statistiques → Performance
2. Vérifier nombre d'utilisateurs actifs
3. Si DB lente:
   - Exécuter analyse DB
   - Optimiser indexes
4. Augmenter ressources serveur si nécessaire

### Problème: Erreur 500 au backend

1. Vérifier logs du serveur:
   - Terminal backend
   - Fichiers logs
2. Rechercher l'erreur dans les logs
3. Chercher sur documentation
4. Redémarrer le serveur si nécessaire:
   ```bash
   # Arrêter
   Ctrl+C (dans terminal backend)
   
   # Relancer
   uvicorn main:app --reload
   ```

### Problème: Base de données corrompue

1. ⚠️ CRITICITE ÉLEVÉE
2. Restaurer sauvegarde:
   ```bash
   mysql -u betalab_user -p betalab_db < backup.sql
   ```
3. Vérifier intégrité:
   ```bash
   mysql> CHECK TABLE users;
   ```
4. Redémarrer application

---

## 📋 Checklist quotidienne admin

- [ ] Vérifier notifications et alertes
- [ ] Approuver utilisateurs en attente (24h max)
- [ ] Modérer contenu en attente
- [ ] Répondre aux questions non répondues
- [ ] Vérifier logs de sécurité
- [ ] Vérifier performance serveur
- [ ] Répondre mails support
- [ ] Mettre à jour calendrier événements si needed

## 📋 Checklist hebdomadaire admin

- [ ] Générer statistiques
- [ ] Revue des suspensions
- [ ] Vérifier backups DB
- [ ] Nettoyer contenu supprimé (archiver)
- [ ] Mettre à jour configurations si needed
- [ ] Vérifier dominions/certificat SSL
- [ ] Communiquer avec équipe

## 📋 Checklist mensuelle admin

- [ ] Rapport mensuel complet
- [ ] Analyse engagement utilisateurs
- [ ] Révision règles/code de conduite
- [ ] Planifier phasing/nouvelles features
- [ ] Audit de sécurité
- [ ] Mettre à jour documentation
- [ ] Réunion équipe (si applicable)

---

## 🚨 Escalade & Support

Si vous rencontrez un problème non documenté:

1. Vérifier la documentation complète
2. Chercher dans les logs
3. Tenter un redémarrage
4. Contacter l'équipe technique:
   - Email: tech-support@betalab.fr
   - Joindre: screenshots, logs, description détaillée
5. Escalader vers responsable système

---

## 📞 Contacts urgents

| Rôle | Email | Tel |
|---|---|---|
| Tech Support | tech@betalab.fr | +33 1 XX XX XX XX |
| Responsable Système | admin@betalab.fr | +33 1 XX XX XX XX |
| Équipe | team@betalab.fr | - |

---

**Merci de gérer BetaLab avec diligence et sécurité! 🛡️**

*Dernière mise à jour: Mars 2026*
