import chess.engine
import chess.pgn
import io
from .global_analyzer import GlobalAnalyzer

# CONFIG
# Make sure this path is correct for your system!
STOCKFISH_PATH = r"C:\Users\lenovo\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"

def perform_full_game_analysis(pgn_string: str, global_analyzer: GlobalAnalyzer):
    print("🚀 Starting Stockfish Analysis...")
    
    pgn_io = io.StringIO(pgn_string)
    game = chess.pgn.read_game(pgn_io)
    
    if not game:
        raise ValueError("Invalid PGN")

    board = game.board()
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    
    move_analysis = []
    
    try:
        # Analyze every move in the game
        for move in game.mainline_moves():
            # 1. Capture FEN BEFORE the move (for UI chessboard)
            fen_before = board.fen()
            
            # 2. Evaluate position BEFORE move (to see if move was good)
            info = engine.analyse(board, chess.engine.Limit(depth=18)) # Depth 18 is fast but decent
            score_before = info["score"].white().score(mate_score=10000)

            # Make the move on the board
            board.push(move)
            
            # 3. Evaluate position AFTER move
            info_after = engine.analyse(board, chess.engine.Limit(depth=18))
            score_after = info_after["score"].white().score(mate_score=10000)

            # 4. Calculate Diff (Flip for Black)
            if board.turn == chess.BLACK: # White just moved
                 diff = score_after - score_before
            else: # Black just moved
                 diff = -(score_after - score_before)

            # 5. Classify Move
            label = "normal"
            if diff <= -300: label = "blunder"
            elif diff <= -100: label = "mistake"
            elif diff <= -50: label = "inaccuracy"
            elif diff >= 200: label = "brilliant"
            elif diff >= 0: label = "best"

            move_analysis.append({
                "move_san": move.uci(),
                "score_differential": diff,
                "analysis": label,
                "fen": fen_before
            })

    except Exception as e:
        print(f"🔥 Analysis Error: {e}")
    finally:
        engine.quit()

    # --- 6. GENERATE SUMMARY FOR FRONTEND ---
    mistakes_list = []
    best_moves_list = []

    for i, m in enumerate(move_analysis):
        # Create the object structure the Frontend expects
        move_obj = {
            "move_info": {
                "move_num": (i // 2) + 1,
                "move": m["move_san"],
                "eval_diff": m["score_differential"],
                "board_before_fen": m["fen"]
            },
            "explanation": f"Evaluation changed by {m['score_differential']} points."
        }
        
        # Populate Lists based on label
        if m["analysis"] in ["mistake", "blunder"]:
            mistakes_list.append(move_obj)
        elif m["analysis"] in ["best", "brilliant"]:
            best_moves_list.append(move_obj)

    print(f"✅ Analysis Complete. Processed {len(move_analysis)} moves.")
    
    return {
        "game_headers": dict(game.headers),
        "move_by_move_analysis": move_analysis,
        "weakness_report": {}, 
        "key_move_summary": {
            "mistakes": mistakes_list,
            "best_moves": best_moves_list
        }
    }
