import streamlit as st
import chess.pgn
import chess.engine
import chess.svg
import io
import tempfile
from PIL import Image
import cairosvg

# Function to classify moves
def classify_move(player_move, best_move, eval_diff):
    if player_move == best_move:
        return "Good"
    elif eval_diff is not None:
        if abs(eval_diff) < 50:
            return "Inaccuracy"
        elif abs(eval_diff) < 200:
            return "Mistake"
        else:
            return "Blunder"
    return "Unknown"

# Analyze game and return feedback
def analyze_game(game, engine_path):
    board = game.board()
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    analysis = []

    for i, move in enumerate(game.mainline_moves(), start=1):
        info = engine.analyse(board, chess.engine.Limit(depth=15))
        best_move = engine.play(board, chess.engine.Limit(depth=15)).move
        eval_score = info["score"].relative.score(mate_score=10000)

        player_move = move
        move_quality = classify_move(player_move, best_move, eval_score)
        board.push(move)
        analysis.append({
            "move_num": i,
            "move": player_move,
            "eval_diff": eval_score,
            "classification": move_quality,
            "board_fen": board.fen()
        })

    engine.quit()
    return analysis

# Convert board to image
def render_board_svg(fen):
    board = chess.Board(fen)
    svg = chess.svg.board(board, size=400)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=f.name)
        return Image.open(f.name)

# Streamlit app
st.title("♟️ Chess Tutor & Move Evaluator")
st.markdown("Upload a PGN file, and get instant move feedback!")

stockfish_path = "stockfish"  # or provide full path to the executable

uploaded_file = st.file_uploader("Upload PGN File", type=["pgn"])

if uploaded_file is not None:
    game = chess.pgn.read_game(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
    if game:
        st.success("Game loaded successfully!")
        analysis = analyze_game(game, stockfish_path)

        for move_info in analysis:
            st.subheader(f"Move {move_info['move_num']}: {move_info['move']}")
            st.image(render_board_svg(move_info['board_fen']))
            st.write(f"**Evaluation:** {move_info['classification']} ({move_info['eval_diff']} cp)")
            st.markdown("---")
    else:
        st.error("Could not read PGN. Please check your file.")
