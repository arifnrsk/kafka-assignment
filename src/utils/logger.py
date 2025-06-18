"""
Logging Configuration Module
Provides structured logging with colors and proper formatting
"""
import logging
import sys
from pathlib import Path
from typing import Optional
import colorlog
from decouple import config


class KafkaLogger:
    """Custom logger for Kafka application"""
    
    def __init__(self, name: str, log_level: Optional[str] = None):
        self.name = name
        self.log_level = log_level or config('APP_LOG_LEVEL', default='INFO')
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with file and console handlers"""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.log_level.upper()))
        
        # Prevent duplicate logs
        if logger.handlers:
            logger.handlers.clear()
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Console handler with colors
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Color formatter for console
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler
        file_handler = logging.FileHandler(
            logs_dir / f"{self.name.lower().replace('.', '_')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        # File formatter
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def get_logger(self) -> logging.Logger:
        """Get configured logger instance"""
        return self.logger


def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """Convenience function to get a logger"""
    kafka_logger = KafkaLogger(name, log_level)
    return kafka_logger.get_logger()


# Application loggers
producer_logger = get_logger('producer')
consumer_logger = get_logger('consumer')
config_logger = get_logger('config')
processor_logger = get_logger('processor') 