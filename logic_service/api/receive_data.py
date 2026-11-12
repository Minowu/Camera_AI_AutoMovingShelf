from typing import Dict, Any, List
import time
from shared.logger import get_logger
from fastapi import APIRouter, Request
from services.POS_manager import pos_manager
from services.Task_manager import task_service
from services.Robot_manager import robot_service

logger = get_logger("logic_service")
router = APIRouter()

@router.post("/ai-data")
async def receive_data(payload: Dict):
    try:
        # Ghi log rõ ràng những điểm đang có hàng
        hang_list = [k for k, v in payload.items() if isinstance(v, dict) and v.get("label") == "hang"]
        if hang_list:
            logger.info(f"📥 [NHẬN TÍN HIỆU AI] {len(payload)} ô | Đang CÓ HÀNG tại: {hang_list}")
        await pos_manager.update_state(payload)
        return {"status": "success", "message": "Data updated", "active_hang": len(hang_list)}
    except Exception as e:
        logger.error(f"Error updating state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-ai")
async def active_proc(request: Request):
    try:
        payload = await request.json()
        response = await pos_manager.active_request(payload)
        return response
    except Exception as e:
        logger.error(f"Error updating state: {e}")
        return {"status": "error", "data": str(e)}

@router.post("/task-status")
async def receive_task_status(request: Request):
    payload = await request.json()
    logger.info(f"📥 [NHẬN TASK STATUS] orderId={payload.get('orderId')} | status={payload.get('status')} | subTaskSeq={payload.get('subTaskSeq')} | subTaskStatus={payload.get('subTaskStatus')}")
    data = await task_service.unlock_task(payload)

    return {"status": "success", "data": data}

@router.post("/robot-zone")
async def receive_task_status(request: Request):
    payloads = await request.json()
    if not isinstance(payloads, list):
        payloads = [payloads]

    for payload in payloads:
        try:
            await robot_service.receive_data(payload)
        except Exception as e:
            logger.error(f"Error updating state: {e}")
    return {"status": "success", "data": payloads}