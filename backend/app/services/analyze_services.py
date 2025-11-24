import chess.pgn
import io
import os
from typing import Dict, Any

# --- Import your ACTUAL analysis modules ---
from backend.app.services.analyze_pgn import analyze_game
from backend.app.services.weakness_analysis import analyze_player_weaknesses_global
from backend.app.services.llm_analyzer import (
    get_llm_summary_for_game,
    get_llm_weakness_summary
)
from backend.app.services.global_analyzer import GlobalAnalyzer
from backend.app.core.logger import logger

# --- Configuration ---
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "./stockfish/stockfish-macos-m1-apple-silicon")
if not os.path.exists(STOCKFISH_PATH):
    logger.error(f"Stockfish executable not found at {STOCKFISH_PATH}")

def perform_full_game_analysis(
    pgn_string: str, 
    global_analyzer: GlobalAnalyzer
) -> Dict[str, Any]:
    """
    Orchestrates the full, long-running game analysis pipeline.
    This function is called by the Celery task.
    
    Args:
        pgn_string (str): The PGN content of the game.
        global_analyzer (GlobalAnalyzer): The pre-trained K-Means model instance.
    """
    logger.info("Starting full analysis...")
    
    # 1. Load PGN string into a game object
    pgn_file = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn_file)
    
    if game is None:
        raise ValueError("Invalid PGN string provided. Could not read game.")

    game_headers = dict(game.headers)
    player_name = game_headers.get("White", "Player") # Just an example

    # 2. Call analyze_game from analyze_pgn.py
    logger.info(f"Running Stockfish analysis (Depth 15)...")
    move_analysis = analyze_game(game, STOCKFISH_PATH)
    
    if not move_analysis:
        logger.warning("No moves found in game. Aborting.")
        return {"error": "No moves found in PGN."}
        
    # 3. Call analyze_player_weaknesses_global
    logger.info("Analyzing player weaknesses...")
    # This report contains the raw clusters
    weakness_report_raw = analyze_player_weaknesses_global(
        move_analysis, 
        global_analyzer, 
        player_name=player_name
    )
    
    # 4. Call LLM functions for summaries and explanations
    
    # 4a. Get LLM summary for key moves (mistakes/best)
    logger.info("Generating LLM summary for key moves...")
    key_move_summary = get_llm_summary_for_game(move_analysis)
    
    # 4b. Get LLM explanations for the weakness profiles
    logger.info("Generating LLM explanations for weakness profiles...")
    weakness_report_explained = {}
    if weakness_report_raw:
        weakness_report_explained = get_llm_weakness_summary(
            weakness_report_raw, 
            player_name=player_name
        )
    else:
        logger.debug("No weaknesses found, skipping LLM summary.")

    # 5. Assemble the single, large result dictionary
    logger.info("Assembling final report.")
    final_result = {
        "game_headers": game_headers,
        "move_by_move_analysis": move_analysis,
        "weakness_report": weakness_report_explained,
        "key_move_summary": key_move_summary,
    }
    
    logger.info("Full analysis complete.")
    return final_result