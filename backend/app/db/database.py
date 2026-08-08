import pymongo
from ..core.config import settings

client = pymongo.MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB_NAME]

# Collections
users_collection = db["users"]
raw_arxiv_collection = db["raw_arxiv_metadata"]
papers_collection = db["papers"]

# Ensure Indexes
try:
    users_collection.create_index("username", unique=True)
    raw_arxiv_collection.create_index("paper_id", unique=True)
    papers_collection.create_index("paper_id", unique=True)
    papers_collection.create_index("category")
    papers_collection.create_index("year")
except Exception as e:
    print(f"[MongoDB] Index setup note: {e}")

def get_db():
    return db

def get_users_collection():
    return users_collection

def get_raw_arxiv_collection():
    return raw_arxiv_collection

def get_papers_collection():
    return papers_collection
