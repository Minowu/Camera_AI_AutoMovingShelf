from datetime import datetime, timezone
from shared.logger import get_logger
import asyncio
from typing import Dict, Any, Optional, List, Tuple
import contextlib
import json
import asyncio
import os
import re
import sys
import time
import importlib
from core.config import settings

logger = get_logger("logic_service")

class Position_Manager:
    def __init__(self, time_recognition) -> None:
        self._consumer_task: Optional[asyncio.Task] = None
        self._position_state: Dict[str, Any] = {}
        self.data_configs = {}
        self.mapping = {}
        self._pending_state = {}
        self._registry = {}
        self._last_check_time = {}
        self.time_recognition = time_recognition
        self._failed_points = set()
        self._dispatching = set()

    async def start(self) -> None:
        self.load_configs()
        if self._consumer_task is None:
            self._consumer_task = asyncio.create_task(self._consumer_loop())

    def load_configs(self):
        config_dir = "config/map_config"
        if not os.path.exists(config_dir):
            logger.error(f"The config path does not exist")
            return
            
        for filename in os.listdir(config_dir):
            # Chỉ kiểm tra file có đuôi .json
            if filename.lower().endswith(".json"):
                path = os.path.join(config_dir, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                        
                        if content:
                            # Lưu toàn bộ nội dung file vào data
                            self.data_configs[filename] = content
                            
                            # Mapping từng key trong file đó để biết nó thuộc về file nào (logic nào)
                            for key in content.keys():
                                self.mapping[key] = filename

                except Exception as e:
                    print(f"[ERROR] Could not load {filename}: {e}")
            
        logger.info(f"Loaded all config files")

    async def stop(self) -> None:
        if self._consumer_task:
            self._consumer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._consumer_task
            self._consumer_task = None

    async def mark_failed(self, pos_id):
        self._failed_points.add(pos_id)
        logger.error(f"[POS_manager] Điểm {pos_id} bị đánh dấu thất bại (failed), tạm dừng dispatch")

    async def update_state(self, data) -> None:
        now = time.time()

        for pos_id, info in data.items():
            new_label = info.get("label")
            group_id = info.get("group_id")
            current_confirmed = self._position_state.get(pos_id, {})
            
            if current_confirmed.get("label") == "block":
                continue

            if new_label == current_confirmed.get("label"):
                self._position_state[pos_id]["ts"] = now
                self._pending_state.pop(pos_id, None)

                # Kiểm tra có trong config thì thực hiện gửi đến đúng logic
                file_name = self.mapping.get(pos_id)
                if file_name and new_label == "hang":
                    if pos_id not in self._failed_points and pos_id not in self._dispatching:
                        self._dispatching.add(pos_id)
                        asyncio.create_task(self.request_service_auto(self.data_configs[file_name][pos_id], pos_id))
                continue

            pending = self._pending_state.get(pos_id)

            if pending and pending["label"] == new_label:
                elapsed = now - pending["start_ts"]
                if elapsed >= self.time_recognition:
                    # Đã đủ 5 giây liên tục -> Xác nhận trạng thái mới
                    self._position_state[pos_id] = {
                        "label": new_label,
                        "group_id": group_id,
                        "ts": now,
                    }
                    self._pending_state.pop(pos_id, None)

            else:
                self._pending_state[pos_id] = {
                    "label": new_label,
                    "start_ts": now
                }

    async def request_service_auto(self, data, pos_id=None):
        try:
            await self.execute_logic(data, 0)
        except Exception as e:
            logger.warning(f"Error: {e}")
        finally:
            if pos_id is not None:
                self._dispatching.discard(pos_id)

    async def execute_logic(self, data, mode):
        try:
            logic_path = data.get('logic_path')
            if not logic_path:
                return

            # 1. Lấy hàm từ file logic (Tự động hot-reload nếu cần)
            process_func = await self.get_logic_func(logic_path, mode)

            if process_func:
                response = await process_func(data) 
                return response
            else:
                logger.warning(f"Function process_auto not found in {logic_path}")
                return None

        except Exception as e:
            logger.error(f"Failed to execute logic {logic_path}: {e}")
            return None

    async def get_logic_func(self, logic_path, mode):
        file_path = os.path.join(".", "logic", f"{logic_path}_logic.py")
        module_name = f"logic.{logic_path}_logic"
        now = time.time()
        
        last_check = self._last_check_time.get(logic_path, 0)

        # Cơ chế Cooldown (Chỉ check ổ đĩa 1 lần mỗi giây)
        if now - last_check > 1.0: 
            self._last_check_time[logic_path] = now
            
            if os.path.exists(file_path): # Kiểm tra file vật lý
                current_mtime = os.path.getmtime(file_path)
                cached_info = self._registry.get(logic_path)

                if not cached_info or current_mtime > cached_info["mtime"]:
                    try:
                        if module_name in sys.modules:
                            # Nếu module đã từng được nạp, ta reload nó
                            module = importlib.reload(sys.modules[module_name])
                            logger.info(f"--- HOT RELOADED: {logic_path} ---")
                        else:
                            # Nếu chưa từng nạp, ta import mới
                            module = importlib.import_module(module_name)
                            logger.info(f"--- LOADED NEW: {logic_path} ---")

                        self._registry[logic_path] = {
                            "module": module,
                            "mtime": current_mtime
                        }
                    except Exception as e:
                        logger.error(f"Error loading logic {logic_path}: {e}")

        # Đoạn này chạy cực nhanh vì nó chỉ lấy từ Dict trong RAM ra
        if logic_path in self._registry:
            # Lấy object module đã lưu trong registry ra và tìm hàm 
            if mode == 0:
                return getattr(self._registry[logic_path]["module"], "process_auto", None)

            if mode == 1:
                return getattr(self._registry[logic_path]["module"], "active_request", None)

            if mode == 2:
                return getattr(self._registry[logic_path]["module"], "handle_clear_monitor", None)
        
        return None

    async def get_state(self, points):
        states = []
        for point in points:
            pos_data = self._position_state.get(point, {})            
            label = pos_data.get("label", None)            
            states.append(label)
        return states

    async def get_group(self, point):
        pos_data = self._position_state.get(point, {})            
        group = pos_data.get("group_id", None)            
        return group

    async def block_point(self, point):
        points = point if isinstance(point, list) else [point]
        
        for p in points:
            pos_data = self._position_state.get(p)
            if pos_data:
                self._position_state[p]["label"] = "block"

    async def un_block_point(self, point):
        points = point if isinstance(point, list) else [point]
        
        for p in points:
            pos_data = self._position_state.get(p)
            if pos_data:
                self._position_state[p]["label"] = "None"

    async def active_request(self, data):
        key = str(data.get("end"))
        
        file_name = self.mapping.get(key)
        logger.info(f"file_name: {file_name}")
        if file_name:
            group_id = data.get("group_id")
            node_name = data.get("node_name")
            new_data = self.data_configs[file_name][key]
            new_data["group_id"] = group_id
            new_data["node_name"] = node_name
            try:
                response = await self.execute_logic(new_data, 1)
                return response
            except Exception as e:
                logger.warning(f"Error: {e}")
                return None

    async def clear_monitor(self, data):
        key = data.get("position")

        file_name = self.mapping.get(key)
        if file_name:
            try:
                data["logic_path"] = self.data_configs[file_name][key]["logic_path"]
                await self.execute_logic(data, 2)
            except Exception as e:
                logger.warning(f"Error: {e}")

    async def _consumer_loop(self) -> None:
        while True:
            try:
                now = time.time()
                # Dọn dẹp dữ liệu cũ (> 10 phút)
                keys_to_del = [k for k, v in self._position_state.items() 
                               if now - v.get('ts', 0) > 600]
                for k in keys_to_del:
                    del self._position_state[k]
                
                await asyncio.sleep(60) 
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in manager loop: {e}")
                await asyncio.sleep(1)

pos_manager = Position_Manager(settings.time_recognition)