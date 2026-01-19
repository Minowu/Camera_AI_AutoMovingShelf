from shared.logger import get_logger
import asyncio
from typing import Dict, Any
import asyncio
import contextlib
from datetime import datetime
from typing import Dict, List
import os
import json

logger = get_logger("logic_service")

class RobotService:
    def __init__(self) -> None:
        self.robot_in_zones: Dict[str, List[str]] = {}
        self.zone_configs = {}
        self.robot_configs = {}

    def load_zone_configs(self):
        config_dir = "config/zone_config"
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
                            for key in content.keys():
                                self.zone_configs[key] = content[key]

                except Exception as e:
                    print(f"[ERROR] Could not load {filename}: {e}")
            
        logger.info(f"Loaded all zone config files")

    def load_robot_configs(self):
        config_dir = "config/robot_config"
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
                            for key in content.keys():
                                self.robot_configs[key] = content[key]

                except Exception as e:
                    print(f"[ERROR] Could not load {filename}: {e}")
            
        logger.info(f"Loaded all robot config files")
    
    async def receive_data(self, payload):
        robot_sn = payload.get("deviceCode")
        device_position = payload.get("devicePosition")
        
        try:
            await self.is_inside_zone(robot_sn, device_position)
        except Exception as e:
            logger.error(f"Error updating state: {e}")

    async def is_inside_zone(self, serial_number, device_position):
        data_robot = self.robot_configs.get(serial_number)
        if not data_robot:
            return

        if not device_position:
            logger.error(f"device_position None for robot {serial_number}")
            return

        for zone in data_robot:
            has_zone = self.zone_configs.get(zone)
            if not has_zone:
                continue

            if device_position in has_zone:
                zone_list = self.robot_in_zones.setdefault(zone, [])
                if serial_number not in zone_list:
                    zone_list.append(serial_number)

                logger.info(
                    f"Robot {serial_number} is in the {zone} at {device_position}"
                )
                break


robot_service = RobotService()