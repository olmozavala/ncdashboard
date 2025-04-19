import time
import threading
from typing import Optional


class Logger:
    LEVELS = {"DEBUG": 10, "INFO": 20, "ERROR": 30}
    COLORS = {
        "DEBUG": "\033[94m",   # Blue
        "INFO": "\033[92m",    # Green
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"
    }

    def __init__(self, name: str, level: str = "DEBUG", use_colors: bool = True, thread_safe: bool = False):
        self.name = name
        self.level = self.LEVELS.get(level.upper(), 10)
        self.use_colors = use_colors
        self.lock = threading.Lock() if thread_safe else None

    def _log(self, level_name: str, message: str):
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
        self._log("DEBUG", message)

    def info(self, message: str):
        self._log("INFO", message)

    def error(self, message: str):
        self._log("ERROR", message)
