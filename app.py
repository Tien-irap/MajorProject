# app
import streamlit as st
import chess.pgn
import chess.engine
import chess.svg
import io
import tempfile
from PIL import Image
import cairosvg

from analyze_pgn import analyze_game, render_board_svg, analyze_with_logs
from llm_analyzer import get_llm_summary_for_game

# --- Streamlit App UI ---
st.set_page_config(page_title="Chess Tutor", layout="wide")
st.title("♟️ Chess Tutor & Move Evaluator")
st.markdown("Upload a PGN file of a completed game to get a detailed analysis and personalized feedback from our AI coach.")

# NEW: Add a sidebar for the API Key
#with st.sidebar: # Keep sidebar for general info, remove API key input
#    st.info("Your PGN analysis will appear on the main page after you upload a file.")


stockfish_path = "D:\\6th sem\\MP\\MajorProject\\stockfish\\stockfish.exe"

uploaded_file = st.file_uploader("Upload Your PGN File Here", type=["pgn"])

if uploaded_file is not None:
    game = chess.pgn.read_game(io.StringIO(uploaded_file.getvalue().decode("utf-8")))

    if game:
        # Analyze the game using your existing function
        with st.spinner("Performing engine analysis on your game... this might take a moment."):
            analysis_result = analyze_game(game, stockfish_path)

        # NEW: Get the LLM summary after the analysis is done
        with st.spinner("AI Coach is analyzing key moments..."):
            llm_summary = get_llm_summary_for_game(analysis_result) # No API key argument needed here
        
        st.header("AI Coach Summary")
        
        if "error" in llm_summary:
             st.error(llm_summary["error"])
        else:
            # Display Top Mistakes/Blunders
            if llm_summary['mistakes']:
                with st.expander("🔍 Top Mistakes/Blunders"):
                    for i, mistake_data in enumerate(llm_summary['mistakes']):
                        st.subheader(f"Mistake {i+1}: Move {mistake_data['move_info']['move_num']}")
                        move_info = mistake_data["move_info"]
                        st.markdown(f"**You played {move_info['move'].uci()}**")
                        
                        # We need the FEN *before* the move was made
                        board_before = chess.Board(mistake_data['board_before_fen'])
                        st.image(render_board_svg(board_before.fen()))
                        
                        st.info(f"**Coach's Advice:** {mistake_data['explanation']}")
                        if i < len(llm_summary['mistakes']) - 1:
                            st.markdown("---") # Separator for multiple mistakes

            # Display Top Best Moves
            if llm_summary['best_moves']:
                # Add a bit of space if there were mistakes displayed above
                if llm_summary['mistakes']:
                    st.markdown("---") 
                with st.expander("🏆 Top Best Moves"):
                    for i, best_move_data in enumerate(llm_summary['best_moves']):
                        st.subheader(f"Best Move {i+1}: Move {best_move_data['move_info']['move_num']}")
                        move_info = best_move_data["move_info"]
                        st.markdown(f"**You played {move_info['move'].uci()}**")
                        
                        board_before = chess.Board(best_move_data['board_before_fen'])
                        st.image(render_board_svg(board_before.fen()))
                        
                        st.success(f"**Coach's Analysis:** {best_move_data['explanation']}")
                        if i < len(llm_summary['best_moves']) - 1:
                            st.markdown("---") # Separator for multiple best moves
            
            if not llm_summary['mistakes'] and not llm_summary['best_moves']:
                st.info("No significant mistakes or best moves found for AI Coach analysis.")

        st.markdown("---")


        # Display the detailed move-by-move results in an expander
        with st.expander("Show Detailed Move-by-Move Analysis"):
            if not analysis_result:
                st.info("No moves to display in the detailed analysis.")
            
            for move_info in analysis_result:
                st.subheader(f"Move {move_info['move_num']}: {move_info['move'].uci()}")
                st.image(render_board_svg(move_info['board_fen']))

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Classical Analysis")
                    st.write(f"**Best Move:** `{move_info['best_move'].uci()}`")
                    st.write(f"**Classification:** {move_info['classification']}")
                    st.metric(label="Centipawn Loss", value=f"{move_info['eval_diff'] or 0} cp")

                with col2:
                    st.subheader("Win Probability Analysis")
                    st.write(f"**Classification:** {move_info['classification_wp']}")
                    st.metric(
                        label="Win Probability Drop",
                        value=f"{move_info['win_prob_drop']:.2%}",
                        delta=f"From {move_info['win_prob_before']:.1%} to {move_info['win_prob_after']:.1%}",
                        delta_color="inverse"
                    )

                if move_info['pv']:
                    pv_moves = ' → '.join([str(m) for m in move_info['pv']])
                    st.write(f"**Principal Variation:** {pv_moves}")

                st.markdown("---")
    else:
        st.error("Could not read the PGN file. Please ensure it's a valid PGN.")