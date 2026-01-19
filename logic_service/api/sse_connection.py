from typing import Dict, Any, List
import time
from shared.logger import get_logger
from fastapi import APIRouter, Request
from services.SSE_manager import sse_manager
from fastapi.responses import StreamingResponse
import asyncio

logger = get_logger("logic_service")
router = APIRouter()

@router.get("/sse/group")
async def sse_endpoint(request: Request, group_id: int = None):
    # 1. Đăng ký nhận tin nhắn
    queue = await sse_manager.subscribe({"group_id": group_id})

    async def event_generator():
        try:
            while True:
                # Kiểm tra nếu trình duyệt đóng kết nối
                if await request.is_disconnected():
                    break

                # Đợi tin nhắn mới từ Manager
                try:
                    # Timeout để loop có thể check is_disconnected() định kỳ
                    data = await asyncio.wait_for(queue.get(), timeout=10.0)
                    yield data
                except asyncio.TimeoutError:
                    # Gửi comment để giữ kết nối (keep-alive)
                    yield ": keep-alive\n\n"

        except asyncio.CancelledError:
            pass
        finally:
            sse_manager.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no" # Quan trọng nếu dùng Nginx
        }
    )
