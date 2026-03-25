#!/usr/bin/env python3
"""Test de connexion admin"""

import sys
sys.path.insert(0, '/home/codecraft-arena/Pictures/application-gestion-labo-betalab-codecraft')

from database import SessionLocal
from models import AdminUser
from admin_auth import AdminAuthManager
from dependencies import verify_password
from fastapi import Form
import json

db = SessionLocal()

try:
    print("\n" + "="*60)
    print("TEST: SIMULATION DE CONNEXION ADMIN (Bug Fix Verification)")
    print("="*60)
    
    # Simulation de la requête POST /admin-login
    username = "admin"
    password = "admin123"
    
    # Étapes du code endpoints/compatibility.py ligne 104-155
    print(f"\n1️⃣  Recherche de l'admin '{username}'...")
    admin = db.query(AdminUser).filter(
        AdminUser.username == username
    ).first()
    
    if not admin:
        print("   ❌ Admin non trouvé")
        sys.exit(1)
    else:
        print(f"   ✅ Admin trouvé: {admin.username}")
    
    # Vérifier le mot de passe
    print(f"2️⃣  Vérification du mot de passe...")
    pwd_valid = verify_password(password, admin.password)
    
    if not pwd_valid:
        print(f"   ❌ Mot de passe incorrect")
        sys.exit(1)
    else:
        print(f"   ✅ Mot de passe correct")
    
    # Vérifier is_active (FIX: avant c'était admin.suspended)
    print(f"3️⃣  Vérification du statut du compte...")
    if not admin.is_active:
        print(f"   ❌ Compte désactivé (is_active = {admin.is_active})")
        sys.exit(1)
    else:
        print(f"   ✅ Compte actif (is_active = {admin.is_active})")
    
    print("\n" + "="*60)
    print("✅✅✅ SUCCÈS: Admin peut se connecter!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
