"""
speed_pulse_reader.py

Speed Pulse Reader Module for Robot Control System

This module reads the speed pulse signals (one per motor) using pulseio.
Pin mappings are loaded exclusively from robot_config.txt.
It uses pulseio.PulseIn to measure pulse durations, which later can be used for
closed-loop (PID) control.
"""

import board
import pulseio
import time
from config_loader import load_config

# Load configuration parameters
config = load_config("robot_config.txt")

# Verify required configuration keys exist
required_keys = ["SPEED_PULSE_LEFT_PIN", "SPEED_PULSE_RIGHT_PIN"]
for key in required_keys:
    if key not in config:
        raise RuntimeError("Missing required config entry: {}".format(key))

# Retrieve pin names from config (no defaults)
LEFT_PULSE_PIN_NAME = config["SPEED_PULSE_LEFT_PIN"]
RIGHT_PULSE_PIN_NAME = config["SPEED_PULSE_RIGHT_PIN"]

# Initialize pulse input objects (maxlen can be adjusted as needed)
left_pulse_input = pulseio.PulseIn(getattr(board, LEFT_PULSE_PIN_NAME), maxlen=10, idle_state=True)
right_pulse_input = pulseio.PulseIn(getattr(board, RIGHT_PULSE_PIN_NAME), maxlen=10, idle_state=True)

def read_speed_pulse(pulse_input):
    """
    Reads pulse durations from a pulseio.PulseIn object.
    
    :param pulse_input: A pulseio.PulseIn instance.
    :return: The duration (in microseconds) of the first pulse, or None if no pulse is available.
    """
    pulse_input.clear()
    pulse_input.resume()
    time.sleep(0.05)  # Allow some time to accumulate pulse data
    if len(pulse_input) > 0:
        return pulse_input[0]
    return None

if __name__ == "__main__":
    print("Speed Pulse Reader Test: Monitoring left and right pulse durations.")
    try:
        while True:
            left_duration = read_speed_pulse(left_pulse_input)
            right_duration = read_speed_pulse(right_pulse_input)
            print("Left Pulse: {}, Right Pulse: {}".format(left_duration, right_duration))
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting Speed Pulse Reader Test.")
