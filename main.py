"""
Point d'entrée BetaLab — FastAPI v2.0
Nouvelle architecture:
  - Endpoints organisés: admin/, user/, shared/
  - Sessions persistantes en BD
  - Authentification admin en BD
  - CSRF protection
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

from database import engine, Base, SessionLocal
import models

app = FastAPI(
    title="Application Gestion Labo",
    description="API de gestion du laboratoire BetaLab v2.0",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:30000", "http://localhost:30000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-CSRF-Token"],
)

# Créer les tables
Base.metadata.create_all(bind=engine)

# Initialiser les données par défaut
@app.on_event("startup")
def startup_event():
    """Événement au démarrage."""
    db = SessionLocal()
    try:
        print("\n" + "="*70)
        print("🚀 Démarrage BetaLab v2.0 — Architecture Modulaire")
        print("="*70)
        
        # 1. Vérifier/créer admin par défaut
        admin = db.query(models.AdminUser).filter(
            models.AdminUser.username == "admin"
        ).first()
        
        if not admin:
            from dependencies import get_password_hash
            admin = models.AdminUser(
                username="admin",
                email="admin@betalab.fr",
                password=get_password_hash("admin123"),
                role="super_admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("✅ Admin par défaut créé (username: admin, password: admin123)")
        else:
            print("ℹ️  Admin par défaut existe déjà")
        
        # 2. Nettoyer les sessions expirées
        now = datetime.utcnow()
        expired_sessions = db.query(models.Session).filter(
            models.Session.expires_at < now
        ).delete()
        if expired_sessions > 0:
            print(f"🧹 {expired_sessions} sessions expirées nettoyées")
        
        # 3. Nettoyer les CSRF tokens expirés
        expired_csrf = db.query(models.CSRFToken).filter(
            models.CSRFToken.expires_at < now
        ).delete()
        if expired_csrf > 0:
            print(f"🧹 {expired_csrf} tokens CSRF expirés nettoyés")
        
        # 4. Nettoyer les tokens d'invitation expirés
        expired_invitations = db.query(models.InvitationToken).filter(
            models.InvitationToken.expires_at < now,
            models.InvitationToken.used == False
        ).delete()
        if expired_invitations > 0:
            print(f"🧹 {expired_invitations} invitations expirées nettoyées")
        
        db.commit()
        
        print("\n✅ Initialisation complétée avec succès")
        print("📊 Endpoints organisés en 3 catégories:")
        print("   📁 endpoints/admin/     - Gestion admin")
        print("   👤 endpoints/user/      - Profil et contributions utilisateur")
        print("   🤝 endpoints/shared/    - Contact, questions, suggestions")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Erreur au démarrage: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclure tous les routers
print("📦 Chargement des endpoints...")

# Endpoints Compatibilité (Frontend ⟷ Backend mapping) - EN PREMIER
from endpoints.compatibility import router as compat_router
app.include_router(compat_router)
print(f"   ✅ Compatibility Layer")

# Endpoints Admin
from endpoints.admin import get_admin_routers
admin_routers = get_admin_routers()
for router in admin_routers:
    app.include_router(router)
    print(f"   ✅ {router.tags[0] if router.tags else 'Admin'}")

# Endpoints Utilisateur
from endpoints.user import get_user_routers
user_routers = get_user_routers()
for router in user_routers:
    app.include_router(router)
    print(f"   ✅ {router.tags[0] if router.tags else 'User'}")

# Endpoints Partagés
from endpoints.shared import get_shared_routers
shared_routers = get_shared_routers()
for router in shared_routers:
    app.include_router(router)
    print(f"   ✅ {router.tags[0] if router.tags else 'Shared'}")

print("\n")

# Santé check
@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
