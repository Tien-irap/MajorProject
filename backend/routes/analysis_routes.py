# --- API Endpoints ---
from fastapi import APIRouter, UploadFile, File, HTTPException, Path, status
from fastapi.responses import JSONResponse

import app

from backend.app.models.analysis_model import AnalysisCreateResponse, AnalysisStatusResponse, validate_object_id
from backend.app.main import analyses_collection
from backend.app.tasks.celery_worker import run_chess_analysis

@app.post(
    "/analysis/", 
    response_model=AnalysisCreateResponse, 
    status_code=status.HTTP_202_ACCEPTED
)
async def create_analysis_job(file: UploadFile = File(...)):
    """
    1. The "Analyze" Endpoint (Asynchronous)
    
    Accepts a PGN file, creates a "PENDING" job in MongoDB,
    starts the background Celery task, and returns the job ID.
    """
    if not file.filename.endswith(".pgn"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid file type. Please upload a .pgn file."
        )
    
    # Read PGN file content
    pgn_content_bytes = await file.read()
    try:
        pgn_string = pgn_content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Could not decode file. Ensure it's UTF-8 encoded."
        )

    # Create new document in MongoDB
    new_job = {"status": "PENDING", "result": None, "error": None}
    result = await analyses_collection.insert_one(new_job)
    analysis_id = str(result.inserted_id)

    # Start the background Celery task
    # .delay() sends the task to the Redis queue
    run_chess_analysis.delay(analysis_id, pgn_string)

    # Respond immediately with 202 Accepted
    return AnalysisCreateResponse(
        analysis_id=analysis_id, 
        status="PENDING",
        message="Analysis job accepted and is being processed in the background."
    )


@app.get(
    "/analysis/{analysis_id}/status", 
    response_model=AnalysisStatusResponse
)
async def get_analysis_status(
    analysis_id: str = Path(..., title="The ID of the analysis job")
):
    """
    2. The "Status" Endpoint
    
    Your React app will call this endpoint every few seconds
    to check if the analysis is complete.
    """
    oid = validate_object_id(analysis_id)
    
    job = await analyses_collection.find_one(
        {"_id": oid},
        projection={"status": 1, "error": 1} # Only get the fields we need
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Analysis job not found"
        )
    
    return AnalysisStatusResponse(
        status=job["status"],
        error=job.get("error")
    )


@app.get("/analysis/{analysis_id}")
async def get_analysis_result(
    analysis_id: str = Path(..., title="The ID of the analysis job")
):
    """
    3. The "Results" Endpoint
    
    Once the status is "COMPLETED", your React app will call this
    to get the full analysis data.
    """
    oid = validate_object_id(analysis_id)
    
    job = await analyses_collection.find_one({"_id": oid})
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Analysis job not found"
        )
    
    status = job["status"]
    
    if status == "COMPLETED":
        # Returns the full JSON object containing the results
        return job["result"]
    elif status == "FAILED":
        # Return a 404 or 500 to indicate the result isn't available
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Analysis failed and no result is available. Error: {job.get('error')}"
        )
    else: # PENDING or PROCESSING
        # Return 202 Accepted to indicate it's not ready yet
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "status": status,
                "message": "Analysis is not yet complete. Please poll /status endpoint."
            }
        )