from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware  # <-- 1. Import the middleware

# Import your core app elements
from backend.app.core.database import db_async
from backend.app.routes import analysis_routes

# --- LIFESPAN (Startup & Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    Connects to the database on startup and disconnects on shutdown.
    """
    print("FastAPI: Starting up...")
    db_async.connect()
    
    # This is where we attach the database collection to the app's state
    # so the routers can access it via dependency injection.
    app.state.analysis_collection = db_async.db.analyses
    print("FastAPI: Database connection established.")
    
    yield  # --- Application is now running ---
    
    print("FastAPI: Shutting down...")
    db_async.close()
    print("FastAPI: Database connection closed.")

# --- CREATE THE MAIN APP INSTANCE ---
app = FastAPI(
    title="Chess Analysis API",
    lifespan=lifespan
)

# --- 2. ADD CORS MIDDLEWARE ---
# This is the fix. It must be added *after* app is created
# and *before* you include your routers.
origins = [
    "http://localhost:8080",  # Your React app's address from the screenshot
    "http://localhost",       # In case you ever serve from root
    "http://localhost:5173",  # A common port for Vite/React, just in case
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # List of origins that are allowed
    allow_credentials=True,    # Allow cookies (if you use them)
    allow_methods=["*"],         # Allow all HTTP methods
    allow_headers=["*"],         # Allow all headers
)

# --- INCLUDE ROUTERS ---
# All of your analysis endpoints are now handled by this router.
app.include_router(
    analysis_routes.router,
    prefix="/analysis",  # This adds /analysis to all routes in that file
    tags=["Analysis"]     # Groups them nicely in the /docs
)

# A simple root endpoint to check if the API is running
@app.get("/", tags=["Root"])
async def read_root():
    return {"status": "Chess Analysis API is running"}