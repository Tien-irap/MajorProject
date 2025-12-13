import requests
import chess
import os
import time
import json
from dotenv import load_dotenv
from backend.app.core.logger import logger

# --- Configuration ---
API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL = "mistral-small-latest" 

# Load environment variables from .env file
load_dotenv()

def _call_mistral_api(prompt, api_key, use_json_mode=False): 
    if not api_key:
        return "Error: Mistral API key is missing." 

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "user", "content": prompt}]
    
    # If JSON mode is requested, add a system message enforcing it
    if use_json_mode:
        messages.insert(0, {
            "role": "system", 
            "content": "You are a helpful assistant that always responds with valid JSON. Never include any text outside the JSON structure."
        })
    
    data = {
        "model": MODEL,
        "messages": messages
    }
    
    # Enable JSON mode if requested
    if use_json_mode:
        data["response_format"] = {"type": "json_object"}

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        logger.debug(f"LLM Response (first 200 chars): {content[:200]}")
        return content
    except requests.exceptions.RequestException as e:
        # Handle 429 specifically for better error messages
        if hasattr(e, 'response') and e.response.status_code == 429:
            return "Error: Mistral API rate limit hit. Please wait a moment."
        logger.error(f"Mistral API error: {e}")
        return f"Error calling Mistral API: {e}"

def _create_prompt(move_data, board_before_move, move_type):
    """
    Creates a detailed prompt for the LLM to analyze a single move.
    """
    turn = "White" if board_before_move.turn == chess.WHITE else "Black"
    
    # Standardizing motifs helps your future Evolution Algorithm know exactly what to generate.
    allowed_motifs = (
        "Pin, Fork, Skewer, Hanging Piece, Back Rank Weakness, Discovered Attack, "
        "Trapped Piece, Overloaded Piece, Deflection, Decoy, Mating Net, "
        "Promotion, Positional Error, Blundered Checkmate, Opening Theory"
    )

    if move_type == "mistake":
        explanation_structure = """Your explanation must include these three sections in markdown:

### **1. The Mistake:**
Explain why the player's move was a blunder. What did it allow the opponent to do? Focus on the core tactical or positional error.

### **2. The Better Move:**
Explain why the engine's recommended move is superior. What advantages does it provide? How does it avoid the mistake?

### **3. Key Takeaway:**
Provide one clear lesson the player can learn from this mistake. Format it in italics like: *"Always check if..."*
"""
    else: # for "best_move"
        explanation_structure = """Your explanation must include these three sections in markdown:

### **1. The Brilliance:**
Explain why this was an excellent move. What makes it special? Does it win material, create a decisive advantage, or execute a tactical blow?

### **2. The Idea:**
Describe the strategic or tactical concept behind the move. What pattern or principle does it exemplify?

### **3. Key Takeaway:**
Provide one clear lesson about this pattern that the player can apply in future games. Format it in italics like: *"Look for opportunities to..."*
"""

    # --- Use .get() for all dictionary access to prevent crashes ---
    prompt = f"""
You are an expert chess coach speaking to a beginner or intermediate player. Analyze this chess move.

**Position Details:**
- Board State (FEN): {board_before_move.fen()}
- Player to Move: {turn} 
- Move Played: {move_data.get('move', 'N/A')} (Classification: {move_data.get('classification', 'N/A')})
- Engine's Best Move: {move_data.get('best_move', 'N/A')}
- Centipawn Loss: {move_data.get('eval_diff', 'N/A')}

**Task 1 - Choose the Motif:**
Select ONE tactical/strategic pattern from this list: [{allowed_motifs}]

**Task 2 - Write the Explanation:**
{explanation_structure}

**CRITICAL - JSON Format Required:**
Respond with ONLY this JSON structure (no markdown code blocks, no extra text):

{{
    "motif": "Your chosen motif here",
    "explanation": "Your complete 3-section analysis with markdown formatting here"
}}

The explanation field must contain all three sections with markdown headers as shown above.
Respond with ONLY the JSON:
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

def _parse_llm_response(raw_response):
    """
    Parses the LLM response to extract the motif and explanation separately.
    First tries to parse as JSON, then falls back to text parsing.
    """
    motif = None
    explanation = raw_response
    
    # Define allowed motifs for fallback detection
    allowed_motifs = [
        "Pin", "Fork", "Skewer", "Hanging Piece", "Back Rank Weakness", 
        "Discovered Attack", "Trapped Piece", "Overloaded Piece", 
        "Deflection", "Decoy", "Mating Net", "Promotion", 
        "Positional Error", "Blundered Checkmate", "Opening Theory"
    ]
    
    # Clean up response - remove markdown code blocks if present
    cleaned_response = raw_response.strip()
    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]  # Remove ```json
    elif cleaned_response.startswith("```"):
        cleaned_response = cleaned_response[3:]  # Remove ```
    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]  # Remove trailing ```
    cleaned_response = cleaned_response.strip()
    
    try:
        # First, try to parse as JSON
        parsed_json = json.loads(cleaned_response)
        if isinstance(parsed_json, dict):
            motif = parsed_json.get('motif')
            explanation = parsed_json.get('explanation', raw_response)
            if motif and explanation:
                logger.info(f"Successfully parsed JSON response with motif: {motif}")
                return motif, explanation
    except json.JSONDecodeError as e:
        logger.warning(f"Response is not valid JSON ({e}), trying text parsing...")
    
    try:
        # Fallback: Try text format with MOTIF: and EXPLANATION: labels
        lines = raw_response.split('\n')
        motif_line = None
        explanation_start = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("MOTIF:"):
                motif_line = stripped.replace("MOTIF:", "").strip()
            elif stripped.startswith("EXPLANATION:"):
                explanation_start = i
                break
        
        if motif_line:
            motif = motif_line
        
        if explanation_start is not None:
            explanation = '\n'.join(lines[explanation_start:]).replace("EXPLANATION:", "").strip()
        
        # If motif wasn't found in proper format, try to extract from content
        if not motif:
            logger.warning("MOTIF: label not found in LLM response. Attempting fallback extraction.")
            lower_response = raw_response.lower()
            for allowed_motif in allowed_motifs:
                if allowed_motif.lower() in lower_response:
                    motif = allowed_motif
                    logger.info(f"Extracted motif via fallback: {motif}")
                    break
            
            if not motif:
                motif = "Tactical Error"
                logger.warning(f"No recognizable motif found. Using default: {motif}")
        
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {e}. Using default motif.")
        motif = "Tactical Error"
    
    return motif, explanation

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
        raw_response = _call_mistral_api(prompt, api_key, use_json_mode=True) 
        
        motif, explanation = _parse_llm_response(raw_response)

        sanitized_move_info = mistake_data.copy()
        
        summary['mistakes'].append({
            "move_info": sanitized_move_info,
            "motif": motif,
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
        raw_response = _call_mistral_api(prompt, api_key, use_json_mode=True)
        
        motif, explanation = _parse_llm_response(raw_response)

        sanitized_move_info = best_move_data.copy()

        summary['best_moves'].append({
            "move_info": sanitized_move_info,
            "motif": motif,
            "explanation": explanation
        })
        
        time.sleep(1)  # <-- 4. Add a 1-second delay *after* each API call

    return summary