# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from . import api
except ImportError:
    # If relative import fails, try absolute import
    from backend.app import api

app = FastAPI(title="Chess Tutor API")

# CORS configuration for React frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Chess Tutor API is running! Go to /docs for API documentation."}