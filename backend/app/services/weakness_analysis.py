import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import chess

def analyze_player_weaknesses(analysis_data, player_name="Player", n_clusters=4):
    """
    Analyzes a player's mistakes from a game using K-Means clustering to find weakness patterns.

    Args:
        analysis_data (list): The list of dictionaries from the initial game analysis.
        player_name (str): The name of the player for the report.
        n_clusters (int): The number of weakness profiles to identify.

    Returns:
        dict: A dictionary containing the summary of each weakness cluster.
    """
    mistakes_data = [
        m for m in analysis_data if m['classification'] in ["Blunder", "Mistake"]
    ]

    if len(mistakes_data) < n_clusters:
        print("Not enough mistakes to perform a meaningful analysis.")
        return None

    # 1. Feature Extraction: Create a dataset of mistakes
    features = []
    for move_data in mistakes_data:
        # Get the board state *before* the move to calculate piece count
        board_before_fen = chess.STARTING_FEN
        if move_data['move_num'] > 1:
            # Find the analysis data for the move *before* the current one.
            # This is safer than assuming the index `move_num - 2` is correct,
            # especially if the list was ever filtered.
            previous_move_data = next((m for m in analysis_data if m['move_num'] == move_data['move_num'] - 1), None)
            if previous_move_data:
                board_before_fen = previous_move_data['board_fen']

        board = chess.Board(board_before_fen)
        
        features.append({
            'move_num': move_data['move_num'],
            'eval_before': move_data['eval_before'] or 0, # Was the position winning/losing?
            'eval_diff': move_data['eval_diff'], # How severe was the mistake?
            'board_piece_count': len(board.piece_map()), # How complex was the position?
            'move_uci': move_data['move'].uci()
        })
    
    df = pd.DataFrame(features)
    
    # Select only the numerical features for clustering
    numerical_features = df[['move_num', 'eval_before', 'eval_diff', 'board_piece_count']]

    # 2. Data Scaling: Normalize the features
    # This is crucial so that features with larger ranges (like eval_diff) don't dominate the clustering.
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(numerical_features)

    # 3. K-Means Clustering: Group the mistakes
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    df['cluster'] = kmeans.fit_predict(scaled_features)

    # 4. Interpretation: Analyze and describe each cluster
    summary = {}
    print(f"--- Weakness Analysis Report for {player_name} ---")
    for i in range(n_clusters):
        cluster_df = df[df['cluster'] == i]
        
        if cluster_df.empty:
            continue
            
        # Calculate the average characteristics of the mistakes in this cluster
        profile = cluster_df[['move_num', 'eval_before', 'eval_diff', 'board_piece_count']].mean().to_dict()
        
        # Generate a human-readable interpretation
        interpretation = []
        # Phase of game
        if profile['move_num'] < 15:
            interpretation.append("Opening Phase Errors:")
        elif profile['move_num'] < 35:
            interpretation.append("Middlegame Errors:")
        else:
            interpretation.append("Endgame Errors:")

        # Context of mistake
        if profile['eval_before'] > 150:
            interpretation.append("Failing to convert a winning advantage.")
        elif profile['eval_before'] < -150:
            interpretation.append("Making a bad position even worse.")
        else:
            interpretation.append("Critical mistakes made in equal positions.")
        
        # Complexity
        if profile['board_piece_count'] > 25:
            interpretation.append("Occur in complex positions with many pieces on the board.")
        else:
            interpretation.append("Occur in simpler, clearer positions.")
        
        cluster_summary = {
            "profile_name": " ".join(interpretation),
            "num_mistakes": len(cluster_df),
            "avg_centipawn_loss": round(profile['eval_diff']),
            "example_moves": cluster_df['move_uci'].tolist()
        }
        summary[f"Weakness Profile {i+1}"] = cluster_summary

        # Print the summary
        print(f"\n## Weakness Profile {i+1}: {cluster_summary['profile_name']}")
        print(f"   - Number of Mistakes: {cluster_summary['num_mistakes']}")
        print(f"   - Average Severity: {cluster_summary['avg_centipawn_loss']} centipawn loss")
        print(f"   - Example Moves: {', '.join(cluster_summary['example_moves'])}")

    return summary