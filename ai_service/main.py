from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from shared.logger import setup_logger
from core.config import settings
from core.database import connect_to_mongo, close_mongo_connection
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.camera_orchestrator_service import CameraOrchestratorService

logger = setup_logger("camera_ai_service", "INFO", "ai")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting CameraAI Service...")
    ai_service = CameraOrchestratorService(settings.group_id, settings.num_process, settings.max_retry_attempts, settings.weight_path, settings.target_fps)

    try:
        logger.info("Initializing Camera Detector...")
        await connect_to_mongo(settings.mongo_url, settings.mongo_db)
        logger.info("Database connected")
        await ai_service.start()
        logger.info("AI service is running on")

    except Exception as e:
        logger.error(f"Error initializing Camera Detector: {e}")
        raise

    yield

    logger.info("Shutting down Camera Detector...")
    await ai_service.stop()
    logger.info("AI_service stopped")
    await close_mongo_connection()

# Create FastAPI app
app = FastAPI(
    title="Camera AI Service",
    description="AI-powered camera service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Camera AI Service API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug
    )