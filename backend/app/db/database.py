import pymongo
from ..core.config import settings

client = pymongo.MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB_NAME]

# Collections
users_collection = db["users"]
raw_arxiv_collection = db["raw_arxiv_metadata"]
papers_collection = db["papers"]
chats_collection = db["chats"]
notifications_collection = db["notifications"]

# Ensure Indexes
try:
    users_collection.create_index("username", unique=True)
    raw_arxiv_collection.create_index("paper_id", unique=True)
    papers_collection.create_index("paper_id", unique=True)
    papers_collection.create_index("category")
    papers_collection.create_index("year")
    chats_collection.create_index("chat_id", unique=True)
    chats_collection.create_index("user_id")
    notifications_collection.create_index("notification_id", unique=True)
    notifications_collection.create_index("created_at")
    
    # Weighted Text Index for Ranked Search & Autocomplete
    papers_collection.create_index(
        [
            ("title", pymongo.TEXT),
            ("authors", pymongo.TEXT),
            ("full_abstract", pymongo.TEXT)
        ],
        weights={"title": 10, "authors": 5, "full_abstract": 1},
        name="papers_weighted_text_index"
    )
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

def get_chats_collection():
    return chats_collection

def get_notifications_collection():
    return notifications_collection
