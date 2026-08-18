import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routes import analytics, auth, chat, documents, search
from app.core.config import settings
from app.db.init_db import ensure_admin, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database and create admin user on startup
    init_db()
    ensure_admin()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(analytics.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def serve_dashboard():
    """
    Serves the main frontend dashboard when visiting http://localhost:8000
    Inside Docker, __file__ is /app/app/main.py, so '..' goes to /app/
    """
    file_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dashboard.html")
    return FileResponse(file_path)