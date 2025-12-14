import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env():
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key:
        print(f"MISTRAL_API_KEY is set: {api_key}")
    else:
        print("MISTRAL_API_KEY is not set. Please check your .env file.")

if __name__ == "__main__":
    check_env()