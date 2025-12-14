import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Ensure backend/ is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.app.api.api_v1.api import api_router
# IMPORT THE SHARED DB INSTANCE
from backend.app.core.database import db_async 

# --- LIFESPAN (New way to handle startup/shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ FastAPI: Starting up...")
    # 1. Use the shared connection logic
    db_async.connect()
    yield
    print("🛑 FastAPI: Shutting down...")
    db_async.close()

app = FastAPI(title="Chess Analysis API", lifespan=lifespan)

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:8080",
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"status": "Chess Analysis API is running"}
