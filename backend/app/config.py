# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # We standardize on GOOGLE_API_KEY to match your .env file
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MONGODB_URI = os.getenv("MONGODB_URI")
    DB_NAME = os.getenv("DB_NAME", "policy_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "policy_chunks")

settings = Settings()