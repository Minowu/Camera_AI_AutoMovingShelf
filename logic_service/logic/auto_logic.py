"""
auto_logic.py
Module kịch bản điều khiển tự động chuyển đơn 2 điểm [A, B] (áp dụng cho Honda Hà Nam).
Nguyên tắc:
1. Đọc process_code động từ file config JSON.
2. Kiểm tra chặt mã lệnh và trạng thái ô đích trống trước khi điều xe.
3. Gửi HTTP sang RCS và khóa đồng thời cả 2 điểm [source, dest]; rollback nếu rớt mạng.
4. Không chia robot theo zone, để RCS tự do điều phối xe.
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
    Kịch bản tự động chuyển đơn 2 điểm A -> B cho Honda Hà Nam.
    Được POS_manager gọi khi ô nguồn A có 'hang' đủ time_recognition.
    """
    matching = data.get("matching", [])
    if len(matching) < 2:
        return

    source, dest = matching[0], matching[1]

    # 1. Kiểm tra ô đích có đang trống hay không
    states = await pos_manager.get_state([dest])
    if not states or states[0] != "trong":
        return

    # 2. Kiểm tra mã lệnh cấu hình trong JSON
    model_code = data.get("process_code")
    if not model_code:
        logger.error(f"[auto_logic] Điểm {source} chưa cấu hình process_code trong JSON!")
        return

    # 3. Tạo Order ID chuẩn S- và gói tin điều xe
    order_id = f"S-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
    payload = {
        "modelProcessCode": model_code,
        "fromSystem": "Thadosoft",
        "orderId": order_id,
        "priority": 6,
        "taskOrderDetail": [{"taskPath": f"{source},{dest}"}]
    }

    # 4. Ghi tracking, gửi sang RCS và khóa cả 2 điểm
    await task_service.track_for_task(order_id, {"position": [source, dest]})

    logger.info(f"📤 [auto_logic] Gửi lệnh RCS: {ics_url}/ics/taskOrder/addTask | Payload: {json.dumps(payload)}")
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
            logger.warning(f"⚠️ [auto_logic] Lần {attempt}/3 gửi RCS thất bại cho {source}: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(1)

    if res_json is None:
        logger.error(f"❌ [auto_logic] Gọi RCS thất bại cho {source} -> {dest}: {last_error}. Rollback tracking.")
        task_service.tracking_task.pop(order_id, None)
        await pos_manager.mark_failed(source)
        return

    logger.info(f"📥 [auto_logic] RCS phản hồi: {res_json}")

    if str(res_json.get("code")) != "1000":
        logger.error(
            f"❌ [auto_logic] RCS từ chối lệnh {order_id} cho {source}: "
            f"code={res_json.get('code')} desc={res_json.get('desc')} | body={res_json}"
        )
        task_service.tracking_task.pop(order_id, None)
        await pos_manager.mark_failed(source)
        return

    # RCS nhận lệnh thành công -> Khóa cả ô lấy và ô trả hàng
    await pos_manager.block_point([source, dest])
    logger.info(f"[auto_logic] Đã điều xe {source} -> {dest} (Order: {order_id}, Code: {model_code})")
