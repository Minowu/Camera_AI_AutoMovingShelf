import cv2
import time
import threading
from shared.logger import get_logger

logger = get_logger("camera_ai_service")

class CameraThread(threading.Thread):
    def __init__(self, camera_info, shared_dict, max_retries, target_fps):
        super().__init__()
        self.camera_info = camera_info
        self.shared_dict = shared_dict
        self.max_retries = max_retries
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        self.running = True
        self.retry_count = 0

    def _connect_camera(self, time_out=5.0):
        cap = cv2.VideoCapture(self.camera_info['cam_path'])
        current_time = time.time()

        # Thử kết nối trong khoảng time_out
        while not cap.isOpened() and time.time() - current_time < time_out:
            time.sleep(0.1)
            cap = cv2.VideoCapture(self.camera_info['cam_path'])

        if cap.isOpened():
            logger.info(f"{self.camera_info['camera_name']} đã kết nối thành công")
            self.retry_count = 0  # Reset retry count khi thành công
            return cap
        else:
            # SỬA LỖI Ở ĐÂY: Chỉ log lỗi, KHÔNG tắt self.running
            logger.warning(f"Kết nối thất bại với {self.camera_info['camera_name']} (timeout)")
            return None

    def run(self):
        # Vòng lặp chính: Chạy miễn là cờ running = True
        while self.running:
            
            # Kiểm tra nếu đã thử quá số lần cho phép
            if self.retry_count >= self.max_retries:
                logger.error(f"Dừng {self.camera_info['camera_name']} vì quá số lần thử lại.")
                self.running = False
                break

            # 1. Cố gắng kết nối
            cap = self._connect_camera()

            if cap is not None:
                # --- TRƯỜNG HỢP KẾT NỐI THÀNH CÔNG ---
                logger.info(f"Bắt đầu lấy luồng video từ {self.camera_info['camera_name']}")
                p_time = 0
                while self.running:
                    ret, frame = cap.read()

                    if not ret:
                        logger.warning(f"Mất tín hiệu từ camera {self.camera_info['camera_name']}")
                        break 

                    #Bỏ qua frame để đảm bảo fps
                    c_time = time.time()
                    if c_time - p_time < self.frame_interval:
                        continue
                    p_time = c_time

                    frame = cv2.resize(frame, (1280, 720))

                    # Update dữ liệu thành công
                    self.shared_dict[self.camera_info['camera_name']] = {
                        'frame': frame,
                        'ts': time.time(),
                        'status': 'success',
                        'retry_count': 0,
                        'rois': self.camera_info['roi'],
                        'group_id': self.camera_info['group_id']
                    }

                cap.release() # Giải phóng camera khi bị break ra ngoài
            
            else:
                # --- TRƯỜNG HỢP KẾT NỐI THẤT BẠI ---
                self.retry_count += 1
                
                # Cập nhật trạng thái lỗi vào shared_dict để UI biết
                self.shared_dict[self.camera_info['camera_name']] = {
                    'frame': None,
                    'ts': time.time(),
                    'status': 'failed',
                    'retry_count': self.retry_count
                }

                logger.info(f"Đang thử lại {self.camera_info['camera_name']} ({self.retry_count}/{self.max_retries}) sau 5s...")
                time.sleep(5) # Chờ 5 giây trước khi quay lại đầu vòng lặp để thử kết nối lại

    def stop(self):
        self.running = False