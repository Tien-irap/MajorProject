import subprocess

process = subprocess.Popen(
    ["C:\\Users\\lenovo\\Downloads\\stockfish-windows-x86-64-avx2\\stockfish"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Send 'uci' command and 'quit' to terminate Stockfish
output, error = process.communicate(input=b"uci\nquit\n")

print(output.decode())

if __name__ == "__main__":
    game = load_game_from_pgn("lichess_db_standard_rated_2014-08.pgn")
    evals = evaluate_game(game)
    for move, label in evals:
        print(f"{move}: {label}")