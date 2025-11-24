from typing import List
from backend.app.core.database import db_async
from backend.app.models.puzzle_models import PuzzleDB, UserTrainingHistory
from backend.app.core.logger import logger

class TrainingRepository:
    """
    Handles database operations for Training Puzzles and User History.
    Accesses the 'puzzles' and 'training_history' collections.
    """
    
    @property
    def db(self):
        """
        Property to ensure we always get the current database connection.
        This prevents issues if the connection is established after repo instantiation.
        """
        if db_async.db is None:
            raise RuntimeError("Database not connected. Ensure db_async.connect() was called during startup.")
        return db_async.db

    async def create_puzzles_bulk(self, puzzles: List[PuzzleDB]) -> List[str]:
        """
        Saves a batch of generated puzzles to MongoDB.
        """
        if not puzzles:
            logger.warning("No puzzles to save")
            return []

        logger.debug(f"Saving {len(puzzles)} puzzles to database")
        # Convert Pydantic models to dicts for MongoDB
        # by_alias=True ensures '_id' is used instead of 'id'
        puzzles_dict = [p.model_dump(by_alias=True) for p in puzzles]
        
        result = await self.db["puzzles"].insert_many(puzzles_dict)
        logger.info(f"Successfully saved {len(result.inserted_ids)} puzzles")
        
        return [str(id) for id in result.inserted_ids]

    async def record_attempt(self, attempt: UserTrainingHistory) -> str:
        """
        Records a user's attempt (Success/Fail/Time) for RL processing.
        """
        logger.debug(f"Recording attempt for puzzle {attempt.puzzle_id} by user {attempt.user_id}")
        attempt_dict = attempt.model_dump(by_alias=True)
        result = await self.db["training_history"].insert_one(attempt_dict)
        logger.info(f"Training attempt recorded with ID: {result.inserted_id}")
        return str(result.inserted_id)

    async def get_puzzle_by_id(self, puzzle_id: str) -> dict:
        """
        Optional: Fetch a specific puzzle (useful for validation).
        """
        return await self.db["puzzles"].find_one({"_id": puzzle_id})

# Export a singleton instance if preferred, or instantiate in Router
training_repo = TrainingRepository()