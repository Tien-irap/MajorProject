# The GlobalAnalyzer class must be defined/imported before this function.
import chess
import pandas as pd
from backend.app.core.logger import logger

def analyze_player_weaknesses_global(analysis_data, global_analyzer, player_name="Player"):
    """
    Analyzes a player's mistakes by classifying them using the global weakness profiles.

    Args:
        analysis_data (list): The list of dictionaries from the initial game analysis.
        global_analyzer (GlobalAnalyzer): An instance of the pre-trained global analyzer.
        player_name (str): The name of the player for the report.

    Returns:
        dict: A dictionary containing the summary of each global weakness cluster.
    """
    mistakes_data = [
        m for m in analysis_data if m['classification'] in ["Blunder", "Mistake"]
    ]

    if not mistakes_data:
        logger.warning("No mistakes found to perform analysis.")
        return None

    # 1. Feature Extraction: Create a dataset of mistakes
    features = []
    for move_data in mistakes_data:
        # Get the board state *before* the move to calculate piece count
        # Ensure 'move_num' is correct. For move 1, the previous board is the start.
        # analysis_data is 0-indexed, move_num is 1-indexed.
        prev_move_index = move_data['move_num'] - 2
        board_before_fen = analysis_data[prev_move_index]['board_fen'] if prev_move_index >= 0 else chess.STARTING_FEN
        board = chess.Board(board_before_fen)
        
        features.append({
            'move_num': move_data['move_num'],
            'eval_before': move_data.get('eval_before') or 0,
            'eval_diff': move_data['eval_diff'],
            'board_piece_count': len(board.piece_map()),
            'move_uci': move_data['move']
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
            "example_moves": llm_context["example_moves"],
            # Store the LLM context for later use
            "llm_context": llm_context
        }
        summary[f"Global Weakness Profile {i+1}"] = cluster_summary

        # Print the summary
        logger.debug(f"Global Weakness Profile {i+1}: {global_description}")
        logger.debug(f"Mistakes of this type: {cluster_summary['num_mistakes']}")
        logger.debug(f"Average Severity: {cluster_summary['avg_centipawn_loss']} centipawn loss")
        logger.debug(f"Example Moves: {', '.join(cluster_summary['example_moves'][:3])}...")

    return summary

# Example of the final step: Sending to an LLM
def generate_llm_explanation(cluster_summary):
    """
    Simulates sending the analysis to an LLM for a rich explanation.
    """
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