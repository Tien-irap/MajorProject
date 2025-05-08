import subprocess

process = subprocess.Popen(
    ["./stockfish/stockfish-macos-m1-apple-silicon"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Send 'uci' command and 'quit' to terminate Stockfish
output, error = process.communicate(input=b"uci\nquit\n")

print(output.decode())

