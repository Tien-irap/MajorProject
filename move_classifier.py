import math

# K_FACTOR determines the steepness of the logistic curve. Adjust as needed.
K_FACTOR = 0.004

def centipawns_to_win_probability(centipawns):
    if centipawns is None:
        return 0.5 # Assume equal chances if evaluation is unknown
    try:
        return 1 / (1 + math.exp(-K_FACTOR * centipawns))
    except OverflowError:
        # If centipawns is a very large negative number, exp will be huge, prob -> 0
        # If centipawns is a very large positive number, exp will be tiny, prob -> 1
        return 0.0 if centipawns < 0 else 1.0

def classify_move_by_win_prob(player_move, best_move, eval_before, eval_after_player):
    if player_move == best_move:
        return "Best Move"

    if eval_before is None or eval_after_player is None:
        return "Unknown"

    win_prob_before = centipawns_to_win_probability(eval_before)
    win_prob_after = centipawns_to_win_probability(eval_after_player)

    win_prob_drop = win_prob_before - win_prob_after #damage done by move

    if win_prob_drop > 0.30:
        return "Blunder"
    elif win_prob_drop > 0.15:
        return "Mistake"
    elif win_prob_drop > 0.05: # A noticeable but not critical drop
        return "Inaccuracy"
    elif win_prob_drop > 0.02: # A very small, often acceptable drop
        return "Good"
    
    return "Excellent" # Includes best moves and moves with negligible win prob drop