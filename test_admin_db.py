#!/usr/bin/env python3
"""Script pour tester les identifiants admin en base de données"""

import sys
sys.path.insert(0, '/home/codecraft-arena/Pictures/application-gestion-labo-betalab-codecraft')

from database import SessionLocal
from models import AdminUser
from admin_auth import AdminAuthManager
from dependencies import get_password_hash, verify_password

db = SessionLocal()

try:
    print("\n" + "="*60)
    print("TEST AUTHENTIFICATION ADMIN")
    print("="*60)
    
    # Vérifier si l'admin existe
    admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
    
    if not admin:
        print("❌ Admin 'admin' n'existe pas en base de données")
        print("\n→ Création de l'admin par défaut...")
        admin = AdminAuthManager.create_admin_user(
            db=db,
            username="admin",
            password="admin123",
            email="admin@betalab.fr",
            role="super_admin"
        )
        print(f"✅ Admin créé: {admin.username}")
    else:
        print(f"✅ Admin trouvé: {admin.username}")
        print(f"   - Email: {admin.email}")
        print(f"   - Actif: {admin.is_active}")
        print(f"   - Rôle: {admin.role}")
        print(f"   - Hash password (30 premiers chars): {admin.password[:30]}...")
    
    # Tester la vérification de mot de passe
    print("\n" + "-"*60)
    print("TEST VÉRIFICATION DE MOT DE PASSE")
    print("-"*60)
    
    result = AdminAuthManager.verify_admin(db, "admin", "admin123")
    if result:
        print(f"✅ Mot de passe 'admin123' CORRECT pour l'utilisateur 'admin'")
    else:
        print(f"❌ Mot de passe 'admin123' INCORRECT pour l'utilisateur 'admin'")
        
        # Essayer de vérifier manuellement
        print("\n   Vérification manuelle du hash:")
        is_valid = verify_password("admin123", admin.password)
        print(f"   verify_password() retourne: {is_valid}")
    
    # Lister tous les admins
    print("\n" + "-"*60)
    print("LISTE DE TOUS LES ADMINS")
    print("-"*60)
    all_admins = db.query(AdminUser).all()
    for a in all_admins:
        print(f"  - {a.username} ({a.email}) - Actif: {a.is_active}")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
    print("\n" + "="*60 + "\n")
