import time
import multiprocessing
from services.camera_thread_worker import CameraThread
from shared.logger import get_logger

logger = get_logger("camera_ai_service")

def start_camera_threads(process_id, camera_group, shared_dict, max_retry_attempts, target_fps):
    """
    stop_event: multiprocessing.Event() dùng để báo hiệu dừng an toàn từ Main Process
    """
    threads = []

    # --- 1. Khởi tạo và chạy Thread ---
    for camera in camera_group:
        # Truyền thẳng shared_dict vào thread để ghi trực tiếp
        thread = CameraThread(
            camera_info=camera, 
            shared_dict=shared_dict,  # Ghi thẳng vào đây
            max_retries=max_retry_attempts, 
            target_fps=target_fps
        )
        threads.append(thread)
        thread.start()
        logger.info(f"Process {process_id}: Đã khởi động thread cho cam {camera['camera_name']}")

    # --- 2. Vòng lặp vô tận (Keep-alive) ---
    try:
        # Thay vì check stop_event, ta cứ chạy mãi mãi
        # Process này chỉ chết khi bị cha gọi .terminate()
        while True:
            time.sleep(1) 

    except KeyboardInterrupt:
        # Để hỗ trợ debug khi chạy tay (Ctrl+C)
        pass
    except Exception as e:
        logger.error(f"Process {process_id} gặp lỗi crash: {e}")