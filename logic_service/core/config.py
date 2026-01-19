from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    # Environment
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Logging
    log_level: str = "INFO"

    # RCS
    ics_host: str = "192.168.50.39"

    # Service
    time_recognition: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
