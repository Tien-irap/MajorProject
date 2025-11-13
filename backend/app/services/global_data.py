import chess.pgn
import pandas as pd
import io 
import os
import chess
from backend.app.services.analyze_pgn import analyze_game, engine_path 

#debugging
def safe_int_conversion(elo_raw, default_elo=1200):
    #converts a raw ELO string (which might be '?', '', or 'Unrated') to an integer.
    if elo_raw is None:
        return default_elo
    elo_raw = str(elo_raw).strip()
    if elo_raw.isdigit():
        return int(elo_raw)
    return default_elo 

def create_global_mistakes_dataset(pgn_file_path, output_csv_path, max_games=None):
    all_mistakes = []
    game_count = 0
    
    # Use io.open for robust handling of large files and character encoding
    with io.open(pgn_file_path, encoding="utf-8") as pgn_file:
        
        while True:
            # chess.pgn.read_game reads one game at a time
            game = chess.pgn.read_game(pgn_file) 
            
            if game is None:
                break  # End of file
            
            if max_games and game_count >= max_games:
                break
                
            game_count += 1
            print(f"Analyzing Game {game_count}...")
            
            try:
                # 1. Safely extract ELO ratings from game headers
                white_elo_raw = game.headers.get("WhiteElo")
                black_elo_raw = game.headers.get("BlackElo")

                white_elo = safe_int_conversion(white_elo_raw)
                black_elo = safe_int_conversion(black_elo_raw)

                # 2. Analyze the game to get move features
                # NOTE: This call relies on your analyze_game function being correct
                game_analysis = analyze_game(game, engine_path)
                
                # 3. Filter for Mistakes and Blunders and compile features
                for m in game_analysis:
                    if m['classification'] in ["Mistake", "Blunder"]:
                        
                        # Determine the player who made the move: White (odd move_num) or Black (even move_num)
                        is_white_move = m['move_num'] % 2 != 0
                        
                        # Select the correct ELO for the player who made the mistake
                        player_elo = white_elo if is_white_move else black_elo

                        # Select and normalize the features we need for clustering
                        all_mistakes.append({
                            'move_num': m['move_num'],
                            'eval_before': m['eval_before'],
                            'eval_diff': m['eval_diff'],
                            'board_piece_count': m['board_piece_count'],
                            'classification': m['classification'],
                            'player_elo': player_elo
                        })

            except Exception as e:
                print(f"Error processing game {game_count}: {e}")
                continue
                
    # Convert the collected list of mistake features into a DataFrame
    global_df = pd.DataFrame(all_mistakes)
    
    # Save the resulting DataFrame to a CSV file
    global_df.to_csv(output_csv_path, index=False)
    print(f"\n✅ Successfully processed {game_count} games.")
    print(f"   Saved {len(global_df)} mistakes/blunders to {output_csv_path}")
    
# --- Execution Block ---
if __name__ == "__main__":
    INPUT_PGN = "/Users/paripatankar/Desktop/Major_project/data/MacKenzie.pgn"
    OUTPUT_FOLDER = "output"
    OUTPUT_FILENAME = "global_mistake_features.csv"
    
    # 1. Create the full path
    OUTPUT_CSV = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)
    
    # 2. Ensure the output directory exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    print(f"Saving data to: {os.path.abspath(OUTPUT_CSV)}")
    
    create_global_mistakes_dataset(INPUT_PGN, OUTPUT_CSV, max_games=100) 