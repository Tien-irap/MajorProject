import inspect
import logging
import os
from logging.handlers import RotatingFileHandler
from fastapi import Request
from backend.app.core.config import settings
from typing import Optional

class LoggerConfig:
    """
    Logger configuration class to setup logging for the application.
    Provides structured logging with file rotation and console output.
    """
 
    def __init__(
        self, 
        env: int = 20, 
        logger_name: str = "ChessAnalyzer", 
        log_directory: str = "logs", 
        log_file: str = "app.log"
    ):
        """
        Initialize the logger configuration.
 
        Args:
            env (int): Logging level (10: DEBUG, 20: INFO, 30: WARNING, etc.).
            logger_name (str): Name of the logger.
            log_directory (str): Directory to store log files.
            log_file (str): Name of the log file.
        """
        try:
            self.logger_name = logger_name
            self.log_directory = os.path.abspath(log_directory)
            self.log_file_path = os.path.join(self.log_directory, log_file)
            self.env = env
            self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
 
            self.logger = logging.getLogger(self.logger_name)
            self.root_logger = logging.getLogger()
            self.setup_logging()
            self.setup_logger()
        except Exception as e:
            print(f"Failed to initialize logger: {str(e)}")
 
    def setup_logging(self):
        """
        Configure the basic logging settings.
        """
        try:
            if self.logger.hasHandlers():
                self.logger.handlers.clear()
            if self.root_logger.hasHandlers():
                self.root_logger.handlers.clear()
 
            self.logger.propagate = False
            self.logger.setLevel(self.env)
            self.root_logger.setLevel(20)
        except Exception as e:
            print(f"Failed to setup logging: {str(e)}")
 
    def setup_logger(self):
        """
        Setup the logger with file and console handlers.
        Uses rotating file handler to prevent log files from growing too large.
        """
        try:
            os.makedirs(self.log_directory, exist_ok=True)
 
            # File handler with rotation (20MB per file, 21 backup files)
            file_handler = RotatingFileHandler(
                self.log_file_path, 
                backupCount=21, 
                maxBytes=1024 * 1024 * 20, 
                encoding="utf-8"
            )
            file_handler.setLevel(self.env)
 
            # Console handler (WARNING and above)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(30)
 
            formatter = logging.Formatter(self.log_format)
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
 
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
 
            # Root logger handlers
            root_file_handler = RotatingFileHandler(
                self.log_file_path, 
                backupCount=21, 
                maxBytes=1024 * 1024 * 20, 
                encoding="utf-8"
            )
            root_file_handler.setLevel(self.env)
 
            root_console_handler = logging.StreamHandler()
            root_console_handler.setLevel(30)
 
            root_file_handler.setFormatter(formatter)
            root_console_handler.setFormatter(formatter)
 
            self.root_logger.addHandler(root_file_handler)
            self.root_logger.addHandler(root_console_handler)
        except Exception as e:
            print(f"Failed to setup logger handlers: {str(e)}")
 
    def define_logger(
        self,
        level: int,
        message: str,
        request: Optional[Request] = None,
        loggName: Optional["inspect.FrameInfo"] = None,
        pid: Optional[int] = None,
        body: Optional[str] = None,
        response: Optional[str] = None,
    ):
        """
        Write logs with detailed information.
 
        Args:
            level (int): Logging level (10: DEBUG, 20: INFO, 30: WARNING, etc.).
            message (str): Log message.
            request (Request, optional): FastAPI request object.
            loggName (FrameInfo, optional): File and function name from inspect.
            pid (int, optional): Process ID.
            body (str, optional): Request body as string.
            response (str, optional): Response data as string.
        """
        try:
            log_parts = {
                "IP": f"{request.client.host}" if request else None,
                "URL": f"{request.method} {request.url}" if request else None,
                "MESSAGE": message,
                "PID": str(pid) if pid is not None else None,
                "FILE": f"{loggName[1]}:{loggName[3]}" if loggName else None,
                "BODY": str(body) if body is not None else None,
                "RESPONSE": str(response) if response is not None else None,
            }
 
            txt = " - ".join(
                [f"{key}: {value}" for key, value in log_parts.items() if value is not None]
            )
 
            self.logger.log(level=level, msg=txt)
        except Exception as e:
            print(f"Failed to write logs: {str(e)}")
    
    # Convenience methods
    def info(self, message: str, **kwargs):
        """Log INFO level message."""
        self.define_logger(level=logging.INFO, message=message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log DEBUG level message."""
        self.define_logger(level=logging.DEBUG, message=message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log WARNING level message."""
        self.define_logger(level=logging.WARNING, message=message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log ERROR level message."""
        self.define_logger(level=logging.ERROR, message=message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log CRITICAL level message."""
        self.define_logger(level=logging.CRITICAL, message=message, **kwargs)

# Create global logger instance
logger = LoggerConfig(
    env=getattr(settings, 'LOGGER', 20),  # Default to INFO if not set
    logger_name="ChessAnalyzer", 
    log_directory="logs", 
    log_file="app.log"
)
