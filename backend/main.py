import uvicorn
import shutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from src.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Candidate Evaluation API",
    description="AI-powered candidate evaluation system with CV and video processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["candidate-evaluation"])

@app.get("/")
async def root():
    """Serve the frontend"""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {
        "message": "Candidate Evaluation API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def root_health_check():
    """Root level health check endpoint for Railway"""
    return {
        "status": "healthy", 
        "message": "App Reviewer Backend is running",
        "ffmpeg_available": shutil.which("ffmpeg") is not None,
        "version": "1.0.0"
    }

# Catch-all route for SPA routing
@app.get("/{path:path}")
async def serve_spa(path: str):
    """Serve SPA for client-side routing"""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"error": "Frontend not found"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )