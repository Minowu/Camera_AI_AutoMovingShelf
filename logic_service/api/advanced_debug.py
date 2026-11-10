from typing import Dict, Any, List
import time
from shared.logger import get_logger
from fastapi import APIRouter, Request
from services.POS_manager import pos_manager

logger = get_logger("logic_service")
router = APIRouter()

@router.post("/unblock_point")
async def receive_data(payload: Dict):
    try:
        await pos_manager.un_block_point(payload)
        return {"status": "success", "message": "Data updated"}
    except Exception as e:
        logger.error(f"Error updating state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/block_point")
async def receive_data(payload: Dict):
    try:
        await pos_manager.block_point(payload)
        return {"status": "success", "message": "Data updated"}
    except Exception as e:
        logger.error(f"Error updating state: {e}")
        raise HTTPException(status_code=500, detail=str(e))