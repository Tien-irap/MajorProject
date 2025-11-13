# backend/app/tasks/celery_worker.py

import time
import os
import pandas as pd
from bson import ObjectId

# --- IMPORTS ---
from ..core.celery_app import celery_app
from ..core.database import get_sync_db_connection
from ..core.config import settings
from ..repos import analyze_repo
from ..services.analyze_services import perform_full_game_analysis
from ..services.global_analyzer import GlobalAnalyzer

# --- SETUP WORKER ENVIRONMENT (Global Scope) ---
# This part is OK to run at startup. It just loads a file, not a network connection.
print("CELERY: Initializing GlobalAnalyzer...")
global_analyzer_instance = GlobalAnalyzer(n_clusters=4)

if not os.path.exists(settings.GLOBAL_MISTAKES_CSV):
    print(f"⚠️ CRITICAL: {settings.GLOBAL_MISTAKES_CSV} not found.")
else:
    try:
        df = pd.read_csv(settings.GLOBAL_MISTAKES_CSV)
        if not df.empty:
            global_analyzer_instance.train_global_model(df)
            print("✅ CELERY: GlobalAnalyzer trained.")
        else:
            print(f"⚠️ WARNING: {settings.GLOBAL_MISTAKES_CSV} is empty.")
    except Exception as e:
        print(f"🔥 CELERY: Model training failed: {e}")


# --- THE TASK DEFINITION ---
@celery_app.task(bind=True)  # Add bind=True
def run_chess_analysis(self, analysis_id: str, pgn_string: str):
    """
    This is the main Celery task that runs in the background.
    """
    
    # --- SOLUTION: Connect INSIDE the task ---
    db, mongo_client = get_sync_db_connection()
    
    if db is None:
        print("CELERY: No DB connection. Aborting task.")
        # We can't even update the DB to say we failed, so just return.
        return {"status": "FAILED", "error": "Worker DB connection failed"}
        
    # Get the collection *inside* the task
    analyses_collection = db.analyses
    # ----------------------------------------
    
    print(f"CELERY: Processing job {analysis_id}")
    
    try:
        # USE THE REPO
        analyze_repo.update_job_status_sync(analyses_collection, analysis_id, "PROCESSING")
        
        start_time = time.time()
        
        # Run Analysis
        result_data = perform_full_game_analysis(
            pgn_string, 
            global_analyzer_instance
        )
        
        duration = time.time() - start_time

        # USE THE REPO
        analyze_repo.set_job_completed_sync(
            analyses_collection,
            analysis_id,
            result_data,
            duration
        )
        return {"status": "COMPLETED"}

    except Exception as e:
        print(f"ERROR in Job {analysis_id}: {e}")
        # USE THE REPO
        analyze_repo.set_job_failed_sync(
            analyses_collection, 
            analysis_id, 
            str(e)
        )
        return {"status": "FAILED", "error": str(e)}
    
    finally:
        # --- IMPORTANT: Always close the connection ---
        if mongo_client:
            mongo_client.close()
            print(f"CELERY: Closed DB connection for job {analysis_id}")