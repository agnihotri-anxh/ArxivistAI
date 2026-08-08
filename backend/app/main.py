from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .core.config import settings
from .api import routes, auth, admin

app = FastAPI(title=settings.API_TITLE)

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(routes.router, prefix="/api")

# Serve PDFs
pdfs_path = Path(__file__).resolve().parent.parent.parent / "data" / "pdfs"
app.mount("/api/pdfs", StaticFiles(directory=str(pdfs_path)), name="pdfs")

@app.get("/")
def root():
    return {"message": "Welcome to the AI Research Assistant API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}