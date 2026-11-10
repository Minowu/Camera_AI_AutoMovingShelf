import cv2
import numpy as np
import time
from ultralytics import YOLO
from multiprocessing import Process, Event
import torch
from shared.logger import get_logger

logger = get_logger("camera_ai_service")

class YoloDetector(Process):
    def __init__(self, shared_dict, target_dict, model_path, target_fps=5.0, draw=True):
        super().__init__()
        self.shared_dict = shared_dict
        self.target_dict = target_dict
        self.frame_interval = 1.0 / target_fps
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_path = model_path
        self._stop_event = Event()
        self.show_video = draw

    def _load_model(self):
        try:
            model = YOLO(self.model_path)
            model.to(self.device)
            logger.info(f"AI Model loaded successfully on {self.device}")
            self.model = model
        except Exception as e:
            logger.error(f"FATAL: Cannot load model Yolo: {e}")

    def _detect(self, frame):
        try:
            # Hỗ trợ cả đơn frame (np.ndarray) và batch (List[np.ndarray])
            results = self.model(frame, device=self.device, verbose=False)
            return results
        except Exception as e:
            logger.error(f"Error inference: {e}")
            return None

    def _draw_debug(self, frame, cam_name, detections, rois):
        for roi in rois:
            x1, y1, x2, y2 = roi['x1'], roi['y1'], roi['x2'], roi['y2']
            name = roi['name']
            
            # Kiểm tra xem vùng này có đang chứa class nào không
            current_label = detections.get(name)
            color = (0, 0, 255) if current_label == "hang" else (0, 255, 0) # Đỏ nếu có, Xanh nếu trống
            
            # Vẽ ROI
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{name}: {current_label}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        cv2.imshow(f"Debug AI: {cam_name}", frame)

    def _is_inside_box(self, cx, cy, x1, y1, x2, y2):
        return x1 < cx < x2 and y1 < cy < y2

    def _process_results(self, results, batch_info, frame_list):
        try:
            # i chính là vị trí của frame trong batch
            for i, result in enumerate(results):
                # Lấy lại đúng metadata của camera đó qua index i
                info = batch_info[i]
                cam_name = info['camera_name']
                group_id = info['group_id']
                rois = info.get('rois', [])

                # Tạo dict tạm cho camera này
                cam_results = {}

                # Khởi tạo trạng thái trước cho các ROI
                current_frame_results = {}
                for roi in rois:
                    current_frame_results[roi['name']] = "trong"
                
                if result.boxes is not None:
                    for data in result.boxes.data.tolist():
                        x1, y1, x2, y2, conf, cls_id = data
                        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

                        #Kiểm tra xem có trong vùng không
                        if conf > 0.6:
                            label = result.names[int(cls_id)]
                            for roi in rois:
                                if self._is_inside_box(cx, cy, roi['x1'], roi['y1'], roi['x2'], roi['y2']):  
                                    # Lưu kết quả vào vùng tương ứng
                                    cam_results[roi['name']] = label

                                    current_frame_results[roi['name']] = label

                # Cập nhật sang target gửi sang
                now = time.time()
                for roi_name, final_label in current_frame_results.items():
                    # Chỉ cập nhật vào shared memory ở đây
                    self.target_dict[roi_name] = {
                        "ts": now,
                        "label": final_label,
                        "group_id": group_id
                    }

                if self.show_video:
                    # Lấy frame tương ứng từ frame_list để vẽ
                    debug_frame = frame_list[i].copy()
                    self._draw_debug(debug_frame, cam_name, cam_results, rois)

            if self.show_video:
                cv2.waitKey(1) # Cần thiết để cv2.imshow hoạt động

        except Exception as e:
            logger.error(f"Error mapping results: {e}")


    def run(self):
        logger.info(f"Start AI Process. Model: {self.model_path}")

        self._load_model()
        if self.model is None:
            logger.error("Error: Cannot import model")
            return

        last_inference_time = 0

        while not self._stop_event.is_set():
            current_time = time.time()
            if current_time - last_inference_time < self.frame_interval:
                time.sleep(0.01)
                continue
            
            last_inference_time = current_time
            
            # Lấy danh sách camera hiện có
            try:
                camera_names = list(self.shared_dict.keys())
            except:
                continue

            frame_list = []
            batch_info = []

            for camera_name in camera_names:
                try:
                    camera_data = self.shared_dict.get(camera_name)
                    # Kiểm tra tính hợp lệ
                    if not camera_data or camera_data['status'] != 'success' or camera_data['frame'] is None:
                        continue    
                    # Kiểm tra frame age (Tùy chọn: bỏ qua nếu frame quá cũ > 1s)
                    if current_time - camera_data.get('ts', 0) > 3.0:
                        continue
                    try:
                        # Decode frame từ JPEG
                        frame = camera_data['frame']
                        if frame is not None:
                            try:
                                frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_LINEAR)
                            except Exception as re:
                                logger.error(f"Error resize frame {camera_name}: {re}")
                        #Lấy frame từ shared_dict vào list
                        if frame is not None:
                            frame_list.append(frame)
                            batch_info.append({
                                "camera_name": camera_name,
                                "rois": camera_data.get("rois"),
                                "group_id": camera_data.get("group_id")
                            })
                    except Exception as e:
                        logger.error(f"Error handling {camera_name}: {e}")
                except Exception as e:
                    logger.error(f"Error getting frame from {camera_name}: {e}")
            
            #Xử lý kết quả
            if frame_list:
                results = self._detect(frame_list)
                
                if results:
                    self._process_results(results, batch_info, frame_list)

        logger.info("AI Process stopped. Cleaning up resources...")
        if self.model:
            del self.model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        logger.info("AI Process exited cleanly.")
    
    def stop(self):
        """Hàm này được gọi từ Main Process để yêu cầu dừng"""
        logger.info("Stopping YoloDetector service...")
        self._stop_event.set()


 
                    
    