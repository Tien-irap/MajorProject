# repos/analysis_repository.py

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.collection import Collection as PyMongoCollection
from typing import Dict, Any
from backend.app.core.logger import logger

# --- Helper ---
def _validate_object_id(job_id: str) -> ObjectId:
    try:
        return ObjectId(job_id)
    except Exception:
        raise ValueError(f"Invalid ObjectId: {job_id}")

# ==========================================================
# ASYNC Functions (for FastAPI / main.py)
# ==========================================================

async def create_job_async(collection: AsyncIOMotorCollection, pgn_hash: str = None) -> str:
    """
    Creates a new analysis job document with 'PENDING' status.
    Returns the new job's ID as a string.
    
    Args:
        collection: MongoDB collection
        pgn_hash: SHA256 hash of PGN content for caching (optional)
    """
    new_job = {
        "status": "PENDING", 
        "result": None, 
        "error": None
    }
    
    if pgn_hash:
        new_job["pgn_hash"] = pgn_hash
    
    result = await collection.insert_one(new_job)
    return str(result.inserted_id)

async def get_job_by_id_async(collection: AsyncIOMotorCollection, job_id: str) -> Dict[str, Any] | None:
    """
    Fetches a complete job document by its ID.
    Returns the document or None if not found.
    """
    oid = _validate_object_id(job_id)
    return await collection.find_one({"_id": oid})

async def get_job_status_async(collection: AsyncIOMotorCollection, job_id: str) -> Dict[str, Any] | None:
    """
    Fetches only the status and error fields for a job.
    """
    oid = _validate_object_id(job_id)
    return await collection.find_one(
        {"_id": oid},
        projection={"status": 1, "error": 1}
    )

# ==========================================================
# SYNC Functions (for Celery / celery_worker.py)
# ==========================================================

def update_job_status_sync(collection: PyMongoCollection, job_id: str, status: str):
    """Updates the status of a job (e.g., to 'PROCESSING')."""
    oid = _validate_object_id(job_id)
    collection.update_one({"_id": oid}, {"$set": {"status": status}})

def set_job_completed_sync(
    collection: PyMongoCollection, 
    job_id: str, 
    result_data: Dict[str, Any], 
    duration: float
):
    """Sets the job to 'COMPLETED' and saves the full result."""
    oid = _validate_object_id(job_id)
    collection.update_one(
        {"_id": oid},
        {"$set": {
            "status": "COMPLETED",
            "result": result_data,
            "analysis_duration_sec": duration
        }}
    )

def set_job_failed_sync(collection: PyMongoCollection, job_id: str, error_message: str):
    """Sets the job to 'FAILED' and saves the error message."""
    oid = _validate_object_id(job_id)
    collection.update_one(
        {"_id": oid},
        {"$set": {"status": "FAILED", "error": error_message}}
    )