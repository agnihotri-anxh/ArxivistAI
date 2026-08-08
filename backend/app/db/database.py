import pymongo
from ..core.config import settings

client = pymongo.MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB_NAME]

# Collections
users_collection = db["users"]

# Ensure unique index on username
try:
    users_collection.create_index("username", unique=True)
except Exception as e:
    print(f"[MongoDB] Index setup note: {e}")

def get_db():
    return db

def get_users_collection():
    return users_collection
