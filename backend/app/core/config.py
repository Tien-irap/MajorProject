# core/config.py
import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

class Settings:
    # MongoDB
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    DB_NAME: str = os.getenv("DB_NAME", "chess_analysis_db")
    
    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # External Tools
    STOCKFISH_PATH: str = os.getenv("STOCKFISH_PATH", r"C:\Users\lenovo\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe")
    GLOBAL_MISTAKES_CSV: str = os.getenv("GLOBAL_MISTAKES_CSV", "global_mistake_features.csv")
    
    # API Keys
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    
    # Logging
    LOGGER: int = int(os.getenv("LOGGER", "20"))  # 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY")
    if not MISTRAL_API_KEY:
        print("WARNING: MISTRAL_API_KEY is not set. LLM features will be disabled.")

settings = Settings()