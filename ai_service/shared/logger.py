"""
Centralized logging configuration
Shared logging utilities for all services
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from logging.handlers import TimedRotatingFileHandler

def setup_logger(
    name: str = "camera_ai",
    log_level: str = "INFO",
    service_name: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        log_level: Logging level
        service_name: Service name for log file naming
    
    Returns:
        Configured logger instance
    """
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Only setup if not already configured
    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        date_str = datetime.now().strftime("%Y%m%d")
        log_file_name = f"{service_name or 'app'}_{date_str}.log"
        log_file = log_dir / log_file_name

        file_handler = TimedRotatingFileHandler(
            log_file,
            when="D",           # Rotate mỗi ngày
            interval=1,         # Chu kỳ: 1 ngày
            backupCount=30,     # Giữ tối đa 30 file, cũ hơn sẽ tự xoá
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = "camera_ai") -> logging.Logger:
    """Get existing logger instance"""
    return logging.getLogger(name)