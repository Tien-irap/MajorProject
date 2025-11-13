import requests
import os
import json
from dotenv import load_dotenv

# --- Configuration ---
API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL = "mistral-small-latest"

# Load environment variables from .env file
load_dotenv()

def _create_puzzle_prompt(weakness_description):
    """Creates a prompt for the LLM to generate a chess puzzle based on a weakness."""
    prompt = f"""
    You are a chess puzzle creator. Your task is to generate a single chess puzzle based on a player's specific weakness.

    **Player's Weakness:** "{weakness_description}"

    **Your Instructions:**
    1.  Create a chess position in FEN (Forsyth-Edwards Notation) that clearly demonstrates this weakness. For example, if the weakness is "missed fork," the puzzle position should contain a winning fork. The turn to move in the FEN should be for the player who can execute the winning move.
    2.  Provide the single best move (the solution) in UCI format (e.g., "e4f5").
    3.  Provide a brief explanation of why the solution is the best move.
    4.  Provide three plausible but incorrect "distractor" moves, also in UCI format. These should be moves a player might mistakenly play.

    **Output Format:**
    Return your response as a single, valid JSON object. Do not include any text outside of the JSON object.

    **JSON Structure Example:**
    {{
      "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
      "solution_uci": "f3e5",
      "explanation": "This move, Nxe5, forks the queen and the rook, winning material.",
      "distractors": ["f3g5", "d2d4", "f1c4"]
    }}
    """
    return prompt.strip()

def generate_puzzle_from_weakness(weakness_description):
    """
    Uses Mistral LLM to generate a puzzle (FEN, solution, explanation) for a given weakness.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        return {"error": "Mistral API key not found."}

    prompt = _create_puzzle_prompt(weakness_description)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=45)
        response.raise_for_status()
        # The response should be a JSON string, so we parse it.
        puzzle_data = json.loads(response.json()['choices'][0]['message']['content'])
        return puzzle_data
    except requests.exceptions.RequestException as e:
        return {"error": f"API call failed: {e}"}
    except (json.JSONDecodeError, KeyError) as e:
        return {"error": f"Failed to parse LLM response: {e}. Response: {response.text}"}