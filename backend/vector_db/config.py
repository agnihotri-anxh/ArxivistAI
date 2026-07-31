from pathlib import Path
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
JSON_DIR = DATA_DIR / "structured_json"
METADATA_PATH = DATA_DIR / "metadata.json"
MILVUS_URI = os.getenv("MILVUS_URI", "./milvus_demo.db")
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN", "")  # Zilliz API Key

COLLECTION_NAME = "research_papers"
MODEL_NAME = "BAAI/bge-m3"
