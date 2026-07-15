"""Admin authentication for the SQLAdmin dashboard (ARCHITECTURE.md §12).

Single-admin login backed by env-var credentials. This gate is separate from the
app's user JWT auth. Set a strong `ADMIN_PASSWORD` and `ADMIN_SESSION_SECRET` in
production; consider also restricting `/admin` at the edge (Cloudflare) by IP.
"""

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.config import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if username == settings.admin_username and password == settings.admin_password:
            request.session.update({"admin": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin"))
