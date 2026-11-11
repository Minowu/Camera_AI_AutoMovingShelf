from shared.logger import get_logger
import asyncio
from typing import Dict, Any
import asyncio
import contextlib
from datetime import datetime
from services.POS_manager import pos_manager

logger = get_logger("logic_service")

class TaskService:
    def __init__(self) -> None:
        self.tracking_task = {}
        self._log_spam = {}
        self._reverse_index = {}

    async def track_for_task(self, order_id, data):
        self.tracking_task[order_id] = data
    
    async def unlock_task(self, payload):
        task_data = {
            "order_id": payload.get("orderId"),
            "device_code": payload.get("deviceCode"),
            "model_process_code": payload.get("modelProcessCode"),
            "device_num": payload.get("deviceNum"),
            "qr_code": payload.get("qrCode"),
            "shelf_number": payload.get("shelfNumber"),
            "status": payload.get("status"),
            "updated_at": datetime.now().isoformat(),
        }

        order_id = task_data["order_id"]

        if order_id in self.tracking_task:
            first_str = order_id[0]

            if task_data["status"] in (21, 3) and first_str == "4":
                await pos_manager.un_block_point(self.tracking_task[order_id]["position"])
                self.tracking_task.pop(order_id, None)

            # Đơn Single chuyển 2 điểm của Hà Nam (prefix S-): Mở khóa cùng lúc cả 2 điểm khi xong (3) hoặc hủy (4, 5)
            if task_data["status"] in (3, 4, 5) and first_str == "S":
                await pos_manager.un_block_point(self.tracking_task[order_id]["position"])
                self.tracking_task.pop(order_id, None)

            # Đơn trả kệ rỗng (X-) và Đơn 1 nguồn nhiều đích (O-) của Hà Nam:
            # Mở khóa khi robot vừa nhấc kệ xong (subTaskSeq=2, subTaskStatus=2) hoặc khi xong/hủy (3, 4, 5)
            if first_str in ("X", "O"):
                sub_status = str(payload.get("subTaskStatus"))
                sub_seq = str(payload.get("subTaskSeq"))
                if (sub_status == "2" and sub_seq == "2") or task_data["status"] in (3, 4, 5):
                    await pos_manager.un_block_point(self.tracking_task[order_id]["position"])
                    self.tracking_task.pop(order_id, None)

            if task_data["status"] in (23, 3) and first_str == "2":
                await pos_manager.un_block_point(self.tracking_task[order_id]["position"])
                self.tracking_task.pop(order_id, None)

            if task_data["status"] in (20, 3) and first_str == "3":
                data = self.tracking_task[order_id]
                data["order_id"] = order_id
                await pos_manager.clear_monitor(data)


task_service = TaskService()
    