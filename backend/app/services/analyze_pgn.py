import chess.pgn
import chess.engine
import os 
import subprocess
import tempfile
from PIL import Image
import cairosvg
from move_classifier import classify_move_by_win_prob,centipawns_to_win_probability


# Path to the Stockfish executable
engine_path = "./stockfish/stockfish-macos-m1-apple-silicon"

def analyze_with_logs(game, engine_path):
    # start Stockfish subprocess
    engine = subprocess.Popen(
        engine_path,
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
def analyze_game(game, engine_path):
    board = game.board()
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
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
            eval_after_player = -eval_after # eval_after is from the next player's perspective, so we negate it
            eval_diff = eval_before - eval_after_player

        
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
            "eval_after": eval_after, 
            "eval_diff": eval_diff, 
            "classification": move_quality_cp, 
            "classification_wp": move_quality_wp, 
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

# Simple classification 
def classify_move(player_move, best_move, centipawn_loss):
    if player_move == best_move:
        return "Best Move"  # A positive value means a drop in evaluation.
    
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
