# analyze_pgn
from dotenv import load_dotenv
import chess.pgn
import chess.engine
import os 
import subprocess
import tempfile
from PIL import Image
import cairosvg
import os
from pathlib import Path
from .move_classifier import (
    classify_move_by_win_prob,
    centipawns_to_win_probability
)

BACKEND_DIR = Path(__file__).parent.parent
load_dotenv(BACKEND_DIR / ".env")
STOCKFISH_PATH = BACKEND_DIR / "stockfish" / "stockfish.exe"
# Path to the Stockfish executable
# befor code: engine_path = "D:\\6th sem\\MP\\MajorProject\\stockfish\\stockfish.exe"

def analyze_with_logs(game, STOCKFISH_PATH):
    # start Stockfish subprocess
    engine = subprocess.Popen(
        STOCKFISH_PATH,
        universal_newlines=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1
    )

    # init UCI
    engine.stdin.write("uci\n")
    engine.stdin.flush()
    while True:
        if "uciok" in engine.stdout.readline():
            break

    board = game.board()
    logs = []

    for move in game.mainline_moves():
        board.push(move)
        fen = board.fen()

        engine.stdin.write(f"position fen {fen}\n")
        engine.stdin.write("go depth 12\n")
        engine.stdin.flush()

        move_log = []
        while True:
            output = engine.stdout.readline()
            move_log.append(output.strip())
            if "bestmove" in output:
                break
        logs.append({"move": move.uci(), "fen": fen, "log": move_log})

    engine.stdin.write("quit\n")
    engine.stdin.flush()
    engine.terminate()

    return logs

# Loading PGN file
def load_game_from_pgn(file_path):
    with open(file_path) as pgn_file:
        game = chess.pgn.read_game(pgn_file)
    return game

# Analyze moves 
def evaluate_game(game, stockfish_path="./stockfish"):
    board = game.board()
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

    evaluations = []
    for move in game.mainline_moves():
        info = engine.analyse(board, chess.engine.Limit(depth=15))
        best_move = engine.play(board, chess.engine.Limit(depth=15)).move
        eval_score = info["score"].relative.score(mate_score=10000)  # centipawn

        board.push(move)
        move_quality = classify_move(move, best_move, eval_score)
        evaluations.append((move, move_quality))

    engine.quit()
    return evaluations

# Analyze game and return feedback
def analyze_game(game, STOCKFISH_PATH):
    board = game.board()
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    analysis = []

    for i, move in enumerate(game.mainline_moves(), start=1):
        info_before = engine.analyse(board, chess.engine.Limit(depth=15))
        eval_before = info_before["score"].relative.score(mate_score=10000)
        best_move = engine.play(board, chess.engine.Limit(depth=15)).move
        pv_line = info_before.get("pv", [])

        player_move = move
        move_quality = classify_move(player_move, best_move, eval_before)

        board.push(move)
        info_after = engine.analyse(board, chess.engine.Limit(depth=15))
        eval_after = info_after["score"].relative.score(mate_score=10000)
        eval_diff = None
        eval_after_player = None
        if eval_before is not None and eval_after is not None:
            # eval_after is from the next player's perspective, so we negate it
            # to get the evaluation from the current player's perspective.
            eval_after_player = -eval_after
            eval_diff = eval_before - eval_after_player

        # The classification should be based on the drop in evaluation.
        # OLD CLASSIFICATION:
        move_quality_cp = classify_move(player_move, best_move, eval_diff)
        # NEW WIN PROBABILITY CLASSIFICATION:
        move_quality_wp = classify_move_by_win_prob(player_move, best_move, eval_before, eval_after_player)

        win_prob_before = centipawns_to_win_probability(eval_before)
        win_prob_after = centipawns_to_win_probability(eval_after_player)

        analysis.append({
            "move_num": i,
            "move": player_move,
            "best_move": best_move,
            "eval_before": eval_before,
            "eval_after": eval_after, # This is from the opponent's perspective
            "eval_diff": eval_diff, # This is the centipawn loss
            "classification": move_quality_cp, # Keep old one for reference if needed
            "classification_wp": move_quality_wp, # New classification
            "win_prob_before": win_prob_before,
            "win_prob_after": win_prob_after,
            "win_prob_drop": win_prob_before - win_prob_after,
            "pv": pv_line,
            "board_fen": board.fen()
        })

    engine.quit()
    return analysis



# Convert board to image to FEN
def render_board_svg(fen):
    board = chess.Board(fen)
    svg = chess.svg.board(board, size=400)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=f.name)
        return Image.open(f.name)

# Simple classification (expand later)
def classify_move(player_move, best_move, centipawn_loss):
    """
    Classifies a move based on the centipawn loss.
    `centipawn_loss` is the difference between the evaluation of the position
    before the move and the evaluation after the move from the same player's perspective.
    A positive value means a drop in evaluation.
    """
    if player_move == best_move:
        return "Best Move"
    
    if centipawn_loss is not None:
        if centipawn_loss < 20:
            return "Excellent"
        elif centipawn_loss < 50:
            return "Inaccuracy"
        elif centipawn_loss < 150:
            return "Mistake"
        else:
            return "Blunder"
    return "Unknown"
# Add this at the END of backend/app/services.py

def analyze_game_with_stockfish(pgn_content_string):
    """
    Main wrapper function to analyze a PGN game with Stockfish and return structured results.
    This is called by the FastAPI endpoint.
    """
    import io
    from .llm_analyzer import get_llm_summary_for_game
    
    # Parse the PGN string
    pgn_io = io.StringIO(pgn_content_string)
    game = chess.pgn.read_game(pgn_io)
    
    if not game:
        raise ValueError("Could not parse PGN file")
    
    # Extract game headers
    white_player = game.headers.get("White", "Unknown")
    black_player = game.headers.get("Black", "Unknown")
    result = game.headers.get("Result", "*")
    
    print(f"📊 Analyzing game: {white_player} vs {black_player}")
    
    # Perform the Stockfish analysis using your existing function
    print("🔍 Running Stockfish analysis...")
    analysis_result = analyze_game(game, str(STOCKFISH_PATH))
    print(f"✅ Stockfish analyzed {len(analysis_result)} moves")
    
    # Get LLM summary (top 10 best and worst moves with explanations)
    print("🤖 Getting AI coach feedback...")
    llm_summary = get_llm_summary_for_game(analysis_result)
    print("✅ AI analysis complete")
    
    # Format moves for the response
    moves_list = []
    for move_data in analysis_result:
        moves_list.append({
            "move_number": move_data["move_num"],
            "move": move_data["move"].uci(),
            "move_san": move_data["move"].uci(),
            "evaluation_before": move_data["eval_before"],
            "evaluation_after": -move_data["eval_after"] if move_data["eval_after"] is not None else None,
            "centipawn_loss": move_data["eval_diff"],
            "best_move": move_data["best_move"].uci(),
            "classification": move_data["classification"],
            "classification_wp": move_data["classification_wp"],
            "win_prob_before": move_data["win_prob_before"],
            "win_prob_after": move_data["win_prob_after"],
            "win_prob_drop": move_data["win_prob_drop"],
            "comment": None,
            "is_white": (move_data["move_num"] % 2 == 1)
        })
    
    # Format top 10 worst moves (mistakes/blunders)
    top_10_worst = []
    if "mistakes" in llm_summary and llm_summary["mistakes"]:
        for mistake in llm_summary["mistakes"][:10]:
            move_info = mistake["move_info"]
            top_10_worst.append({
                "move_number": move_info["move_num"],
                "move": move_info["move"].uci(),
                "centipawn_loss": move_info["eval_diff"] if move_info["eval_diff"] is not None else 0,
                "evaluation_before": move_info["eval_before"],
                "evaluation_after": -move_info["eval_after"] if move_info["eval_after"] is not None else None,
                "player": "White" if (move_info["move_num"] % 2 == 1) else "Black",
                "description": mistake["explanation"],
                "classification": move_info["classification"],
                "win_prob_drop": move_info["win_prob_drop"]
            })
    
    # Format top 10 best moves
    top_10_best = []
    if "best_moves" in llm_summary and llm_summary["best_moves"]:
        for best in llm_summary["best_moves"][:10]:
            move_info = best["move_info"]
            top_10_best.append({
                "move_number": move_info["move_num"],
                "move": move_info["move"].uci(),
                "centipawn_loss": move_info["eval_diff"] if move_info["eval_diff"] is not None else 0,
                "evaluation_before": move_info["eval_before"],
                "evaluation_after": -move_info["eval_after"] if move_info["eval_after"] is not None else None,
                "player": "White" if (move_info["move_num"] % 2 == 1) else "Black",
                "description": best["explanation"],
                "classification": move_info["classification"],
                "win_prob_drop": move_info["win_prob_drop"]
            })
    
    # Calculate average centipawn loss for each player
    white_moves = [m for m in analysis_result if m["move_num"] % 2 == 1]
    black_moves = [m for m in analysis_result if m["move_num"] % 2 == 0]
    
    avg_cpl_white = None
    avg_cpl_black = None
    
    if white_moves:
        white_losses = [m["eval_diff"] for m in white_moves if m["eval_diff"] is not None and m["eval_diff"] > 0]
        if white_losses:
            avg_cpl_white = sum(white_losses) / len(white_losses)
    
    if black_moves:
        black_losses = [m["eval_diff"] for m in black_moves if m["eval_diff"] is not None and m["eval_diff"] > 0]
        if black_losses:
            avg_cpl_black = sum(black_losses) / len(black_losses)
    
    # Return formatted response
    return {
        "game_summary": f"Analysis complete: {white_player} vs {black_player}",
        "white_player": white_player,
        "black_player": black_player,
        "result": result,
        "total_moves": len(analysis_result),
        "moves": moves_list,
        "top_10_best_moves": top_10_best,
        "top_10_worst_moves": top_10_worst,
        "average_centipawn_loss_white": avg_cpl_white,
        "average_centipawn_loss_black": avg_cpl_black,
        "pgn_content": pgn_content_string[:500] + "..." if len(pgn_content_string) > 500 else pgn_content_string
    }
