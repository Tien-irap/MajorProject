import chess
import chess.pgn
import chess.engine
import io
import pandas as pd
import argparse
from multiprocessing import Pool, cpu_count
import time

# --- Constants ---
STOCKFISH_PATH = "./stockfish/stockfish-macos-m1-apple-silicon" # Adjust this path 
ANALYSIS_TIME_LIMIT = 0.1  # Seconds per move. Keep this low for batch processing.
MIN_RATING = 1400 # Minimum ELO of players to analyze
MAX_RATING = 1600 # Maximum ELO of players to analyze
# Set to True to analyze all games regardless of player rating.
IGNORE_RATING_FILTER = True 
def get_move_classification(eval_diff):
    """Classify a move based on centipawn loss."""
    if eval_diff >= 300:
        return "Blunder"
    if eval_diff >= 100:
        return "Mistake"
    return None

def extract_positional_features(board):
    """Extracts features that describe the board state."""
    feature_dict = {}
    for piece_type in chess.PIECE_TYPES:
        # Count pieces for each color
        feature_dict[f'white_{chess.piece_name(piece_type)}s'] = len(board.pieces(piece_type, chess.WHITE))
        feature_dict[f'black_{chess.piece_name(piece_type)}s'] = len(board.pieces(piece_type, chess.BLACK))
    
    # Total piece count (as a measure of complexity)
    feature_dict['piece_count'] = len(board.piece_map())
    return feature_dict

def analyze_game_worker(game_pgn_str):
    """
    Worker function to analyze a single game from its PGN string.
    """
    game_mistakes = []
    game = chess.pgn.read_game(io.StringIO(game_pgn_str))
    if game is None:
        return []

    try:
        # Safely get ratings, defaulting to 0 if not present
        white_elo = int(game.headers.get("WhiteElo", 0))
        black_elo = int(game.headers.get("BlackElo", 0))

        # --- Filter for relevant games based on rating ---
        if not IGNORE_RATING_FILTER:
            # If both players have no rating, skip unless filter is ignored
            if white_elo == 0 and black_elo == 0:
                return []
            # If at least one player is outside the range, skip
            if not (MIN_RATING <= white_elo <= MAX_RATING or MIN_RATING <= black_elo <= MAX_RATING):
                return []

        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            board = game.board()
            for move in game.mainline_moves():
                info_before = engine.analyse(board, chess.engine.Limit(time=ANALYSIS_TIME_LIMIT))
                eval_before_cp = info_before['score'].relative.score(mate_score=10000)

                board.push(move)
                info_after = engine.analyse(board, chess.engine.Limit(time=ANALYSIS_TIME_LIMIT))
                eval_after_player = -info_after['score'].relative.score(mate_score=10000)

                eval_diff = eval_before_cp - eval_after_player

                classification = get_move_classification(eval_diff)
                if classification:
                    board_before_move = board.copy()
                    board_before_move.pop()

                    player_elo = white_elo if board_before_move.turn == chess.WHITE else black_elo
                    mistake_data = {
                        'player_rating': player_elo,
                        'move_number': board_before_move.fullmove_number,
                        'classification': classification,
                        'eval_before': eval_before_cp,
                        'eval_diff': eval_diff,
                        'fen_before_mistake': board_before_move.fen(),
                    }
                    positional_features = extract_positional_features(board_before_move)
                    mistake_data.update(positional_features)
                    game_mistakes.append(mistake_data)
    except (ValueError, AttributeError) as e:
        # Print a warning but continue processing other games
        print(f"\nWarning: Skipping a game due to an error: {e}")
    
    return game_mistakes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a mistake dataset from a PGN file.")
    parser.add_argument("pgn_file", help="Path to the PGN file.")
    parser.add_argument("output_csv", help="Path to save the output CSV file.")
    parser.add_argument("--max_games", type=int, default=None, help="Maximum number of games to process (for testing).")
    args = parser.parse_args()

    num_workers = cpu_count()
    print(f"Starting analysis with {num_workers} worker processes...")
    all_mistakes = []
    start_time = time.time()

    with Pool(processes=num_workers) as pool:
        # Use chess.pgn.read_game to stream games from the PGN file
        with open(args.pgn_file) as pgn:
            game_iterator = iter(lambda: chess.pgn.read_game(pgn), None)
            
            # Process games in chunks for better performance
            chunk_size = num_workers * 50
            games_processed = 0

            while True:
                # Manually create PGN strings for each game to pass to workers
                game_chunk = [str(game) for _, game in zip(range(chunk_size), game_iterator) if game is not None]

                if not game_chunk:
                    break

                results = pool.map(analyze_game_worker, game_chunk)
                
                for game_mistakes in results:
                    if game_mistakes:
                        all_mistakes.extend(game_mistakes)
                
                games_processed += len(game_chunk)
                elapsed_time = time.time() - start_time
                games_per_second = games_processed / elapsed_time if elapsed_time > 0 else 0
                
                print(f"Games processed: {games_processed} | Mistakes found: {len(all_mistakes)} | Speed: {games_per_second:.2f} games/sec", end='\r')

                if args.max_games and games_processed >= args.max_games:
                    print(f"\nReached max_games limit of {args.max_games}.")
                    break

    if all_mistakes:
        df = pd.DataFrame(all_mistakes)
        df.to_csv(args.output_csv, index=False)
        print(f"\n\nSuccessfully processed and saved {len(all_mistakes)} mistakes to {args.output_csv}")
    else:
        print("\n\nNo mistakes found or no games processed.")