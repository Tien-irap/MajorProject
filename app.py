import streamlit as st
import chess.pgn
import chess.engine
import chess.svg
import io
import tempfile
from PIL import Image
import cairosvg

from analyze_pgn import analyze_game, render_board_svg, analyze_with_logs
from llm_analyzer import get_llm_summary_for_game, get_llm_weakness_summary
from weakness_analysis import analyze_player_weaknesses
from puzzle_generator import generate_puzzle_from_weakness 

# --- Streamlit App UI ---
st.set_page_config(page_title="Chess Tutor", layout="wide")
st.title("♟️ Chess Tutor & Move Evaluator")
st.markdown("Upload a PGN file of a completed game to get a detailed analysis and personalized feedback from our AI coach.")

# NEW: Add a sidebar for the API Key
#with st.sidebar: # Keep sidebar for general info, remove API key input
#    st.info("Your PGN analysis will appear on the main page after you upload a file.")


stockfish_path = "./stockfish/stockfish-macos-m1-apple-silicon"

uploaded_file = st.file_uploader("Upload Your PGN File Here", type=["pgn"])

if uploaded_file is not None:
    game = chess.pgn.read_game(io.StringIO(uploaded_file.getvalue().decode("utf-8")))

    if game:
        # Analyze the game using your existing function
        with st.spinner("Performing engine analysis on your game... this might take a moment."):
            analysis_result = analyze_game(game, stockfish_path)

        # Get the LLM summary for key moves
        with st.spinner("AI Coach is analyzing key moments..."):
            llm_summary = get_llm_summary_for_game(analysis_result) # No API key argument needed here
        
        # Perform weakness analysis
        player_name = game.headers.get("White", "Player") if game.headers.get("Result") == "1-0" else game.headers.get("Black", "Player")
        weakness_profiles = analyze_player_weaknesses(analysis_result, player_name=player_name)

        # Get LLM explanations for the weaknesses
        if weakness_profiles:
            with st.spinner("AI Coach is preparing your personalized weakness report..."):
                explained_weaknesses = get_llm_weakness_summary(weakness_profiles, player_name)

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
        st.header("Detailed Game Analysis")
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

        # --- Weakness Analysis Section ---
        if weakness_profiles and 'error' not in explained_weaknesses:
            st.header("🧠 Personalized Weakness Report")
            st.markdown("Based on the mistakes in this game, here are some patterns the AI coach identified.")

            for profile_key, profile_data in explained_weaknesses.items():
                st.subheader(f"{profile_data['profile_name']}")
                
                cols = st.columns([2, 1])
                with cols[0]:
                    st.info(f"**Coach's Diagnosis:** {profile_data['llm_explanation']}")
                    st.write(f"**Mistakes in this category:** {profile_data['num_mistakes']}")
                    st.write(f"**Average Severity:** {profile_data['avg_centipawn_loss']}cp loss")

                with cols[1]:
                    # Find the first example move's data to show the board
                    example_move_uci = profile_data['example_moves'][0]
                    move_data = next((m for m in analysis_result if m['move'].uci() == example_move_uci), None)
                    if move_data:
                        # Get board state *before* the move
                        board_before_fen = analysis_result[move_data['move_num'] - 2]['board_fen'] if move_data['move_num'] > 1 else chess.STARTING_FEN
                        st.image(render_board_svg(board_before_fen))
                        st.caption(f"Example position before the move {move_data['move'].uci()}")

                # --- Interactive Puzzle Section ---
                if st.button("Practice this weakness", key=f"practice_{profile_key}"):
                    with st.spinner("Generating a custom puzzle for you..."):
                        puzzle_data = generate_puzzle_from_weakness(profile_data['profile_name'])

                    if "error" in puzzle_data:
                        st.error(f"Could not generate puzzle: {puzzle_data['error']}")
                    else:
                        # Store puzzle data in session state to persist it
                        st.session_state[f'puzzle_{profile_key}'] = puzzle_data

                # Display the puzzle if it exists in the session state
                if f'puzzle_{profile_key}' in st.session_state:
                    puzzle = st.session_state[f'puzzle_{profile_key}']
                    st.subheader("Interactive Puzzle")
                    st.image(render_board_svg(puzzle['fen']))
                    
                    # User input for the move
                    user_move = st.text_input("Enter your move in UCI format (e.g., e2e4)", key=f"move_input_{profile_key}").strip().lower()

                    if user_move:
                        if user_move == puzzle['solution_uci']:
                            st.success(f"**Correct!** {puzzle['explanation']}")
                        else:
                            st.error("That's not the right move. Try again!")

                    # Hint/Options button
                    if st.button("Stuck? Show options", key=f"options_{profile_key}"):
                        options = puzzle['distractors'] + [puzzle['solution_uci']]
                        import random
                        random.shuffle(options)
                        
                        st.write("Which of these moves is best?")
                        # Use st.radio to present options
                        selected_option = st.radio("Choose a move:", options, key=f"radio_{profile_key}")
                        if selected_option == puzzle['solution_uci']:
                            st.write("That's the correct one! Try entering it above.")
                        else:
                            st.write("That's a common mistake, but not the best move here.")

                st.markdown("---")
        elif weakness_profiles and 'error' in explained_weaknesses:
            st.error(f"Could not generate weakness report: {explained_weaknesses['error']}")
    else:
        st.error("Could not read the PGN file. Please ensure it's a valid PGN.")