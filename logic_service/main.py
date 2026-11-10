from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from shared.logger import setup_logger
from services.POS_manager import pos_manager
from services.SSE_manager import sse_manager
from services.Robot_manager import robot_service
from core.config import settings
import sys
import os
from api import receive_data, sse_connection, advanced_debug
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = setup_logger("logic_service", "INFO", "logic")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    try:
        logger.info("Initializing Logic Services...")
        await pos_manager.start()
        logger.info("Successfull running Position Manager")
        robot_service.load_zone_configs()
        robot_service.load_robot_configs()

    except Exception as e:
        logger.error(f"Error initializing Logic Services: {e}")
        raise

    yield

    #Stop
    await pos_manager.stop()
    await sse_manager.disconnect_all()
    logger.info("Shutting down all services!")

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

app.include_router(receive_data.router, tags=["API receive data"])
app.include_router(sse_connection.router, tags=["API for SSE"])
app.include_router(advanced_debug.router, tags=["API for Debugging"])

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