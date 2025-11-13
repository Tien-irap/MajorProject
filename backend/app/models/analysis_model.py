# --- Pydantic Models (for request/response validation) ---
from http.client import HTTPException
from fastapi import status
from pydantic import BaseModel
from bson import ObjectId


class AnalysisCreateResponse(BaseModel):
    analysis_id: str
    status: str
    message: str

class AnalysisStatusResponse(BaseModel):
    status: str
    error: str | None = None

# --- Helper for validating MongoDB ObjectId ---
def validate_object_id(id_: str) -> ObjectId:
    try:
        return ObjectId(id_)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid analysis_id format"
        )