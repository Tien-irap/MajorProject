# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Path, status
# ... (other imports)
from contextlib import asynccontextmanager

from backend.app.core.database import db_async
from backend.app.tasks.celery_worker import run_chess_analysis
from motor.motor_asyncio import AsyncIOMotorCollection
from backend.app.core.celery_app import celery_app

# --- IMPORT THE REPOSITORY ---
from backend.app.repos import analyze_repo

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_async.connect()
    # --- Get the specific collection for the repo ---
    app.state.analysis_collection = db_async.db.analyses
    yield
    db_async.close()

app = FastAPI(title="Chess Analysis API", lifespan=lifespan)

# ... (Keep your Pydantic models) ...

# --- Helper for getting the collection ---
def get_analysis_collection() -> AsyncIOMotorCollection:
    return app.state.analysis_collection

# --- API Endpoints (Now much cleaner!) ---

@app.post("/analysis/", status_code=status.HTTP_202_ACCEPTED)
async def create_analysis_job(file: UploadFile = File(...)):
    
    pgn_string = (await file.read()).decode("utf-8")
    
    collection = app.state.analysis_collection
    analysis_id = await analyze_repo.create_job_async(collection)

    # --- CALL THE TASK BY ITS NAME ---
    # This sends the task without importing the celery_worker.py file,
    # preventing the API server from training the model.
    celery_app.send_task(
        "backend.app.tasks.celery_worker.run_chess_analysis",
        args=[analysis_id, pgn_string]
    )
    
    return {"analysis_id": analysis_id, "status": "PENDING", "message": "Job accepted"}

@app.get("/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    try:
        # USE THE REPO
        collection = get_analysis_collection()
        job = await analyze_repo.get_job_status_async(collection, analysis_id)
    except ValueError as e: # From _validate_object_id
        raise HTTPException(status_code=400, detail=str(e))
        
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": job["status"], "error": job.get("error")}

@app.get("/analysis/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    try:
        # USE THE REPO
        collection = get_analysis_collection()
        job = await analyze_repo.get_job_by_id_async(collection, analysis_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job["status"] == "COMPLETED":
        return job["result"]
    # ... (rest of your logic for FAILED/PENDING) ...