import chess.engine
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
from .global_analyzer import GlobalAnalyzer

# CONFIG
# Make sure this path is correct for your system!
STOCKFISH_PATH = r"C:\Users\lenovo\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"

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
def perform_full_game_analysis(pgn_string: str, global_analyzer: GlobalAnalyzer):
    print("🚀 Starting Stockfish Analysis...")
    
    pgn_io = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn_io)
    
    if not game:
        raise ValueError("Invalid PGN")

    board = game.board()
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    
    move_analysis = []
    
    try:
        # Analyze every move in the game
        for move in game.mainline_moves():
            # 1. Capture FEN BEFORE the move (for UI chessboard)
            fen_before = board.fen()
            
            # 2. Evaluate position BEFORE move (to see if move was good)
            info = engine.analyse(board, chess.engine.Limit(depth=18)) # Depth 18 is fast but decent
            score_before = info["score"].white().score(mate_score=10000)

            # Make the move on the board
            board.push(move)
            
            # 3. Evaluate position AFTER move
            info_after = engine.analyse(board, chess.engine.Limit(depth=18))
            score_after = info_after["score"].white().score(mate_score=10000)

            # 4. Calculate Diff (Flip for Black)
            if board.turn == chess.BLACK: # White just moved
                 diff = score_after - score_before
            else: # Black just moved
                 diff = -(score_after - score_before)

            # 5. Classify Move
            label = "normal"
            if diff <= -300: label = "blunder"
            elif diff <= -100: label = "mistake"
            elif diff <= -50: label = "inaccuracy"
            elif diff >= 200: label = "brilliant"
            elif diff >= 0: label = "best"

            move_analysis.append({
                "move_san": move.uci(),
                "score_differential": diff,
                "analysis": label,
                "fen": fen_before
            })

    except Exception as e:
        print(f"🔥 Analysis Error: {e}")
    finally:
        engine.quit()

    # --- 6. GENERATE SUMMARY FOR FRONTEND ---
    mistakes_list = []
    best_moves_list = []

    for i, m in enumerate(move_analysis):
        # Create the object structure the Frontend expects
        move_obj = {
            "move_info": {
                "move_num": (i // 2) + 1,
                "move": m["move_san"],
                "eval_diff": m["score_differential"],
                "board_before_fen": m["fen"]
            },
            "explanation": f"Evaluation changed by {m['score_differential']} points."
        }
        
        # Populate Lists based on label
        if m["analysis"] in ["mistake", "blunder"]:
            mistakes_list.append(move_obj)
        elif m["analysis"] in ["best", "brilliant"]:
            best_moves_list.append(move_obj)

    print(f"✅ Analysis Complete. Processed {len(move_analysis)} moves.")
    
    return {
        "game_headers": dict(game.headers),
        "move_by_move_analysis": move_analysis,
        "weakness_report": weakness_report_explained,
        "key_move_summary": key_move_summary,
    }
    
    logger.info("Full analysis complete.")
    return final_result
        "weakness_report": {}, 
        "key_move_summary": {
            "mistakes": mistakes_list,
            "best_moves": best_moves_list
        }
    }
