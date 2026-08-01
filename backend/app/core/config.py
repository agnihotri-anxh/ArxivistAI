import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Point explicitly to the root .env file
ENV_PATH = Path(__file__).resolve().parent.parent.parent.parent / ".env"

class Settings(BaseSettings):
    API_TITLE: str = "AI Research Assistant API"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MILVUS_URI: str = os.getenv("MILVUS_URI", "./data/milvus_demo.db")
    MILVUS_TOKEN: str = os.getenv("MILVUS_TOKEN", "")
    
    model_config = SettingsConfigDict(env_file=str(ENV_PATH), extra="ignore")

settings = Settings()
