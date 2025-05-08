import chess.pgn
import chess.engine
import os 
import subprocess

# Path to the Stockfish executable
engine_path = "./stockfish/stockfish-macos-m1-apple-silicon"

# Start Stockfish engine process
engine = subprocess.Popen(
    engine_path,
    universal_newlines=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE
)

# Send a UCI command to check it's working
engine.stdin.write("uci\n")
engine.stdin.flush()

# Read the engine response
while True:
    output = engine.stdout.readline()
    print(output.strip())
    if "uciok" in output:
        break

# Example: set up position and ask for best move
engine.stdin.write("position startpos\n")
engine.stdin.write("go depth 10\n")
engine.stdin.flush()

# Read best move output
while True:
    output = engine.stdout.readline()
    print(output.strip())
    if "bestmove" in output:
        break

# Close engine process
engine.stdin.write("quit\n")
engine.stdin.flush()
engine.terminate()
# Loading PGN file
def load_game_from_pgn(file_path):
    with open(file_path) as pgn_file:
        game = chess.pgn.read_game(pgn_file)
    return game

# Analyze moves using Stockfish
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

# Simple classification (expand later)
def classify_move(player_move, best_move, eval_score):
    if player_move == best_move:
        return "Good"
    elif eval_score is not None:
        if abs(eval_score) < 50:
            return "Inaccuracy"
        elif abs(eval_score) < 200:
            return "Mistake"
        else:
            return "Blunder"
    return "Unknown"

# Example usage
if __name__ == "__main__":
    game = load_game_from_pgn("lichess_db_standard_rated_2014-08.pgn")
    evals = evaluate_game(game)
    for move, label in evals:
        print(f"{move}: {label}")
