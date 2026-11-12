"""
empty_one_place_logic.py
Module kịch bản điều khiển tự động trả kệ rỗng / xả vỏ (áp dụng cho Honda Hà Nam).
Nguyên tắc:
1. Đọc process_code động từ file config JSON (ví dụ SEGroupAF).
2. Lộ trình taskPath gửi sang RCS có cả điểm nguồn và điểm đích (bãi tập kết chung): f"{source},{dest}".
3. Chỉ khóa đúng điểm nguồn (source) để chống spam, tuyệt đối KHÔNG khóa điểm đích (dest) để các line khác vẫn trả vỏ được.
4. Sinh Order ID tiền tố X- để Task_manager mở khóa ngay khi robot bốc kệ xong (subTaskSeq=2, subTaskStatus=2).
"""

from shared.logger import get_logger
from services.POS_manager import pos_manager
from services.Task_manager import task_service
from core.config import settings
import asyncio
import json
import time
import uuid
import httpx

logger = get_logger("logic_service")
ics_url = f"http://{settings.ics_host}:7000"
MAX_RETRIES = 3
RCS_HEADERS = {"Accept-Language": "en-US"}


async def process_auto(data: dict) -> None:
    """
    Kịch bản tự động trả kệ rỗng / xả vỏ cho Honda Hà Nam.
    Được POS_manager gọi khi ô nguồn A có 'hang' (hoặc vỏ) đủ time_recognition.
    """
    matching = data.get("matching", [])
    if not matching:
        return

    source = matching[0]
    dest = matching[1] if len(matching) > 1 else source
    task_path = f"{source},{dest}" if len(matching) > 1 else f"{source}"

    # 1. Kiểm tra mã lệnh cấu hình trong JSON (Pre-validation)
    model_code = data.get("process_code")
    if not model_code:
        logger.error(f"[empty_one_place] Điểm {source} chưa cấu hình process_code trong JSON!")
        return

    # 2. Tạo Order ID chuẩn X- và gói tin điều xe
    order_id = f"X-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
    payload = {
        "modelProcessCode": model_code,
        "fromSystem": "Thadosoft",
        "orderId": order_id,
        "priority": 4,
        "taskOrderDetail": [{"taskPath": task_path}]
    }

    # 3. Ghi tracking và gửi sang RCS (CHỈ KHÓA Ô NGUỒN)
    # Ghi tracking chỉ riêng điểm source
    await task_service.track_for_task(order_id, {"position": source})

    logger.info(f"📤 [empty_one_place] Gửi lệnh RCS: {ics_url}/ics/taskOrder/addTask | Payload: {json.dumps(payload)}")
    res_json = None
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                res = await client.post(
                    f"{ics_url}/ics/taskOrder/addTask",
                    json=payload,
                    headers=RCS_HEADERS
                )
                res.raise_for_status()
                res_json = res.json()
            break
        except Exception as e:
            last_error = e
            logger.warning(f"⚠️ [empty_one_place] Lần {attempt}/3 gửi RCS thất bại cho {source}: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(1)

    if res_json is None:
        logger.error(f"❌ [empty_one_place] Gọi RCS thất bại cho ô {source}: {last_error}. Rollback tracking.")
        task_service.tracking_task.pop(order_id, None)
        await pos_manager.mark_failed(source)
        return

    logger.info(f"📥 [empty_one_place] RCS phản hồi: {res_json}")

    if str(res_json.get("code")) != "1000":
        logger.error(
            f"❌ [empty_one_place] RCS từ chối lệnh {order_id} cho {source}: "
            f"code={res_json.get('code')} desc={res_json.get('desc')} | body={res_json}"
        )
        task_service.tracking_task.pop(order_id, None)
        await pos_manager.mark_failed(source)
        return

    # RCS nhận lệnh thành công -> CHỈ KHÓA Ô NGUỒN, KHÔNG KHÓA Ô ĐÍCH (bãi chung)
    await pos_manager.block_point(source)
    logger.info(
        f"[empty_one_place] Đã điều xe trả vỏ {source} -> {dest} "
        f"(Order: {order_id}, Code: {model_code})"
    )
