# db.py
import pymongo
from app.config import settings

def get_mongo_client():
    if not settings.MONGODB_URI:
        raise ValueError("MONGODB_URI is missing in environment (.env)")
    client = pymongo.MongoClient(settings.MONGODB_URI)
    return client
