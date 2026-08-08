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
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb+srv://agnihotrianxh:agnihotrianxh@cluster0.lr2afmd.mongodb.net/?appName=Cluster0")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "arxivist_ai")
    
    model_config = SettingsConfigDict(env_file=str(ENV_PATH), extra="ignore")

settings = Settings()
