"""
main.py

Main Orchestrator for Robot Control System

This module ties together the configuration, RC receiver, manual overrides,
motor control, speed pulse feedback, and logging. It continuously processes
RC commands, checks for manual overrides, and drives the two ZS-X11H motor
controllers accordingly. Debug information is logged based on the configured
DEBUG_LEVEL.
"""

import time
from config_loader import load_config
from logger import info, debug, error
from rc_receiver import SBusReceiver, uart
from motor_control import control_left_motor, control_right_motor
from manual_overrides import is_manual_stop_left_active, is_manual_stop_right_active, is_manual_brake_active
from speed_pulse_reader import read_speed_pulse, left_pulse_input, right_pulse_input

# Load the configuration file
config = load_config("robot_config.txt")
info("Configuration loaded.")

# Initialize the S-Bus receiver (for RC input)
receiver = SBusReceiver(uart)
info("S-Bus receiver initialized.")

def main():
    info("Starting main control loop.")
    while True:
        # Read RC channels from the S-Bus receiver.
        channels = receiver.get_channels()
        if channels:
            debug("RC Channels: {}".format(channels))
            # --- Mapping RC channels to motor commands ---
            # For this example, we assume:
            #   Channel 0 controls left motor throttle.
            #   Channel 1 controls right motor throttle.
            # A proper conversion (scaling, deadzone, etc.) should be applied.
            # Here, the raw 11-bit values (0-2047) are scaled to 0-65535 for PWM.
            left_speed = int((channels[0] / 2047.0) * 65535)
            right_speed = int((channels[1] / 2047.0) * 65535)
        else:
            debug("No valid RC frame received. Setting motors to stop.")
            left_speed = 0
            right_speed = 0

        # Check manual override inputs.
        if is_manual_stop_left_active():
            info("Left manual STOP activated.")
            left_speed = 0
        if is_manual_stop_right_active():
            info("Right manual STOP activated.")
            right_speed = 0

        # Check global manual BRAKE.
        if is_manual_brake_active():
            info("Global BRAKE activated. Engaging brakes.")
            left_brake = True
