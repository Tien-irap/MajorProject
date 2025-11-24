from fastapi import APIRouter, HTTPException
from typing import List
import os
import uuid

# 1. Import Service (The Logic)
# Make sure this matches your file name: backend/app/services/genetic_puzzle_generator.py
from backend.app.services.GeneticAlgo import GeneticPuzzleGenerator

# 2. Import Repository (The Database Access)
# This replaces direct collection imports like 'puzzles_collection'
from backend.app.repos.GenPuzzle_repo import training_repo

# 3. Import Models (The Data Structures)
from backend.app.models.puzzle_models import (
    GeneratePuzzleRequest, 
    SubmitPuzzleResultRequest, 
    PuzzleDB, 
    UserTrainingHistory
)

# 4. Import Logger
from backend.app.core.logger import logger

router = APIRouter()

# --- CONFIG ---
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "./stockfish/stockfish-macos-m1-apple-silicon")

@router.post("/generate", response_model=List[PuzzleDB])
async def generate_training_puzzles(request: GeneratePuzzleRequest):
    """
    Endpoint: Generates a batch of puzzles from a single mistake FEN.
    
    Architecture Flow:
    1. Router receives Request.
    2. Router calls Service (GeneticPuzzleGenerator) to process logic.
    3. Router calls Repo (training_repo) to save to DB.
    4. Router returns response to Frontend.
    """
    # Validate Stockfish path
    if not os.path.exists(STOCKFISH_PATH):
        logger.error(f"Stockfish engine not found at {STOCKFISH_PATH}")
        raise HTTPException(
            status_code=500, 
            detail=f"Stockfish engine not found at {STOCKFISH_PATH}. Please check STOCKFISH_PATH environment variable."
        )
    
    logger.info(f"Generating puzzles for FEN: {request.fen[:50]}...")
    
    # 1. Initialize Logic Layer
    generator = GeneticPuzzleGenerator(STOCKFISH_PATH)
    
    try:
        # 2. Run the Evolution Loop (Service Layer)
        # This returns raw dictionary data
        raw_puzzles_data = generator.generate_puzzles(request.fen, num_variations=3)
        
        # Check if any puzzles were generated
        if not raw_puzzles_data or len(raw_puzzles_data) == 0:
            logger.warning("No puzzles generated - position may be too simple")
            raise HTTPException(
                status_code=400,
                detail="Could not generate puzzles from this position. The position may be too simple or already solved."
            )
        
        puzzle_objects = []
        
        # 3. Transform to DB Models
        for p_data in raw_puzzles_data:
            puzzle_id = str(uuid.uuid4())
            
            # Map the raw service data to our Pydantic DB model
            puzzle_obj = PuzzleDB(
                _id=puzzle_id,
                fen=p_data["fen"],
                solution=p_data["solution"],
                theme=p_data["theme"],
                generator_type=p_data["generator_type"],
                difficulty_level=request.difficulty_level
            )
            puzzle_objects.append(puzzle_obj)
        
        # 4. Save to MongoDB via Repository (Persistence Layer)
        if puzzle_objects:
            # We use the repository method we created earlier
            await training_repo.create_puzzles_bulk(puzzle_objects)
            logger.info(f"Successfully saved {len(puzzle_objects)} puzzles to database")
            
        return puzzle_objects

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Puzzle generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return a 500 error so the frontend knows something broke
        raise HTTPException(status_code=500, detail=f"Puzzle generation failed: {str(e)}")

@router.post("/submit")
async def submit_result(result: SubmitPuzzleResultRequest):
    """
    Endpoint: Records user performance.
    Data Usage: This data will be fed into the Q-Learning Agent later.
    """
    try:
        logger.info(f"Recording training result for user {result.user_id}, puzzle {result.puzzle_id}")
        
        # 1. Create the History Model
        history_entry = UserTrainingHistory(
            user_id=result.user_id,
            puzzle_id=result.puzzle_id,
            is_correct=result.is_correct,
            time_taken_seconds=result.time_taken_seconds
        )
        
        # 2. Save via Repository
        await training_repo.record_attempt(history_entry)
        
        logger.debug(f"Training result saved successfully")
        return {"status": "success", "message": "Training result saved."}
    except Exception as e:
        logger.error(f"Submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))