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
    
    Returns:
        Dict[str, Any]: Complete analysis results including game headers, 
                       move-by-move analysis, weakness report, and key move summaries.
    """
    logger.info("🚀 Starting full game analysis pipeline...")
    
    # 1. Load PGN string into a game object
    logger.info("Step 1/5: Parsing PGN input...")
    pgn_file = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn_file)
    
    if game is None:
        logger.error("Failed to parse PGN string - invalid format")
        raise ValueError("Invalid PGN string provided. Could not read game.")

    game_headers = dict(game.headers)
    player_name = game_headers.get("White", "Player")
    logger.info(f"Game loaded: {game_headers.get('Event', 'Unknown Event')} - "
                f"White: {game_headers.get('White', 'Unknown')} vs "
                f"Black: {game_headers.get('Black', 'Unknown')}")

    # 2. Call analyze_game from analyze_pgn.py
    logger.info("Step 2/5: Running Stockfish analysis (Depth 15)...")
    try:
        move_analysis = analyze_game(game, STOCKFISH_PATH)
        logger.info(f"Stockfish analysis complete - {len(move_analysis) if move_analysis else 0} moves analyzed")
    except Exception as e:
        logger.error(f"Stockfish analysis failed: {str(e)}")
        raise
    
    if not move_analysis:
        logger.warning("No moves found in game. Aborting analysis.")
        return {"error": "No moves found in PGN."}
        
    # 3. Call analyze_player_weaknesses_global
    logger.info("Step 3/5: Analyzing player weaknesses using K-Means clustering...")
    try:
        weakness_report_raw = analyze_player_weaknesses_global(
            move_analysis, 
            global_analyzer, 
            player_name=player_name
        )
        logger.info("Weakness analysis complete")
    except Exception as e:
        logger.error(f"Weakness analysis failed: {str(e)}")
        weakness_report_raw = {}
    
    # 4. Call LLM functions for summaries and explanations
    logger.info("Step 4/5: Generating AI summaries and explanations...")
    
    # 4a. Get LLM summary for key moves (mistakes/best)
    logger.info("  - Generating LLM summary for key moves...")
    try:
        key_move_summary = get_llm_summary_for_game(move_analysis)
        
        # Enhance summary with frontend-friendly structure
        mistakes_count = len([m for m in move_analysis if m.get('analysis') in ['mistake', 'blunder', 'inaccuracy']])
        best_moves_count = len([m for m in move_analysis if m.get('analysis') in ['best', 'brilliant']])
        logger.info(f"  - Summary generated: {mistakes_count} mistakes/blunders, {best_moves_count} best/brilliant moves")
    except Exception as e:
        logger.error(f"LLM key move summary generation failed: {str(e)}")
        key_move_summary = {"mistakes": [], "best_moves": []}
    
    # 4b. Get LLM explanations for the weakness profiles
    logger.info("  - Generating LLM explanations for weakness profiles...")
    weakness_report_explained = {}
    if weakness_report_raw:
        try:
            weakness_report_explained = get_llm_weakness_summary(
                weakness_report_raw, 
                player_name=player_name
            )
            logger.info(f"  - Weakness explanations generated for {len(weakness_report_explained)} clusters")
        except Exception as e:
            logger.error(f"LLM weakness summary generation failed: {str(e)}")
            weakness_report_explained = {}
    else:
        logger.debug("No weaknesses found, skipping LLM weakness summary.")

    # 5. Assemble the single, large result dictionary
    logger.info("Step 5/5: Assembling final analysis report...")
    final_result = {
        "game_headers": game_headers,
        "move_by_move_analysis": move_analysis,
        "weakness_report": weakness_report_explained,
        "key_move_summary": key_move_summary,
    }
    
    logger.info(f"✅ Full analysis complete! Total moves: {len(move_analysis)}, "
                f"Weaknesses identified: {len(weakness_report_explained)}")
    return final_result
