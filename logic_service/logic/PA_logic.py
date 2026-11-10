from shared.logger import get_logger
from services.POS_manager import pos_manager
from services.Task_manager import task_service
from services.Robot_manager import robot_service
from core.config import settings
import asyncio
import time
import uuid
import re
from fastapi import HTTPException
import httpx

logger = get_logger("logic_service")
ics_url = f"http://{settings.ics_host}:7000"

async def process_auto(data):
    type_point = data.get("logic_type") 

    match type_point:
        case 5: 
            await handle_logic_5(data)
        case 6:
            await handle_logic_6(data)
        case _:
            pass

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

    elif len(data) == 2:
        logger.info("----Sending RCS SINGLE PA----")
        payload = {
                "modelProcessCode": "Cap_PT_PA", 
                "fromSystem": "Thadosoft", 
                "orderId": order_id,  
                "taskOrderDetail": [ 
                    {    
                        "taskPath": f"{data[0]},{data[1]}"
                    } 
                ] 
            }

    elif len(data) == 4:
        logger.info("----Sending RCS DUAL PA----")
        payload = {
                "modelProcessCode": "Cap_tra_PT_PA", 
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
        pos = [data[0], data[1]]
        track_data = {
            "position": pos
        }
        #Handle RCS response
        await task_service.track_for_task(order_id, track_data)
        await add_task(payload)
        await pos_manager.block_point(pos)

async def handle_logic_6(data):
    matching = data.get("matching", [])
    if len(matching) < 4:
        logger.warning("Not enough 4 points data matching")
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

async def handle_logic_5(data):
    matching = data.get("matching", {})
    
    required_keys = ["Start", "End", "Next_start", "Next_end"]
    if not all(k in matching for k in required_keys):
        logger.warning("Not enough parameters for logic 5")
        return None

    start_points = matching.get("Start", [])
    end_points = matching.get("End", [])
    next_starts = matching.get("Next_start", [])

    states_start = await pos_manager.get_state(start_points)
    states_end = await pos_manager.get_state(end_points)
    states_next_start = await pos_manager.get_state(next_starts)

    chosen_start = None
    chosen_end = None
    chosen_next_start = None

    for i, state in enumerate(states_start):
        if state == "hang":
            chosen_start = start_points[i]
            break

    if not chosen_start:
        logger.info("No 'hang' state found in start_points")
        return None

    for i, state in enumerate(states_end):
        if state == "trong":
            chosen_end = end_points[i]
            break

    if not chosen_end:
        logger.info("No 'trong' state found in end_points")
        return None

    for i, state in enumerate(states_next_start):
        if state == "hang":
            chosen_next_start = next_starts[i]
            break

    final_chosen = [chosen_start, chosen_end]
    if chosen_next_start:
        final_chosen.append(chosen_next_start)

    await request_RCS(final_chosen)
    return True

