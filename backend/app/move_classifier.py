# move_classifier
import math

# A constant to scale the centipawn evaluation. A common value for chess is around 0.003 to 0.004.
# This value determines how sensitive the win probability is to changes in evaluation.
K_FACTOR = 0.004

def centipawns_to_win_probability(centipawns):
    """
    Converts a centipawn evaluation to an estimated win probability using a sigmoid function.
    Win_Prob = 1 / (1 + exp(-k * centipawns))
    """
    if centipawns is None:
        return 0.5 # Assume equal chances if evaluation is unknown
    try:
        return 1 / (1 + math.exp(-K_FACTOR * centipawns))
    except OverflowError:
        # If centipawns is a very large negative number, exp will be huge, prob -> 0
        # If centipawns is a very large positive number, exp will be tiny, prob -> 1
        return 0.0 if centipawns < 0 else 1.0

def classify_move_by_win_prob(player_move, best_move, eval_before, eval_after_player):
    """
    Classifies a move based on the drop in win probability.

    Args:
        player_move: The move played by the user.
        best_move: The best move according to the engine.
        eval_before: The centipawn evaluation *before* the player's move.
        eval_after_player: The centipawn evaluation *after* the player's move, from the player's perspective.
    """
    # A move can't be a blunder if it's the best move.
    if player_move == best_move:
        return "Best Move"

    if eval_before is None or eval_after_player is None:
        return "Unknown"

    win_prob_before = centipawns_to_win_probability(eval_before)
    win_prob_after = centipawns_to_win_probability(eval_after_player)

    win_prob_drop = win_prob_before - win_prob_after

    # Thresholds are based on the percentage drop in win probability (e.g., 0.30 is a 30% drop)
    if win_prob_drop > 0.30:
        return "Blunder"
    elif win_prob_drop > 0.15:
        return "Mistake"
    elif win_prob_drop > 0.05:
        return "Inaccuracy"
    elif win_prob_drop > 0.02: # Small drops are still good moves
        return "Good"
    else: # No drop or an increase in win probability
        return "Excellent"