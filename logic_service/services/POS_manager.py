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
        self._position_state: Dict[Tuple[str, str], Any] = {}
        self.data_configs = {}
        self._pending_state = {}
        self._registry = {}
        self._last_check_time = {}
        self.time_recognition = time_recognition
        self._failed_points = set()
        self._dispatching = set()

    async def start(self) -> None:
        self.load_configs()

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
                            

                except Exception as e:
                    print(f"[ERROR] Could not load {filename}: {e}")
            
        logger.info(f"Loaded all config files")

    async def stop(self) -> None:
        if self._consumer_task:
            self._consumer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._consumer_task
            self._consumer_task = None

    async def mark_failed(self, pos_id, group_id):
        key = (group_id, str(pos_id))
        self._failed_points.add(key)
        logger.error(f"[POS_manager] Điểm {pos_id} bị đánh dấu thất bại (failed), tạm dừng dispatch")

    async def update_state(self, data) -> None:
        now = time.time()

        for pos_id, info in data.items():
            new_label = info.get("label")
            group_id = info.get("group_id")
            key = (group_id, pos_id)
            pos_cfg = self.data_configs.get(f"{group_id}_config.json", {}).get(pos_id)
            current_confirmed = self._position_state.get(key, {})
            
            if current_confirmed.get("label") == "block":
                continue

            if new_label == current_confirmed.get("label"):
                self._position_state[key]["ts"] = now
                self._pending_state.pop(key, None)

                # Kiểm tra có trong config thì thực hiện gửi đến đúng logic
                if pos_cfg and new_label == "hang":
                    if key not in self._failed_points and key not in self._dispatching:
                        self._dispatching.add(key)
                        asyncio.create_task(self.request_service_auto(pos_cfg, key))
                continue

            pending = self._pending_state.get(key)

            if pending and pending["label"] == new_label:
                elapsed = now - pending["start_ts"]
                required_time = (pos_cfg or {}).get("time_recognition", self.time_recognition)

                if elapsed >= required_time:
                    # Đã đủ required_time giây liên tục -> Xác nhận trạng thái mới
                    self._position_state[key] = {
                        "label": new_label,
                        "group_id": group_id,
                        "ts": now,
                    }
                    self._pending_state.pop(key, None)

            else:
                self._pending_state[key] = {
                    "label": new_label,
                    "start_ts": now
                }

    async def request_service_auto(self, data, key):
        try:
            await self.execute_logic(data, 0, key[0])
        except Exception as e:
            logger.warning(f"Error: {e}")
        finally:
            self._dispatching.discard(key)

    async def execute_logic(self, data, mode, group_id):
        try:
            logic_path = data.get('logic_path')
            if not logic_path:
                return

            # 1. Lấy hàm từ file logic (Tự động hot-reload nếu cần)
            process_func = await self.get_logic_func(logic_path, mode)

            if process_func:
                response = await process_func(data, group_id)
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

    async def get_state(self, points, group_id):
        states = []
        for point in points:
            pos_data = self._position_state.get((group_id, str(point)), {})
            label = pos_data.get("label", None)            
            states.append(label)
        return states

    async def get_group(self, point, group_id):
        pos_data = self._position_state.get((group_id, str(point)), {})
        group = pos_data.get("group_id", None)            
        return group

    async def block_point(self, point, group_id):
        points = point if isinstance(point, list) else [point]
        now = time.time()
        for p in points:
            key = (group_id, str(p))
            self._failed_points.discard(key)
            self._pending_state.pop(key, None)
            if key in self._position_state:
                self._position_state[key]["label"] = "block"
                self._position_state[key]["ts"] = now
            else:
                self._position_state[key] = {"label": "block", "group_id": group_id, "ts": now}
        blocked_list = [k for k, v in self._position_state.items() if v.get("label") == "block"]
        logger.info(f"🔒 [BLOCK] Đã khóa ô: {points} | Các ô đang block: {blocked_list}")

    async def un_block_point(self, point, group_id):
        points = point if isinstance(point, list) else [point]
        now = time.time()
        for p in points:
            key = (group_id, str(p))
            self._failed_points.discard(key)
            self._pending_state.pop(key, None)
            if key in self._position_state:
                self._position_state[key]["label"] = "None"
                self._position_state[key]["ts"] = now
            else:
                self._position_state[key] = {"label": "None", "group_id": group_id, "ts": now}
        blocked_list = [k for k, v in self._position_state.items() if v.get("label") == "block"]
        logger.info(f"🔓 [UNBLOCK] Đã mở khóa ô: {points} | Các ô đang block còn lại: {blocked_list}")

    async def active_request(self, data):
        key = str(data.get("end"))
        
        group_id = data.get("group_id")
        file_name = f"{group_id}_config.json"
        logger.info(f"file_name: {file_name}")
        pos_cfg = self.data_configs.get(file_name, {}).get(key)
        if pos_cfg:
            node_name = data.get("node_name")
            new_data = pos_cfg.copy()
            new_data["group_id"] = group_id
            new_data["node_name"] = node_name
            try:
                response = await self.execute_logic(new_data, 1, group_id)
                return response
            except Exception as e:
                logger.warning(f"Error: {e}")
                return None

    async def clear_monitor(self, data):
        key = data.get("position")

        group_id = data.get("position_group")
        pos_cfg = self.data_configs.get(f"{group_id}_config.json", {}).get(key)
        if pos_cfg:
            try:
                data["logic_path"] = pos_cfg["logic_path"]
                await self.execute_logic(data, 2, group_id)
            except Exception as e:
                logger.warning(f"Error: {e}")

pos_manager = Position_Manager(settings.time_recognition)