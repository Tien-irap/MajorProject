from typing import Dict, Any

# --- MASTER BENCHMARKS ---
MASTER_STATS = {
    "acpl": 15.0,             # Average Centipawn Loss (Lower is better)
    "blunder_rate": 0.8,      # Percentage of moves that are blunders
    "mistake_rate": 2.5,      # Percentage of moves that are mistakes
    "opening_accuracy": 98.0, # Percentage of "book" or "best" moves in opening
    "endgame_precision": 95.0 # Precision in the last phase of the game
}

def compare_with_master(user_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compares user analysis stats with Master benchmarks.
    Calculates stats dynamically from 'move_by_move_analysis' if pre-computed stats are missing.
    """
    print("\n🔍 DEBUG: Calculating stats from move_by_move_analysis...")

    moves = user_result.get("move_by_move_analysis", [])
    
    if not moves:
        print("⚠️ WARNING: No moves found in analysis result.")
        return {"error": "No move analysis found"}

    # --- 1. CALCULATE STATS FROM MOVES ---
    total_moves = len(moves)
    total_cp_loss = 0
    blunder_count = 0
    mistake_count = 0
    
    # Opening: First 10 moves
    opening_limit = min(10, total_moves)
    opening_good_moves = 0
    
    # Endgame: Last 20 moves ONLY if game > 30 moves
    endgame_moves_list = moves[-20:] if total_moves > 30 else []
    endgame_cp_loss = 0

    for i, move in enumerate(moves):
        # Extract CP Loss (handle Mate scores which might be large ints or strings)
        raw_score = move.get("score_differential", 0)
        
        # Basic filtering for valid CP loss (ignore massive spikes from forced mate)
        try:
            val = float(raw_score)
            if abs(val) < 2000: # Standard CP range
                cp_loss = abs(val)
            else:
                cp_loss = 0 # Ignore mate sequences for ACPL
        except (ValueError, TypeError):
            cp_loss = 0
            
        total_cp_loss += cp_loss
        
        # Check Analysis Label for Blunders/Mistakes
        label = move.get("analysis", "").lower() # e.g. "blunder", "mistake", "best move"
        if "blunder" in label:
            blunder_count += 1
        if "mistake" in label:
            mistake_count += 1
            
        # Opening Accuracy Calculation
        if i < opening_limit:
             if "best" in label or "excellent" in label or "book" in label or "good" in label:
                 opening_good_moves += 1

        # Endgame CP Loss Calculation
        if endgame_moves_list and move in endgame_moves_list:
             endgame_cp_loss += cp_loss

    # --- 2. COMPUTE AVERAGES ---
    
    # ACPL (Average Centipawn Loss)
    user_acpl = total_cp_loss / total_moves if total_moves > 0 else 0
    
    # Rates (Percentage)
    user_blunder_rate = (blunder_count / total_moves) * 100 if total_moves > 0 else 0
    user_mistake_rate = (mistake_count / total_moves) * 100 if total_moves > 0 else 0
    
    # Opening Accuracy
    opening_acc = (opening_good_moves / opening_limit) * 100 if opening_limit > 0 else 0.0
    
    # Endgame Precision
    if len(endgame_moves_list) > 0:
        avg_endgame_loss = (endgame_cp_loss / len(endgame_moves_list))
        # Simple formula: 100 - (Loss * 0.5). Loss of 0 = 100. Loss of 50 = 75.
        endgame_prec = max(0, 100 - (avg_endgame_loss * 0.5))
    else:
        # Game didn't reach endgame -> Return 0 to indicate "N/A" visually (or could handle differently)
        endgame_prec = 0.0

    # Debug Prints to verify calculations
    print(f"📊 STATS CALC: Moves={total_moves}, ACPL={user_acpl:.2f}, Blunders={blunder_count}, Opening Acc={opening_acc:.2f}, Endgame Prec={endgame_prec:.2f}")

    # --- 3. BUILD RESPONSE LIST ---
    comparison_list = [
        {
            "metric": "ACPL",
            "master": MASTER_STATS["acpl"],
            "user": round(user_acpl, 2),
            "difference": round(user_acpl - MASTER_STATS["acpl"], 2),
            "percentage_diff": 0
        },
        {
            "metric": "Blunder Rate",
            "master": MASTER_STATS["blunder_rate"],
            "user": round(user_blunder_rate, 2),
            "difference": round(user_blunder_rate - MASTER_STATS["blunder_rate"], 2),
            "percentage_diff": 0
        },
        {
            "metric": "Mistake Rate",
            "master": MASTER_STATS["mistake_rate"],
            "user": round(user_mistake_rate, 2),
            "difference": round(user_mistake_rate - MASTER_STATS["mistake_rate"], 2),
            "percentage_diff": 0
        },
        {
            "metric": "Opening Accuracy",
            "master": MASTER_STATS["opening_accuracy"],
            "user": round(opening_acc, 2),
            "difference": round(MASTER_STATS["opening_accuracy"] - opening_acc, 2),
            "percentage_diff": 0
        },
        {
            "metric": "Endgame Precision",
            "master": MASTER_STATS["endgame_precision"],
            "user": round(endgame_prec, 2),
            "difference": round(MASTER_STATS["endgame_precision"] - endgame_prec, 2),
            "percentage_diff": 0
        }
    ]

    # --- 4. GENERATE VERDICT ---
    summary = f"Analysis based on {total_moves} moves. "
    
    if user_acpl < 30 and total_moves > 10:
        summary += "Incredible precision! You played very accurately. "
    elif user_acpl < 60:
        summary += "Solid game, but some inaccuracies crept in. "
    elif user_acpl > 100:
        summary += "High error rate detected. Focus on basic tactical safety. "
    else:
        summary += "Average performance with some tactical slips. "
        
    if user_blunder_rate > 2.0:
        summary += " Blunder rate is high - try to double-check your moves."
        
    if endgame_prec == 0.0 and total_moves > 0:
        summary += " (Game ended before endgame phase)."

    return {
        "comparison": comparison_list,
        "summary": summary
    }
