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
    STOCKFISH_PATH: str = os.getenv("STOCKFISH_PATH", "./stockfish/stockfish-macos-m1-apple-silicon")
    GLOBAL_MISTAKES_CSV: str = os.getenv("GLOBAL_MISTAKES_CSV", "global_mistake_features.csv")
    
    # API Keys
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    
    # Logging
    LOGGER: int = int(os.getenv("LOGGER", "20"))  # 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR

settings = Settings()