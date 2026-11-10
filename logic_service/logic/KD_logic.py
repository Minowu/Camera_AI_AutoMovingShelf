from shared.logger import get_logger
from services.POS_manager import pos_manager
from services.Task_manager import task_service
from services.SSE_manager import sse_manager
from core.config import settings
import asyncio
import time
import uuid
import re
from fastapi import HTTPException
import httpx

logger = get_logger("logic_service")
ics_url = f"http://{settings.ics_host}:7000"

async def add_task(payload):
    try:    
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(f"{ics_url}/ics/taskOrder/addTask", json=payload)
        logger.info(f"ICS API response: {response.json()}")
    except Exception as e:
        logger.error(f"Error calling process caller: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def request_RCS(data):
    order_id = f"4-{time.strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:4]}"
    payload = None

    if len(data) == 2:
        logger.info("----Sending RCS SINGLE KD----")
        payload = {
                "modelProcessCode": "Cap_phu_tung68", 
                "fromSystem": "Thadosoft", 
                "orderId": order_id,  
                "taskOrderDetail": [ 
                    {    
                        "taskPath": f"{data[0]},{data[1]}"
                    } 
                ] 
            }

    elif len(data) == 4:
        logger.info("----Sending RCS DUAL KD----")
        payload = {
                "modelProcessCode": "Cap_tra_xe_trong_PT68", 
                "fromSystem": "Thadosoft", 
                "orderId": order_id,  
                "taskOrderDetail": [ 
                    {    
                        "taskPath": f"{data[0]},{data[1]}"
                    }, 
                    {    
                        "taskPath": f"{data[2]},{data[3]}"
                    } 
                ] 
            } 

    else:
        return None

    if payload:
        track_data = {
            "position": data[0]
        }
        #Handle RCS response
        await task_service.track_for_task(order_id, track_data)
        await add_task(payload)
        await pos_manager.block_point(data[0])

async def process_auto(data):
    matching = data.get("matching", [])
    if len(matching) < 4:
        logger.warning("Not enough 3 points data matching")
        return None

    point_to_check = matching[1:3]
    states = await pos_manager.get_state(point_to_check)

    if not states:
        return None

    s1, s2 = states[0], states[1]

    if s1 == "trong" and s2 == "hang":
        data = [matching[0], matching[1], matching[2], matching[3]]
        await request_RCS(data)

    elif s1 == "trong":
        data = [matching[0], matching[1]]
        await request_RCS(data)

async def active_process(data):
    matching = data.get("matching", [])
    if len(matching) < 3:
        logger.warning("Not enough 3 points data matching")
        return None

    point_to_check = matching[1:2]
    logger.info(f"Start checking active: {point_to_check}")
    group_id = await pos_manager.get_group(matching[0])
    
    while True:
        states = await pos_manager.get_state(point_to_check)

        if states:
            status = states[0]
            if status == "hang":
                logger.info("----Sending RCS 3 POINTS----")
                order_id = f"3-{time.strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:4]}"
                payload = {
                    "modelProcessCode": "Cap_tra_xe_vat_lieu68", 
                    "fromSystem": "Thadosoft", 
                    "orderId": order_id,  # Gán orderId bằng timestamp
                    "taskOrderDetail": [ 
                        {    
                            "taskPath": f"{matching[0]},{matching[1]},{matching[2]}"
                        } 
                    ] 
                }

                track_data = {
                    "position": matching[1],
                    "group_id": group_id
                }
                await task_service.track_for_task(order_id, track_data)
                await add_task(payload)
                return True         
            # logger.info(f"Current states: {status}, waiting for hang")

        await asyncio.sleep(1)  # Nghỉ 1 giây mỗi lần check

async def active_request(payload):
    group_id = payload.get("group_id")
    payload["timestamp"] = time.time()
    logger.info(f"Payload: {payload}")

    node_name = payload.get("node_name")

    match = re.search(r"^([^_]+).*?-(\d+)", node_name)
    if match:
        prefix = match.group(1)  # "L2"
        number = match.group(2)  # "1" (string)

    #Create structure spam_log
    if group_id not in task_service._log_spam:
        logger.info(f"Create spam log for group {group_id}")
        task_service._log_spam[group_id] = {}

    if prefix not in task_service._log_spam[group_id]:
        task_service._log_spam[group_id][prefix] = {}

    if number not in task_service._log_spam[group_id][prefix]:
        task_service._log_spam[group_id][prefix][number] = {}

    should_process = (task_service._log_spam[group_id][prefix][number] == {})

    matching = payload.get("matching", [])
    key = matching[1]

    # Nếu key đã tồn tại, không xử lý nữa (chống spam)
    if key in task_service._log_spam[group_id][prefix][number]:
        logger.info(f"Spam detected, skip: group_id={group_id}, key={key}")
        return {"status": "skip", "msg": "Payload already processed"}

    # Nếu chưa có thì lưu lại
    task_service._log_spam[group_id][prefix][number][key] = payload.copy()
    task_service._reverse_index[key] = (prefix, number)

    if should_process:
        try:
            asyncio.create_task(active_process(payload))

            clean_payload = {
                "node_name": payload['node_name'],
                "prefix": prefix,
                "number": number
            }
            await sse_manager.broadcast(group_id=group_id, data=clean_payload)
            logger.info(f"Process active request: {key}, successful send to monitor")

        except Exception as e:
            logger.error(f"Error in background process: {e}")

    return {"status": "success", "data": "Task added to service successfully"}

async def handle_clear_monitor(data):
    order_id = data.get("order_id", "")
    group_id = data.get("group_id", 0)
    if order_id not in task_service._tracking_task:
        logger.warning(f"Undefine order_id: {order_id}, continue!")
        return

    logger.info(f"Clearing order_id: {order_id}")
    task_data = task_service._tracking_task[order_id]
    end_point = str(task_data.get("position"))

    # Lấy prefix, number từ reverse_index
    if end_point not in task_service._reverse_index:
        logger.warning(f"Key {end_point} not found in reverse_index")
        del task_service._tracking_task[order_id]
        return

    prefix, number = task_service._reverse_index.pop(end_point)

    if group_id not in task_service._log_spam:
        logger.info(f"Group_id not found, remove tracking task {order_id}")
        del task_service._tracking_task[order_id]
        return

    group_dict = task_service._log_spam[group_id]

    if prefix not in group_dict or number not in group_dict[prefix]:
        logger.info(f"Prefix or number not found, remove tracking task {order_id}")
        del task_service._tracking_task[order_id]
        return

    number_dict = group_dict[prefix][number]

    # Xóa key hiện tại
    if end_point in number_dict:
        number_dict.pop(end_point, None)
        logger.info(f"Removed spam log: group={group_id}, prefix={prefix}, number={number}, key={end_point}")

    # Lấy key tiếp theo theo insert order (FIFO) trong cùng prefix+number
    next_payload = None
    if number_dict:
        next_key = next(iter(number_dict))
        next_payload = number_dict[next_key]

    if next_payload:
        try:
            clear_payload = {
                "node_name": next_payload['node_name'],
                "prefix": prefix,
                "number": number,
            }
            await sse_manager.broadcast(group_id = group_id, data = clear_payload)
        except Exception as e:
            logger.error(f"Error publishing next qr: {e}")

        try:
            asyncio.create_task(active_process(next_payload))
            logger.info(f"Auto-processed next end_qr: {next_key}")
        except Exception as e:
            logger.error(f"Error publishing to queue: {e}")
    
    else:
        try:
            clear_payload = {
                "prefix": prefix,
                "number": number,
            }
            logger.info(f"Clean {prefix}, {number}")
            await sse_manager.broadcast(group_id = group_id, data = clear_payload)
        except Exception as e:
            logger.error(f"Error publishing next qr: {e}")

    # Nếu hết key trong number → xóa number
    if not number_dict:
        group_dict[prefix].pop(number, None)
    # Nếu hết prefix → xóa prefix
    if not group_dict[prefix]:
        group_dict.pop(prefix, None)
    # Nếu hết group → xóa group
    if not group_dict:
        task_service._log_spam.pop(group_id, None)

    # Xóa order_id khỏi tracking
    del task_service._tracking_task[order_id]
    logger.info(f"Removed order_id: {order_id} from tracking")