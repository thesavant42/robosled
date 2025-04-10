# logger.py
"""
Logger Module for Robot Control System

This module provides logging functionality with adjustable log levels.
Logging levels:
  0 - ERROR
  1 - WARN
  2 - INFO (default)
  3 - DEBUG

The DEBUG_LEVEL is loaded from the configuration file (robot_config.txt).
Messages are printed with a timestamp using time.monotonic().

Usage:
  from logger import error, warn, info, debug

  error("This is an error message.")
  warn("This is a warning message.")
  info("This is an info message.")
  debug("This is a debug message.")
"""

import time
from config_loader import load_config

# Load configuration parameters
config = load_config("robot_config.txt")
# Retrieve DEBUG_LEVEL from config; default to "2" if not set.
DEBUG_LEVEL = int(config.get("DEBUG_LEVEL", "2"))

# Define log level constants
ERROR = 0
WARN = 1
INFO = 2
DEBUG = 3

def log(level, message):
    """
    Log a message if the provided level is <= DEBUG_LEVEL.
    The message is printed with a timestamp.

    :param level: Integer log level (0=ERROR, 1=WARN, 2=INFO, 3=DEBUG)
    :param message: The message string to log.
    """
    if level <= DEBUG_LEVEL:
        timestamp = time.monotonic()
        if level == ERROR:
            level_str = "ERROR"
        elif level == WARN:
            level_str = "WARN"
        elif level == INFO:
            level_str = "INFO"
        elif level == DEBUG:
            level_str = "DEBUG"
        else:
            level_str = "LOG"
        print("[{:.2f}] {}: {}".format(timestamp, level_str, message))

def error(message):
    """Log an ERROR level message."""
    log(ERROR, message)

def warn(message):
    """Log a WARN level message."""
    log(WARN, message)

def info(message):
    """Log an INFO level message."""
    log(INFO, message)

def debug(message):
    """Log a DEBUG level message."""
    log(DEBUG, message)

# For testing purposes, run this module to demonstrate logging functionality.
if __name__ == "__main__":
    error("This is an error test message.")
    warn("This is a warning test message.")
    info("This is an info test message.")
    debug("This is a debug test message.")
