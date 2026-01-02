from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- Request Models ---
class GeneratePuzzleRequest(BaseModel):
    fen: str
    move_uci: str # The bad move the user played (context)
    motif: Optional[str] = None # The tactical motif from LLM analysis
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
    fitness: Optional[float] = None # Puzzle clarity score from genetic algorithm
    best_move: Optional[str] = None # Best move in UCI format
    is_parent: Optional[bool] = False # True if this is the original position
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "123e4567-e89b-12d3-a456-426614174000",
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "solution": ["e2e4"],
                "theme": "Fork",
                "generator_type": "evolutionary",
                "difficulty_level": 1,
                "fitness": 2.5,
                "best_move": "e2e4",
                "is_parent": True
            }
        }

class UserTrainingHistory(BaseModel):
    user_id: str
    puzzle_id: str
    is_correct: bool
    time_taken_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)