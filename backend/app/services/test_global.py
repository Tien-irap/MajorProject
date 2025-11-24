# main_analysis_script.py (Putting everything together)

# --- Imports from your files ---
import chess
import pandas as pd
from backend.app.services.global_analyzer import GlobalAnalyzer # Import the class defined above
# You would also import functions from analyze_pgn.py here:
from backend.app.services.analyze_pgn import analyze_game, engine_path 
# For this example, we'll assume a dummy data source for testing
from backend.app.core.logger import logger

# --- Your analyze_player_weaknesses_global function (from your prompt) ---
def analyze_player_weaknesses_global(analysis_data, global_analyzer, player_name="Player"):
    # ... (The exact code you provided for this function goes here)
    mistakes_data = [
        m for m in analysis_data if m['classification'] in ["Blunder", "Mistake"]
    ]

    if not mistakes_data:
        logger.warning("No mistakes found to perform analysis.")
        return None

    # 1. Feature Extraction: Create a dataset of mistakes
    features = []
    for move_data in mistakes_data:
        # NOTE: This part requires the analysis_data to have 'board_fen' for *all* half-moves
        prev_move_index = move_data['move_num'] - 2
        
        # Safety check: Use STARTING_FEN if it's move 1 (index -1)
        if prev_move_index < 0:
            board_before_fen = chess.STARTING_FEN
        else:
            # Handle the case where analysis_data might not be fully populated up to the move before
            try:
                board_before_fen = analysis_data[prev_move_index]['board_fen']
            except IndexError:
                # Fallback to an earlier position if possible, or STARTING_FEN
                board_before_fen = chess.STARTING_FEN

        board = chess.Board(board_before_fen)
        
        features.append({
            'move_num': move_data['move_num'],
            'eval_before': move_data['eval_before'] or 0,
            'eval_diff': move_data['eval_diff'],
            'board_piece_count': len(board.piece_map()),
            'move_uci': move_data['move'].uci()
        })
    
    df = pd.DataFrame(features)
    
    # 2. Classification against Global Profiles
    df = global_analyzer.analyze_user_mistakes(df)

    # 3. Interpretation: Analyze and describe each cluster
    summary = {}
    logger.info(f"Generating Global Weakness Analysis Report for {player_name}")
    
    for i in range(global_analyzer.n_clusters):
        cluster_df = df[df['global_cluster'] == i]
        
        if cluster_df.empty:
            continue
            
        profile = cluster_df[['move_num', 'eval_before', 'eval_diff', 'board_piece_count']].mean().to_dict()
        global_description = global_analyzer.global_profile_descriptions[i]
        
        # LLM Input Preparation: Gather all context for the LLM
        llm_context = {
            "player_mistake_count": len(cluster_df),
            "avg_severity": round(profile['eval_diff']),
            "avg_move_num": round(profile['move_num']),
            "avg_eval_before": round(profile['eval_before']),
            "avg_complexity": round(profile['board_piece_count']),
            "example_moves": cluster_df['move_uci'].tolist(),
            "global_pattern": global_description
        }
        
        cluster_summary = {
            "global_pattern_name": global_description,
            "num_mistakes": llm_context["player_mistake_count"],
            "avg_centipawn_loss": llm_context["avg_severity"],
            "example_moves": cluster_df['move_uci'].tolist(),
            "llm_context": llm_context
        }
        summary[f"Global Weakness Profile {i+1}"] = cluster_summary

        # Print the summary
        logger.debug(f"Global Weakness Profile {i+1}: {global_description}")
        logger.debug(f"Mistakes of this type: {cluster_summary['num_mistakes']}")
        logger.debug(f"Average Severity: {cluster_summary['avg_centipawn_loss']} centipawn loss")
        logger.debug(f"Example Moves: {', '.join(cluster_summary['example_moves'][:3])}...")

    return summary

# --- Your generate_llm_explanation function (from your prompt) ---
def generate_llm_explanation(cluster_summary):
    # ... (The exact code you provided for this function goes here)
    llm_context = cluster_summary['llm_context']
    
    # This is the prompt you would send to a powerful LLM (like GPT-4 or Gemini)
    prompt = f"""
    Analyze the player's weakness based on the following data:
    Global Weakness Pattern: "{llm_context['global_pattern']}"
    Player's Mistakes of this type: {llm_context['player_mistake_count']}
    Average Severity (centipawn loss): {llm_context['avg_severity']}
    Average Move Number: {llm_context['avg_move_num']} (Game Phase: {'Opening' if llm_context['avg_move_num'] < 15 else 'Middlegame' if llm_context['avg_move_num'] < 35 else 'Endgame'})
    Average Board Complexity (pieces): {llm_context['avg_complexity']}
    Evaluation Before Mistake: {llm_context['avg_eval_before']} (Context: {'Winning' if llm_context['avg_eval_before'] > 150 else 'Losing' if llm_context['avg_eval_before'] < -150 else 'Equal'})
    Example Moves (UCI): {', '.join(llm_context['example_moves'])}

    Provide a concise, encouraging, and actionable paragraph (100-150 words) explaining this weakness. 
    1. Acknowledge the pattern by name.
    2. Explain *why* the player is struggling with this type (e.g., are they underestimating simple threats or misjudging complex positions?).
    3. Suggest one concrete study recommendation (e.g., 'Do tactical puzzles focusing on pins' or 'Study a few master endgames').
    """
    
    # In production, you would call your LLM API here.
    logger.debug(f"LLM Explanation generated for {llm_context['global_pattern'].split(':')[0]}")
    # Placeholder for the actual LLM output
    llm_output = f"Your primary weakness, **{llm_context['global_pattern'].split(':')[0]}**, is a common issue where you miss immediate, simple threats. Your mistakes of this type are relatively severe, averaging a {llm_context['avg_severity']} centipawn loss, and tend to happen during the **{ 'Opening' if llm_context['avg_move_num'] < 15 else 'Middlegame'}** when the position is still quite **complex** ({llm_context['avg_complexity']} pieces). These errors indicate you may be over-focused on your own plans and missing your opponent's direct threats. To fix this, dedicate 15 minutes a day to solving **simple tactical puzzles** like **forks and pins** on platforms like Lichess or Chess.com, ensuring you check for opponent's checks, captures, and threats (the 'blunder check') before every move. Keep it up! 🚀"
    
    return llm_output


# --- DEMO USAGE ---

if __name__ == "__main__":
    # --- STEP 1: Load Global Mistake Data and Train the Analyzer ---
    
    # NOTE: Change this path to the CSV file you created in the 'output' folder
    GLOBAL_DATA_PATH = "/Users/paripatankar/Desktop/Major_project/output/global_mistake_features.csv" 
    
    # --- Dummy Data for Demonstration (Replace with actual loaded data) ---
    try:
        global_df = pd.read_csv(GLOBAL_DATA_PATH)
    except FileNotFoundError:
        logger.warning(f"Global data not found at {GLOBAL_DATA_PATH}. Using dummy data for demo.")
        # Create a dummy dataframe with the expected features
        global_df = pd.DataFrame({
            'move_num': [10, 25, 40, 15, 30, 45, 12, 38],
            'eval_before': [100, -50, 50, 800, 20, -100, 200, 10],
            'eval_diff': [150, 450, 300, 80, 600, 1000, 100, 400],
            'board_piece_count': [30, 25, 15, 30, 20, 10, 30, 18],
            'classification': ['Mistake', 'Blunder', 'Mistake', 'Mistake', 'Blunder', 'Blunder', 'Mistake', 'Blunder'],
            'player_elo': [1400, 1500, 1600, 1400, 1700, 1800, 1300, 1500]
        })
    # --- End Dummy Data ---
    
    # Initialize and train the global model
    global_analyzer = GlobalAnalyzer(n_clusters=4)
    global_analyzer.train_global_model(global_df)

    # --- STEP 2: Get a Single Game Analysis (Replace with your user's game) ---
    # This data would come from calling analyze_game() for a single user's PGN.
    # We use dummy data formatted exactly as analyze_game would return it.
    
    # Dummy user game analysis data (must include all half-moves, even non-mistakes)
    user_analysis = [
        {'move_num': 1, 'move': chess.Move.from_uci('e2e4'), 'classification': 'Best Move', 'eval_before': 0, 'eval_after': -30, 'eval_diff': 30, 'board_fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1'},
        {'move_num': 2, 'move': chess.Move.from_uci('e7e5'), 'classification': 'Excellent', 'eval_before': 30, 'eval_after': 30, 'eval_diff': 0, 'board_fen': 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2'},
        {'move_num': 3, 'move': chess.Move.from_uci('f1c4'), 'classification': 'Inaccuracy', 'eval_before': 30, 'eval_after': -100, 'eval_diff': 130, 'board_fen': 'rnbqkbnr/pppp1ppp/8/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR b KQkq - 1 2'},
        {'move_num': 4, 'move': chess.Move.from_uci('f7f6'), 'classification': 'Mistake', 'eval_before': 100, 'eval_after': -250, 'eval_diff': 350, 'board_fen': 'rnbqkbnr/pppp2pp/5p2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 0 3'}, # User Mistake 1 (Move 4)
        {'move_num': 5, 'move': chess.Move.from_uci('d2d4'), 'classification': 'Best Move', 'eval_before': 250, 'eval_after': -10, 'eval_diff': 260, 'board_fen': 'rnbqkbnr/pppp2pp/5p2/4p3/2BPP3/8/PPP2PPP/RNBQK1NR b KQkq - 0 3'},
        {'move_num': 6, 'move': chess.Move.from_uci('b8c6'), 'classification': 'Excellent', 'eval_before': 10, 'eval_after': 10, 'eval_diff': 0, 'board_fen': 'r1bqkbnr/pppp2pp/2n2p2/4p3/2BPP3/8/PPP2PPP/RNBQK1NR w KQkq - 1 4'},
        {'move_num': 7, 'move': chess.Move.from_uci('a2a3'), 'classification': 'Mistake', 'eval_before': 10, 'eval_after': -400, 'eval_diff': 410, 'board_fen': 'r1bqkbnr/pppp2pp/2n2p2/4p3/2BPP3/P7/1PP2PPP/RNBQK1NR b KQkq - 0 4'}, # User Mistake 2 (Move 7)
        {'move_num': 8, 'move': chess.Move.from_uci('g7g5'), 'classification': 'Blunder', 'eval_before': 400, 'eval_after': -900, 'eval_diff': 1300, 'board_fen': 'r1bqkbnr/pppp3p/2n2p2/4p1p1/2BPP3/P7/1PP2PPP/RNBQK1NR w KQkq - 0 5'}, # User Blunder 3 (Move 8)
    ]

    # --- STEP 3: Analyze the Player's Weaknesses Against Global Profiles ---
    player_name = "User Alpha"
    weakness_summary = analyze_player_weaknesses_global(user_analysis, global_analyzer, player_name)

    # --- STEP 4: Generate LLM Explanations ---
    if weakness_summary:
        logger.info("="*50)
        logger.info("LLM Explanation Section")
        logger.info("="*50)
        
        for profile_name, summary in weakness_summary.items():
            llm_explanation = generate_llm_explanation(summary)
            logger.info(f"{profile_name} LLM Feedback:\n{llm_explanation}")