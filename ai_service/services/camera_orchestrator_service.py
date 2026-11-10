from core.database import get_collection
from multiprocessing import Manager, Process
import math
import time
from shared.logger import get_logger
from typing import List, Dict, Any
from core.database import get_collection
from services.camera_process_worker import start_camera_threads
from services.yolo_detector import YoloDetector
from core.config import settings
import asyncio
import httpx


logger = get_logger("camera_ai_service")

class CameraOrchestratorService:
    def __init__(self, group_id=0, num_processes=4, max_retry_attempts=3, model_path="yolov8n.pt", target_fps=5.0):
        self.group_id = group_id
        self.num_processes = num_processes
        self.max_retry_attempts = max_retry_attempts
        self.model_path = model_path
        self.target_fps = target_fps
        self.manager = Manager()
        self.shared_dict = self.manager.dict()
        self.target_dict = self.manager.dict()
        self.processes = []
        self.cameras = []
        self.logic_path = settings.logic_path
        self._is_running = True

    def _devide_camera_urls(self):
        total_cameras = len(self.cameras)
        if total_cameras == 0:
                return [], 0

        cameras_per_process = math.ceil(total_cameras / self.num_processes)
        
        camera_groups = []
        for i in range(0, total_cameras, cameras_per_process):
            group = self.cameras[i:i + cameras_per_process]
            camera_groups.append(group)

        return camera_groups, total_cameras

    async def _report_to_logic_service(self):
        logger.info("Background reporting task started.")
        
        async with httpx.AsyncClient() as client:
            while self._is_running:
                try:
                    # Chuyển đổi Manager.dict sang dict thường để serialize JSON
                    data_to_send = dict(self.target_dict)
                    if data_to_send:
                        # Gửi POST request
                        response = await client.post(
                            self.logic_path, 
                            json=data_to_send,
                            timeout=3.0
                        )
                        
                        if response.status_code != 200:
                            logger.info(f"Sending AI data fail! Alert!")
                    
                except Exception as e:
                    logger.error(f"Error sending data to Logic Service: {e}")

                # Chờ 1 giây cho chu kỳ tiếp theo
                await asyncio.sleep(0.5)

    async def start(self):
        logger.info(f"Starting Camera Orchestrator Service for group id: {self.group_id}, with {self.num_processes} processes")

        cursor = get_collection("cameras").find({"group_id": {"$in": self.group_id}})
        raw_cameras = await cursor.to_list(length=None)

        #Chuyển dữ liệu về đúng định dạng
        for c in raw_cameras:
            self.cameras.append({
                'camera_name': c['camera_name'],
                'cam_path': c['camera_path'], # Map 'camera_path' từ DB sang 'cam_path' cho Thread
                'id': str(c['_id']),
                'roi': c.get('roi', []), # Lưu lại ROI để dùng cho logic AI sau này
                'group_id': c.get('group_id', 0) # Lưu lại group_id để dùng cho monitor
            })

        #Tìm cách hold cho xong config mới chạy
        # time.sleep(5)

        camera_groups, total = self._devide_camera_urls()

        logger.info(f"Divided {total} cameras into {len(camera_groups)} groups")
        logger.info(f"Starting {len(camera_groups)} camera processes with {self.max_retry_attempts} max retry attempts and {self.target_fps} FPS")

        # Tạo và spawn các process camera
        for i, camera_group in enumerate(camera_groups):
            process = Process(
                target=start_camera_threads,
                args=(i, camera_group, self.shared_dict, self.max_retry_attempts, self.target_fps)
            )
            self.processes.append(process)
            process.start()

        ai_process = YoloDetector(
            shared_dict=self.shared_dict, 
            target_dict=self.target_dict, 
            model_path=self.model_path, 
            target_fps=self.target_fps,
            draw=True
        )
        self.processes.append(ai_process)
        ai_process.start()

        # Kích hoạt task gửi data định kỳ (không dùng await ở đây để nó chạy nền)
        asyncio.create_task(self._report_to_logic_service())
        logger.info("Sending data to logic service ....")

    async def stop(self):
        """Dừng tất cả process"""
        self._is_running = False

        for process in self.processes:
            process.terminate()
        
        for process in self.processes:
            process.join(timeout=5.0)
        
        logger.info("All processes stopped")



        
        
