import requests
import chess
import os
import time
from dotenv import load_dotenv
from backend.app.core.logger import logger

# --- Configuration ---
API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL = "mistral-small-latest" 

# Load environment variables from .env file
load_dotenv()

def _call_mistral_api(prompt, api_key): 
    if not api_key:
        return "Error: Mistral API key is missing." 

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        # Handle 429 specifically for better error messages
        if hasattr(e, 'response') and e.response.status_code == 429:
            return "Error: Mistral API rate limit hit. Please wait a moment."
        return f"Error calling Mistral API: {e}"

def _create_prompt(move_data, board_before_move, move_type):
    """
    Creates a detailed prompt for the LLM to analyze a single move.
    """
    turn = "White" if board_before_move.turn == chess.WHITE else "Black"
    
    if move_type == "mistake":
        task_description = """
        1.  **Explain the Mistake:** In simple terms, explain why the player's move was a blunder or mistake. Focus on the core reason (e.g., "it blundered your queen," "it missed a checkmate opportunity").
        2.  **Explain the Better Move:** Describe why the engine's recommended move is so much better. What does it accomplish?
        3.  **Provide a Key Takeaway:** Give a one-sentence lesson the player can learn.
        """
    else: # for "best_move"
        task_description = """
        1.  **Explain the Brilliance:** In simple terms, explain why this was a great move. Was it the only winning move? Did it start a powerful attack or cleverly solve a defensive problem?
        2.  **Describe the Idea:** What was the strategic or tactical idea behind this excellent move?
        3.  **Provide a Key Takeaway:** Give a one-sentence lesson about the pattern or idea behind this move.
        """

    # --- Use .get() for all dictionary access to prevent crashes ---
    prompt = f"""
    You are an expert chess coach speaking to a beginner or intermediate player. Your tone is encouraging and educational.
    Analyze the following chess move from a game.

    **Position Details:**
    - **Board State (FEN):** {board_before_move.fen()}
    - **Player to Move:** {turn} 
    - **The move they played:** {move_data.get('move', 'N/A')} (Classification: {move_data.get('classification', 'N/A')})
    - **The engine's recommended best move:** {move_data.get('best_move', 'N/A')}
    - **Evaluation Change (Centipawn Loss):** {move_data.get('eval_diff', 'N/A')}

    **Your Task:**
    {task_description}

    Keep your entire explanation concise and easy to understand.
    """
    return prompt.strip()

def _create_weakness_prompt(profile_data, player_name):
    """Creates a prompt for the LLM to explain a specific weakness profile."""
    prompt = f"""
    You are an expert chess coach summarizing a player's weakness. Your tone is encouraging and focused on improvement.

    **Player:** {player_name}

    **Identified Weakness Profile:**
    - **Profile Name:** {profile_data['global_pattern_name']}
    - **Number of Mistakes in this Category:** {profile_data['num_mistakes']}
    - **Average Severity:** {profile_data['avg_centipawn_loss']} centipawn loss

    **Your Task:**
    Based on the profile name (e.g., "Middlegame Errors: Failing to convert a winning advantage"), provide a short, insightful paragraph explaining this weakness.
    1.  **Explain the Pattern:** Describe what this pattern of mistakes means in simple terms.
    2.  **Give Actionable Advice:** Provide one or two concrete tips on how the player can work on this weakness. For example, suggest specific things to think about during a game or types of puzzles to practice.
    3.  **Keep it encouraging and concise.**

    **Example Output Structure:**
    "It looks like you sometimes struggle in complex middlegame positions when you have a winning advantage. This often happens when... To improve, try to... Before you move, always ask yourself..."
    """
    return prompt.strip()

def get_llm_weakness_summary(weakness_profiles, player_name="Player"):
    """
    Uses an LLM to generate a narrative explanation for identified weakness profiles.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        return {"error": "Mistral API key not found."}

    explained_profiles = {}
    for profile_key, profile_data in weakness_profiles.items():
        prompt = _create_weakness_prompt(profile_data, player_name)
        explanation = _call_mistral_api(prompt, api_key)

        new_profile_data = profile_data.copy()
        new_profile_data["llm_explanation"] = explanation
        explained_profiles[profile_key] = new_profile_data
        
        time.sleep(1) # <-- 2. Add a 1-second delay to this loop too

    return explained_profiles

def get_llm_summary_for_game(analysis_data): 
    """
    Takes the full game analysis, identifies key moves, gets LLM explanations,
    and returns a summary report as a dictionary.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key: 
        return {"error": "Mistral API key not found in environment variables. Please ensure it's set in your .env file (e.g., MISTRAL_API_KEY='your_key_here')."}
        
    summary = {}
    
    mistakes = sorted(
        [m for m in analysis_data if m.get('classification') in ["Blunder", "Mistake"]],
        key=lambda x: x.get('eval_diff') if x.get('eval_diff') is not None else 0, 
        reverse=True
    )
    
    best_moves = sorted(
        [m for m in analysis_data if m.get('classification') == "Best Move"],
        key=lambda x: x.get('eval_before') if x.get('eval_before') is not None else 0, 
        reverse=True
    )

    summary['mistakes'] = []
    for i, mistake_data in enumerate(mistakes[:10]): 
        
        board_before_fen_str = mistake_data.get("board_before_fen") 
        if not board_before_fen_str:
            board_before = chess.Board() 
        else:
            board_before = chess.Board(board_before_fen_str)

        prompt = _create_prompt(mistake_data, board_before, "mistake")
        explanation = _call_mistral_api(prompt, api_key) 

        sanitized_move_info = mistake_data.copy()
        
        summary['mistakes'].append({
            "move_info": sanitized_move_info,
            "explanation": explanation
        })
        
        time.sleep(1)  # <-- 3. Add a 1-second delay *after* each API call

    summary['best_moves'] = []
    for i, best_move_data in enumerate(best_moves[:10]): 
        
        board_before_fen_str = best_move_data.get("board_before_fen") 
        if not board_before_fen_str:
            board_before = chess.Board() 
        else:
            board_before = chess.Board(board_before_fen_str)
        
        prompt = _create_prompt(best_move_data, board_before, "best_move")
        explanation = _call_mistral_api(prompt, api_key)

        sanitized_move_info = best_move_data.copy()

        summary['best_moves'].append({
            "move_info": sanitized_move_info,
            "explanation": explanation
        })
        
        time.sleep(1)  # <-- 4. Add a 1-second delay *after* each API call

    return summary