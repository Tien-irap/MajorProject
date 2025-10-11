# backend/app/models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class MoveAnalysis(BaseModel):
    move_number: int
    move: str
    evaluation: Optional[float] = None
    classification: Optional[str] = None
    comment: Optional[str] = None

class GameAnalysis(BaseModel):
    white_player: Optional[str] = None
    black_player: Optional[str] = None
    result: Optional[str] = None
    moves: List[MoveAnalysis]