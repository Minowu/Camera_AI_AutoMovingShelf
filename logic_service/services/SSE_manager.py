import asyncio
import json
from typing import Dict, Set, Any
from fastapi import Request
from fastapi.responses import StreamingResponse

class RawSSEManager:
    def __init__(self):
        self.active_queues: Dict[asyncio.Queue, dict] = {} # Lưu queue và metadata

    async def subscribe(self, metadata: dict):
        queue = asyncio.Queue()
        self.active_queues[queue] = metadata
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self.active_queues:
            del self.active_queues[queue]

    async def broadcast(self, data: Any, event: str = None, group_id: int = None):
        # Định dạng chuẩn SSE: "event: ...\ndata: ...\n\n"
        msg = f"data: {json.dumps(data)}\n\n"
        if event:
            msg = f"event: {event}\n{msg}"

        for queue, meta in self.active_queues.items():
            # Check lọc theo group_id nếu cần
            if group_id is not None and meta.get("group_id") != group_id:
                continue
            try:
                queue.put_nowait(msg)
            except Exception:
                pass

    async def disconnect_all(self):
        """Gửi tín hiệu None để đóng tất cả các stream đang chạy"""
        if not self.active_queues:
            return
        
        # Tạo danh sách các queue để tránh lỗi 'dictionary changed size during iteration'
        queues = list(self.active_queues.keys())
        for queue in queues:
            try:
                # Gửi None làm tín hiệu dừng
                await queue.put(None)
            except Exception:
                pass
        self.active_queues.clear()

sse_manager = RawSSEManager()