import streamlit as st
import chess.pgn
import chess.engine
import chess.svg
import io
import tempfile
from PIL import Image
import cairosvg
from analyze_pgn import analyze_game, render_board_svg, analyze_with_logs
from parse_log import parse_uci_log
from pv import render_board_from_pv_moves

# Streamlit app
st.title("♟️ Chess Tutor & Move Evaluator")
st.markdown("Upload a PGN file, and get instant move feedback!")

stockfish_path = "./stockfish/stockfish-macos-m1-apple-silicon"  # or provide full path to the executable

uploaded_file = st.file_uploader("Upload PGN File", type=["pgn"])

if uploaded_file is not None:
    game = chess.pgn.read_game(io.StringIO(uploaded_file.getvalue().decode("utf-8")))

    if game:
        st.success("Game loaded successfully!")
        # Analyze the game
        analysis_result = analyze_game(game, stockfish_path)

        # Display results in the frontend
        for move_info in analysis_result:
            st.subheader(f"Move {move_info['move_num']}: {move_info['move']}")
            st.image(render_board_svg(move_info['board_fen']))

            st.write(f"**Best Move:** {move_info['best_move']}")
            st.write(f"**Evaluation Before Move:** {move_info['eval_before']} cp")
            st.write(f"**Evaluation After Move:** {move_info['eval_after']} cp")
            st.write(f"**Evaluation Difference:** {move_info['eval_diff']} cp")
            st.write(f"**Classification:** {move_info['classification']}")

            # If there are PV moves, display them
            if move_info['pv']:
                pv_moves = ' → '.join([str(m) for m in move_info['pv']])
                st.write(f"**PV line:** {pv_moves}")

            st.markdown("---")

        # UCI log analysis
        uci_logs = analyze_with_logs(game, stockfish_path)

        # Display move boards and logs
        for log_entry in uci_logs:
            st.subheader(f"Move: {log_entry['move']}")
            st.image(render_board_svg(log_entry['fen']))
            st.text_area("UCI Log Output", "\n".join(log_entry["log"]), height=200)
            st.markdown("---")

    else:
        st.error("Could not read PGN. Please check your file.")

st.markdown("## 📌 Paste UCI Log Lines to Parse PV")

uci_log = st.text_area("Paste your UCI log lines here:")

if st.button("Parse and Visualize PV"):
    result = parse_uci_log(uci_log)

    if result:
        st.success(f"Found PV at depth {result['depth']} | Score: {result['score_value']} ({result['score_type']})")
        st.write("**PV Move Sequence:**", " → ".join(result["pv_moves"]))

        st.image(render_board_from_pv_moves(result["pv_moves"]))
    else:
        st.error("No valid PV line found in the log.")


