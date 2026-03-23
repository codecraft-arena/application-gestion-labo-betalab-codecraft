"""
Routeur des pages HTML (templates Jinja2).
Endpoints :
  GET /           → accueil
  GET /signup     → formulaire d'inscription
  GET /login      → page de connexion
  GET /admin      → page de connexion admin
  GET /design     → page design
  GET /activites  → page activités
  GET /stats      → page statistiques
  GET /dashuser   → tableau de bord utilisateur (protégé)
  GET /dashadmin  → tableau de bord admin
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import models
from dependencies import get_current_user

router = APIRouter(tags=["Pages HTML"])

templates = Jinja2Templates(directory="frontend")


@router.get("/", response_class=HTMLResponse)
async def accueil(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin-login.html", {"request": request})


@router.get("/design", response_class=HTMLResponse)
async def design(request: Request):
    return templates.TemplateResponse("design.html", {"request": request})


@router.get("/activites", response_class=HTMLResponse)
async def activites(request: Request):
    return templates.TemplateResponse("activites.html", {"request": request})


@router.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request})


@router.get("/dashuser", response_class=HTMLResponse)
async def dashuser(
    request: Request,
    current_user: models.User = Depends(get_current_user),
):
    """Page protégée — accessible uniquement si l'utilisateur est connecté."""
    return templates.TemplateResponse("dashuser.html", {"request": request})


@router.get("/dashadmin", response_class=HTMLResponse)
async def dashadmin(request: Request):
    return templates.TemplateResponse("dashadmin.html", {"request": request})
