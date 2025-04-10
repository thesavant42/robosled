# manual_overrides.py
"""
Manual Overrides Module for Robot Control System

This module reads digital inputs for manual override switches:
  - Left STOP button
  - Right STOP button
  - Global BRAKE switch

All required pin mappings are loaded from the configuration file (robot_config.txt).
Each pin must be defined in the config file. This module assumes active-low logic,
where pressing the button pulls the line low.
"""

import board
from digitalio import DigitalInOut, Direction, Pull
from config_loader import load_config

# Load configuration parameters
config = load_config("robot_config.txt")

# Verify that all required configuration keys exist
required_keys = [
    "MANUAL_STOP_LEFT_PIN",
    "MANUAL_STOP_RIGHT_PIN",
    "MANUAL_BRAKE_PIN"
]
for key in required_keys:
    if key not in config:
        raise RuntimeError("Missing required config entry: {}".format(key))

# Retrieve pin names from config (no hard-coded defaults)
manual_stop_left_pin_name = config["MANUAL_STOP_LEFT_PIN"]
manual_stop_right_pin_name = config["MANUAL_STOP_RIGHT_PIN"]
manual_brake_pin_name = config["MANUAL_BRAKE_PIN"]

# Initialize digital inputs for manual override switches
# Assumes pull-ups are needed (active-low buttons)
manual_stop_left = DigitalInOut(getattr(board, manual_stop_left_pin_name))
manual_stop_left.direction = Direction.INPUT
manual_stop_left.pull = Pull.UP

manual_stop_right = DigitalInOut(getattr(board, manual_stop_right_pin_name))
manual_stop_right.direction = Direction.INPUT
manual_stop_right.pull = Pull.UP

manual_brake = DigitalInOut(getattr(board, manual_brake_pin_name))
manual_brake.direction = Direction.INPUT
manual_brake.pull = Pull.UP

def is_manual_stop_left_active():
    """
    Check if the left manual STOP button is active.
    
    Returns:
        bool: True if pressed (active-low), False otherwise.
    """
    return not manual_stop_left.value  # Button pressed if low

def is_manual_stop_right_active():
    """
    Check if the right manual STOP button is active.
    
    Returns:
        bool: True if pressed (active-low), False otherwise.
    """
    return not manual_stop_right.value

def is_manual_brake_active():
    """
    Check if the global manual BRAKE switch is active.
    
    Returns:
        bool: True if engaged (active-low), False otherwise.
    """
    return not manual_brake.value

# For testing purposes, run this module to display the override states.
if __name__ == "__main__":
    import time
    print("Manual Overrides Module Test:")
    print("Press the buttons (active-low) to see states change.")
    try:
        while True:
            left_state = is_manual_stop_left_active()
            right_state = is_manual_stop_right_active()
            brake_state = is_manual_brake_active()
            print("Left STOP: {}, Right STOP: {}, BRAKE: {}".format(
                left_state, right_state, brake_state))
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting Manual Overrides Test.")
