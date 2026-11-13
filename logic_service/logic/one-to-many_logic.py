"""
one-to-many_logic.py
Module kịch bản điều khiển tự động 1 nguồn nhiều đích dự phòng có XOAY VÒNG (áp dụng cho Honda Hà Nam).
Nguyên tắc:
1. Đọc process_code động từ file config JSON (ví dụ SingleGroupAF).
2. matching[0] là ô nguồn; matching[1:] là danh sách ô đích theo thứ tự xoay vòng.
3. Gửi toàn bộ mảng ứng viên sang pos_manager.get_state(candidates) để quét RAM 1 lần cực nhanh.
4. Cơ chế Xoay Vòng (Round-Robin): Lần 1 cấp ô 1, lần 2 cấp ô 2, lần 3 cấp ô 3... Nếu ô đến lượt bận thì tự động nhảy sang ô trống tiếp theo trong vòng tròn.
5. Chỉ khóa đúng ô nguồn (source) để chống spam, tuyệt đối KHÔNG khóa ô đích (dest).
6. Sinh Order ID tiền tố O- để Task_manager mở khóa ngay khi robot bốc hàng xong (subTaskSeq=2, subTaskStatus=2).
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

# Lưu chỉ số xoay vòng (Round-Robin pointer) trong RAM cho từng ô nguồn
_last_dest_index = {}


async def process_auto(data: dict) -> None:
    """
    Kịch bản tự động chuyển hàng 1 nguồn -> xoay vòng các đích dự phòng (Honda Hà Nam).
    Được POS_manager gọi khi ô nguồn A có 'hang' đủ time_recognition.
    """
    matching = data.get("matching", [])
    if len(matching) < 2:
        return

    source = matching[0]
    candidates = matching[1:]
    n = len(candidates)

    # 1. Quét RAM đồng thời trạng thái của toàn bộ danh sách ô đích (cực nhanh)
    states = await pos_manager.get_state(candidates)
    if not states:
        return

    # 2. Thuật toán Xoay Vòng (Round-Robin): Bắt đầu từ vị trí kế tiếp của lần trước
    start_index = _last_dest_index.get(source, 0)
    selected_dest = None
    selected_idx = None

    for step in range(n):
        idx = (start_index + step) % n
        if states[idx] == "trong":
            selected_dest = candidates[idx]
            selected_idx = idx
            break

    # Nếu tất cả các ô đích trong vòng xoay đều bận -> dừng chờ chu kỳ camera quét sau
    if not selected_dest:
        logger.info(f"[one-to-many] Toàn bộ {n} ô đích xoay vòng của {source} đều bận, chờ chu kỳ sau.")
        return

    # 3. Kiểm tra mã lệnh cấu hình trong JSON (Pre-validation)
    model_code = data.get("process_code")
    if not model_code:
        logger.error(f"[one-to-many] Điểm {source} chưa cấu hình process_code trong JSON!")
        return

    # 4. Tạo Order ID chuẩn O- và gói tin điều xe
    order_id = f"O-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
    payload = {
        "modelProcessCode": model_code,
        "fromSystem": "Thadosoft",
        "orderId": order_id,
        "priority": 6,
        "taskOrderDetail": [{"taskPath": f"{source},{selected_dest}"}]
    }

    # 5. Ghi tracking và gửi sang RCS (CHỈ KHÓA Ô NGUỒN)
    # Ghi tracking chỉ riêng điểm source
    await task_service.track_for_task(order_id, {"position": source})

    logger.info(f"📤 [one-to-many] Gửi lệnh RCS: {ics_url}/ics/taskOrder/addTask | Payload: {json.dumps(payload)}")
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
            logger.warning(f"⚠️ [one-to-many] Lần {attempt}/3 gửi RCS thất bại cho {source}: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(1)

    if res_json is None:
        logger.error(f"❌ [one-to-many] Gọi RCS thất bại cho {source} -> {selected_dest}: {last_error}. Rollback tracking.")
        task_service.tracking_task.pop(order_id, None)
        await pos_manager.mark_failed(source)
        return

    logger.info(f"📥 [one-to-many] RCS phản hồi: {res_json}")

    if str(res_json.get("code")) != "1000":
        logger.error(
            f"❌ [one-to-many] RCS từ chối lệnh {order_id} cho {source}: "
            f"code={res_json.get('code')} desc={res_json.get('desc')} | body={res_json}"
        )
        task_service.tracking_task.pop(order_id, None)
        await pos_manager.mark_failed(source)
        return

    # RCS nhận lệnh thành công -> CHỈ KHÓA Ô NGUỒN, KHÔNG KHÓA Ô ĐÍCH
    await pos_manager.block_point(source)

    # CẬP NHẬT CON TRỎ XOAY VÒNG SANG Ô KẾ TIẾP CHO LẦN SAU
    _last_dest_index[source] = (selected_idx + 1) % n

    logger.info(
        f"[one-to-many] Đã điều xe xoay vòng {source} -> {selected_dest} (vị trí {selected_idx + 1}/{n}) "
        f"(Order: {order_id}, Code: {model_code}, Next: index {(_last_dest_index[source])})"
    )
