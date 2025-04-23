"""
Logger Utility Module

This module provides a simple logging system with color-coded output and thread safety.
It supports different log levels (DEBUG, INFO, ERROR) and can be configured for
thread-safe operation when needed.
"""

import time
import threading
from typing import Optional


class Logger:
    """
    A simple logging class with color-coded output and thread safety support.
    
    Attributes:
        LEVELS (dict): Mapping of log level names to their numeric values
        COLORS (dict): ANSI color codes for different log levels
    """
    
    # Log level definitions
    LEVELS = {"DEBUG": 10, "INFO": 20, "ERROR": 30}
    
    # ANSI color codes for terminal output
    COLORS = {
        "DEBUG": "\033[94m",   # Blue
        "INFO": "\033[92m",    # Green
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"
    }

    def __init__(self, name: str, level: str = "DEBUG", use_colors: bool = True, thread_safe: bool = False):
        """
        Initialize the logger.
        
        Args:
            name (str): Name of the logger (typically module name)
            level (str, optional): Minimum log level to display. Defaults to "DEBUG"
            use_colors (bool, optional): Whether to use colored output. Defaults to True
            thread_safe (bool, optional): Whether to use thread-safe logging. Defaults to False
        """
        self.name = name
        self.level = self.LEVELS.get(level.upper(), 10)
        self.use_colors = use_colors
        self.lock = threading.Lock() if thread_safe else None

    def _log(self, level_name: str, message: str):
        """
        Internal method to handle the actual logging.
        
        Args:
            level_name (str): Name of the log level
            message (str): Message to log
        """
        if self.LEVELS[level_name] < self.level:
            return

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        level_tag = f"[{level_name}]"
        color_prefix = self.COLORS[level_name] if self.use_colors else ""
        color_reset = self.COLORS["RESET"] if self.use_colors else ""

        formatted_message = f"{timestamp} {color_prefix}{level_tag}{color_reset} {self.name}: {message}"

        if self.lock:
            with self.lock:
                print(formatted_message)
        else:
            print(formatted_message)

    def debug(self, message: str):
        """
        Log a debug message.
        
        Args:
            message (str): Debug message to log
        """
        self._log("DEBUG", message)

    def info(self, message: str):
        """
        Log an info message.
        
        Args:
            message (str): Info message to log
        """
        self._log("INFO", message)

    def error(self, message: str):
        """
        Log an error message.
        
        Args:
            message (str): Error message to log
        """
        self._log("ERROR", message)
