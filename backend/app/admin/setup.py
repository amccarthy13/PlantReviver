from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import AdminAuth
from app.admin.views import ALL_VIEWS
from app.config import settings
from app.db import engine


def mount_admin(app: FastAPI) -> Admin:
    """Mount the SQLAdmin dashboard at /admin on the main app (ARCHITECTURE.md §12)."""
    admin = Admin(
        app,
        engine,
        authentication_backend=AdminAuth(secret_key=settings.admin_session_secret),
        title="PlantReviver Admin",
    )
    for view in ALL_VIEWS:
        admin.add_view(view)
    return admin
