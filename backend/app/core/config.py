import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_TITLE: str = "AI Research Assistant API"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MILVUS_URI: str = os.getenv("MILVUS_URI", "./data/milvus_demo.db")
    MILVUS_TOKEN: str = os.getenv("MILVUS_TOKEN", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
