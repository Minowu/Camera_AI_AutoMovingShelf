from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List, Any, Union
from pydantic import field_validator

load_dotenv()

class Settings(BaseSettings):
    # Database
    mongo_url: str = "mongodb+srv://CamAI_DB:Xinhzai1102%40%40@cluster0.1xazymq.mongodb.net/"
    # mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "CamAI_Honda"
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    # Environment
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Logging
    log_level: str = "INFO"

    #RCS
    ics_host: str = "192.168.50.39"
    logic_path: str = "http://192.168.1.2"

    #Camera 
    group_id: Any = []
    num_process: int = 4
    max_retry_attempts: int = 3
    weight_path: str = "yolov8n.pt"
    target_fps: float = 5.0

    @field_validator("group_id", mode="before")
    @classmethod
    def parse_group_id(cls, v: Any):
        # Nếu là chuỗi (từ .env gửi qua) như "1" hoặc "1,2,3"
        if isinstance(v, str):
            try:
                return [int(x.strip()) for x in v.split(",") if x.strip()]
            except ValueError:
                return []
        # Nếu đã là list (giá trị mặc định hoặc truyền trực tiếp)
        if isinstance(v, list):
            return v
        # Nếu là số nguyên đơn lẻ (trường hợp hiếm gặp khi nạp từ nguồn khác)
        if isinstance(v, int):
            return [v]
        return []

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
