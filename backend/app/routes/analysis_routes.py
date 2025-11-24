from fastapi import (
    APIRouter, 
    UploadFile, 
    File, 
    HTTPException, 
    Path, 
    status,
    Depends,
    Request
)
from motor.motor_asyncio import AsyncIOMotorCollection
import hashlib

# Import your helper functions, models, and repo
from ..repos import analyze_repo
from ..core.celery_app import celery_app
from ..models.analysis_model import (
    AnalysisCreateResponse, 
    AnalysisStatusResponse, 
    validate_object_id
)
from ..core.logger import logger

# --- CREATE ROUTER ---
router = APIRouter()

# --- DEPENDENCY INJECTION ---
def get_analysis_collection(request: Request) -> AsyncIOMotorCollection:
    """
    A dependency that gets the database collection 
    from the app's state (which was set in main.py).
    """
    return request.app.state.analysis_collection

# --- API ENDPOINTS ---

@router.post(
    "/", 
    response_model=AnalysisCreateResponse, 
    status_code=status.HTTP_202_ACCEPTED
)
async def create_analysis_job(
    file: UploadFile = File(...),
    collection: AsyncIOMotorCollection = Depends(get_analysis_collection)
):
    """
    1. The "Analyze" Endpoint (Asynchronous)
    
    Accepts a PGN file, creates a "PENDING" job in MongoDB,
    starts the background Celery task, and returns the job ID.
    
    Optimization: Caches analysis by PGN content hash to avoid reprocessing.
    """
    if not file.filename.endswith(".pgn"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid file type. Please upload a .pgn file."
        )
        
    pgn_string = (await file.read()).decode("utf-8")
    
    # Calculate hash of PGN content for caching
    pgn_hash = hashlib.sha256(pgn_string.encode()).hexdigest()
    
    # Check if this exact PGN has been analyzed before
    cached_analysis = await collection.find_one({
        "pgn_hash": pgn_hash,
        "status": "COMPLETED"
    })
    
    if cached_analysis:
        logger.info(f"Cache hit - returning existing analysis for hash: {pgn_hash[:16]}...")
        return AnalysisCreateResponse(
            analysis_id=str(cached_analysis["_id"]),
            status="COMPLETED",
            message="Analysis already exists. Returning cached result."
        )
    
    # No cache hit - create new job
    logger.info(f"Cache miss - creating new analysis job for hash: {pgn_hash[:16]}...")
    analysis_id = await analyze_repo.create_job_async(collection, pgn_hash=pgn_hash)

    # CALL THE TASK BY ITS NAME
    celery_app.send_task(
        "backend.app.tasks.celery_worker.run_chess_analysis",
        args=[analysis_id, pgn_string]
    )
    logger.info(f"Analysis job {analysis_id} queued for processing")
    
    return AnalysisCreateResponse(
        analysis_id=analysis_id, 
        status="PENDING",
        message="Analysis job accepted and is being processed in the background."
    )

@router.get(
    "/{analysis_id}/status", 
    response_model=AnalysisStatusResponse
)
async def get_analysis_status(
    analysis_id: str = Path(..., title="The ID of the analysis job"),
    collection: AsyncIOMotorCollection = Depends(get_analysis_collection)
):
    """
    2. The "Status" Endpoint
    
    Checks the current status of the analysis job.
    """
    try:
        # USE THE REPO
        job = await analyze_repo.get_job_status_async(collection, analysis_id)
    except ValueError as e: # From _validate_object_id
        raise HTTPException(status_code=400, detail=str(e))
        
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return AnalysisStatusResponse(
        status=job["status"],
        error=job.get("error")
    )

@router.get("/{analysis_id}")
async def get_analysis_result(
    analysis_id: str = Path(..., title="The ID of the analysis job"),
    collection: AsyncIOMotorCollection = Depends(get_analysis_collection)
):
    """
    3. The "Results" Endpoint
    
    Fetches the full analysis data once the job is "COMPLETED".
    """
    try:
        # USE THE REPO
        job = await analyze_repo.get_job_by_id_async(collection, analysis_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    status = job["status"]
    
    if status == "COMPLETED":
        # Return the full JSON object
        return job["result"]
    elif status == "FAILED":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Analysis failed and no result is available. Error: {job.get('error')}"
        )
    else: # PENDING or PROCESSING
        # Return a 200 OK but with a status payload, making it friendlier for clients
        # that only check for response.ok (status 200-299).
        return {
            "status": status,
            "message": "Analysis is not yet complete. Please poll the /status endpoint.",
            "result": None
        }