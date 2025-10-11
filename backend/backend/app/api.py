# backend/app/api.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import traceback

router = APIRouter()

# Import your analysis function
try:
    from .services import analyze_game_with_stockfish
    print("✓ Successfully imported analyze_game_with_stockfish")
except ImportError as e:
    print(f"✗ Error importing analysis function: {e}")
    traceback.print_exc()
    analyze_game_with_stockfish = None

class MoveAnalysis(BaseModel):
    move_number: int
    move: str
    move_san: Optional[str] = None
    evaluation_before: Optional[float] = None
    evaluation_after: Optional[float] = None
    centipawn_loss: Optional[float] = None
    best_move: Optional[str] = None
    classification: Optional[str] = None
    classification_wp: Optional[str] = None
    win_prob_before: Optional[float] = None
    win_prob_after: Optional[float] = None
    win_prob_drop: Optional[float] = None
    comment: Optional[str] = None
    is_white: Optional[bool] = None

class BestWorstMove(BaseModel):
    move_number: int
    move: str
    centipawn_loss: float
    evaluation_before: Optional[float] = None
    evaluation_after: Optional[float] = None
    player: str
    description: Optional[str] = None
    classification: Optional[str] = None
    win_prob_drop: Optional[float] = None

class AnalysisResponse(BaseModel):
    game_summary: str
    white_player: Optional[str] = None
    black_player: Optional[str] = None
    result: Optional[str] = None
    total_moves: int
    moves: List[MoveAnalysis]
    top_10_best_moves: List[BestWorstMove]
    top_10_worst_moves: List[BestWorstMove]
    average_centipawn_loss_white: Optional[float] = None
    average_centipawn_loss_black: Optional[float] = None
    pgn_content: Optional[str] = None

@router.post("/analyze-pgn", response_model=AnalysisResponse)
async def analyze_pgn_endpoint(pgn_file: UploadFile = File(...)):
    """
    Endpoint to analyze a PGN file with Stockfish and get AI coach feedback
    """
    if not pgn_file.filename.endswith('.pgn'):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload a .pgn file."
        )

    try:
        # Read file content
        content = await pgn_file.read()
        pgn_content_string = content.decode("utf-8")

        if analyze_game_with_stockfish is None:
            raise HTTPException(
                status_code=500,
                detail="Analysis function not available. Check services.py configuration."
            )

        # Call Stockfish analysis with LLM summaries
        print("=" * 60)
        print("🔍 Starting comprehensive game analysis...")
        print("=" * 60)
        analysis_result = analyze_game_with_stockfish(pgn_content_string)
        print("=" * 60)
        print("✅ Analysis complete!")
        print("=" * 60)

        return analysis_result
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in analysis: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Error analyzing PGN: {str(e)}"
        )

@router.get("/api/test")
async def test_endpoint():
    return {"message": "API router is working!", "status": "ok"}

@router.get("/api/stockfish-status")
async def stockfish_status():
    """Check if Stockfish and API are properly configured"""
    try:
        from pathlib import Path
        import os
        
        BACKEND_DIR = Path(__file__).parent.parent
        stockfish_path = BACKEND_DIR / "stockfish" / "stockfish.exe"
        
        # Check Mistral API key
        from dotenv import load_dotenv
        load_dotenv(BACKEND_DIR / ".env")
        mistral_key = os.getenv("MISTRAL_API_KEY")
        
        return {
            "stockfish_available": stockfish_path.exists(),
            "stockfish_path": str(stockfish_path),
            "mistral_api_configured": mistral_key is not None and len(mistral_key) > 0,
            "analysis_function_loaded": analyze_game_with_stockfish is not None
        }
    except Exception as e:
        return {
            "error": str(e),
            "stockfish_available": False
        }