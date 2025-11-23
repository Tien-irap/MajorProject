from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- Request Models ---
class GeneratePuzzleRequest(BaseModel):
    fen: str
    move_uci: str # The bad move the user played (context)
    difficulty_level: int = 1 # For future RL integration

class SubmitPuzzleResultRequest(BaseModel):
    puzzle_id: str # We will generate a UUID for each puzzle
    user_id: str
    is_correct: bool
    time_taken_seconds: float

# --- DB/Response Models ---
class PuzzleDB(BaseModel):
    id: str = Field(..., alias="_id")
    fen: str
    solution: List[str]
    theme: str
    generator_type: str # 'seed' or 'evolutionary'
    difficulty_level: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class UserTrainingHistory(BaseModel):
    user_id: str
    puzzle_id: str
    is_correct: bool
    time_taken_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)