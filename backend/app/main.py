from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import routes

app = FastAPI(title=settings.API_TITLE)

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the AI Research Assistant API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}