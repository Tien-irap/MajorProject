import requests
import chess
import os
from dotenv import load_dotenv

# --- Configuration ---
API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL = "mistral-small-latest" # Using a slightly more powerful model for better analysis

# Load environment variables from .env file
load_dotenv()

def _call_mistral_api(prompt, api_key): # api_key is now passed from get_llm_summary_for_game
    """
    Helper function to call the Mistral API and return the response content.
    """
    if not api_key:
        return "Error: Mistral API key is missing." # Should not happen if checked in calling function

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

    prompt = f"""
    You are an expert chess coach speaking to a beginner or intermediate player. Your tone is encouraging and educational.
    Analyze the following chess move from a game.

    **Position Details:**
    - **Board State (FEN):** {board_before_move.fen()}
    - **Player to Move:** {turn}
    - **The move they played:** {move_data['move'].uci()} (Classification: {move_data['classification']})
    - **The engine's recommended best move:** {move_data['best_move'].uci()}
    - **Evaluation Change (Centipawn Loss):** {move_data['eval_diff']}

    **Your Task:**
    {task_description}

    Keep your entire explanation concise and easy to understand.
    """
    return prompt.strip()

def get_llm_summary_for_game(analysis_data): 
    """
    Takes the full game analysis, identifies key moves, gets LLM explanations,
    and returns a summary report as a dictionary.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key: # Check for API key here
        return {"error": "Mistral API key not found in environment variables. Please ensure it's set in your .env file (e.g., MISTRAL_API_KEY='your_key_here')."}
        
    summary = {}
    
    mistakes = sorted(
        [m for m in analysis_data if m['classification'] in ["Blunder", "Mistake"]],
        key=lambda x: x['eval_diff'],
        reverse=True
    )
    
    best_moves = sorted(
        [m for m in analysis_data if m['classification'] == "Best Move"],
        key=lambda x: x['eval_before'] if x['eval_before'] is not None else 0,
        reverse=True
    )

    summary['mistakes'] = []
    for i, mistake in enumerate(mistakes[:10]): # Get explanations for top 10 mistakes
        move_num = mistake['move_num']
        board_before = chess.Board() # Default to starting position
        if move_num > 1:
            # The 'board_fen' from the *previous* move's analysis is the state *before* this move.
            # `move_num` is 1-based, list is 0-based. So we access `move_num - 2`.
            # This logic is correct for getting the FEN *before* the current move.
            board_before = chess.Board(analysis_data[move_num - 2]['board_fen'])
        
        prompt = _create_prompt(mistake, board_before, "mistake")
        explanation = _call_mistral_api(prompt, api_key) # Pass api_key
        summary['mistakes'].append({
            "move_info": mistake,
            "board_before_fen": board_before.fen(),
            "explanation": explanation
        })

    summary['best_moves'] = []
    for i, best_move_data in enumerate(best_moves[:10]): # Get explanations for top 10 best moves
        move_num = best_move_data['move_num']
        board_before = chess.Board() # Default to starting position
        if move_num > 1:
            # Same logic for getting the FEN *before* the current move.
            board_before = chess.Board(analysis_data[move_num - 2]['board_fen'])
        
        prompt = _create_prompt(best_move_data, board_before, "best_move")
        explanation = _call_mistral_api(prompt, api_key) # Pass api_key
        summary['best_moves'].append({
            "move_info": best_move_data,
            "board_before_fen": board_before.fen(),
            "explanation": explanation
        })

    return summary