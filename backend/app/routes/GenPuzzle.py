from fastapi import APIRouter, HTTPException
from typing import List
import os
import uuid

# 1. Import Service (The Logic)
from backend.app.services.GeneticAlgo import EvolutionaryPuzzleGenerator

# 2. Import Repository (The Database Access)
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
    Endpoint: Generates evolved puzzle variations from a single mistake FEN.
    
    Uses the Evolutionary Algorithm to create 3 unique variations while
    preserving the tactical motif.
    
    Returns: List of puzzles with fitness scores and metadata.
    """
    # Validate Stockfish path
    if not os.path.exists(STOCKFISH_PATH):
        logger.error(f"Stockfish engine not found at {STOCKFISH_PATH}")
        raise HTTPException(
            status_code=500, 
            detail=f"Stockfish engine not found at {STOCKFISH_PATH}. Please check STOCKFISH_PATH environment variable."
        )
    
    logger.info(f"Generating evolved puzzles for FEN: {request.fen[:50]}...")
    logger.info(f"Motif: {request.motif}, Move: {request.move_uci}")
    
    # 1. Initialize Evolutionary Generator
    generator = EvolutionaryPuzzleGenerator(STOCKFISH_PATH)
    
    try:
        # 2. Run the Evolution Loop (Returns top 3 puzzles)
        # This uses the refined workflow: elitism, asexual reproduction, 1 generation
        evolved_puzzles = generator.evolve_puzzle(
            parent_fen=request.fen,
            motif=request.motif or "Tactical Error",
            solution_move_uci=request.move_uci,
            num_generations=1
        )
        
        # Check if any puzzles were generated
        if not evolved_puzzles or len(evolved_puzzles) == 0:
            logger.warning("No puzzles generated - position may be invalid")
            raise HTTPException(
                status_code=400,
                detail="Could not generate puzzles from this position. The position may be invalid or already solved."
            )
        
        puzzle_objects = []
        
        # 3. Transform to DB Models
        for i, p_data in enumerate(evolved_puzzles):
            puzzle_id = str(uuid.uuid4())
            
            logger.info(f"Puzzle {i}: is_parent={p_data.get('is_parent', False)}, type={p_data.get('type')}, fitness={p_data.get('fitness')}")
            
            # Map the evolved puzzle data to our Pydantic DB model
            puzzle_obj = PuzzleDB(
                _id=puzzle_id,
                fen=p_data["fen"],
                solution=[p_data["best_move"]],  # Solution is the best move
                theme=p_data["motif"],
                generator_type="evolutionary",
                difficulty_level=request.difficulty_level,
                fitness=p_data["fitness"],
                best_move=p_data["best_move"],
                is_parent=p_data.get("is_parent", False)
            )
            puzzle_objects.append(puzzle_obj)
            logger.debug(f"Created puzzle object with is_parent={puzzle_obj.is_parent}")
        
        # 4. Save to MongoDB via Repository (Optional - for record keeping)
        if puzzle_objects:
            await training_repo.create_puzzles_bulk(puzzle_objects)
            logger.info(f"Successfully saved {len(puzzle_objects)} evolved puzzles to database")
            
        return puzzle_objects

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Puzzle generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
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