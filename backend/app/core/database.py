from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from .config import settings

# --- 1. Async Client (For FastAPI) ---
class AsyncDatabase:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        """Call this on FastAPI startup"""
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        self.db = self.client[settings.DB_NAME]
        
        # --- ADD PRINT HERE ---
        print(f"✅ FastAPI: Connected to MongoDB (Async). DB Name: '{settings.DB_NAME}'") 

    def close(self):
        """Call this on FastAPI shutdown"""
        if self.client:
            self.client.close()
            print("❌ FastAPI: Disconnected from MongoDB")

# Create a global instance to import in main.py
db_async = AsyncDatabase()


# --- 2. Sync Client (For Celery Worker) ---
def get_sync_db_connection():
    """
    Creates a fresh synchronous connection. 
    Used exclusively by the Celery Worker.
    """
    try:
        client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client[settings.DB_NAME]
        
        # --- ADD PRINT HERE ---
        print(f"✅ Celery Worker: Connected to MongoDB (Sync). DB Name: '{settings.DB_NAME}'")

        # Test connection
        client.server_info()
        return db, client
    except Exception as e:
        print(f"🔥 ERROR: Could not connect to MongoDB (Sync): {e}")
        return None, None
