# motor_control.py
"""
Motor Control Module for Robot Control System

This module interfaces with two ZS-X11H motor controllers, controlling:
  - PWM signal (for speed)
  - Direction (DIR)
  - Brake (BRAKE)

All required pin mappings and parameters are loaded from robot_config.txt.
Ensure that the configuration file has entries for all keys, e.g.:

  MOTOR_LEFT_PWM_PIN = D18
  MOTOR_LEFT_DIR_PIN = D19
  MOTOR_LEFT_BRAKE_PIN = D20
  MOTOR_RIGHT_PWM_PIN = D21
  MOTOR_RIGHT_DIR_PIN = D22
  MOTOR_RIGHT_BRAKE_PIN = D23
  TARGET_PWM_FREQUENCY = 2000
"""

import board
import pwmio
from digitalio import DigitalInOut, Direction
from config_loader import load_config

# Load configuration parameters
config = load_config("robot_config.txt")

# Ensure all required configuration keys exist
required_keys = [
    "MOTOR_LEFT_PWM_PIN", "MOTOR_LEFT_DIR_PIN", "MOTOR_LEFT_BRAKE_PIN",
    "MOTOR_RIGHT_PWM_PIN", "MOTOR_RIGHT_DIR_PIN", "MOTOR_RIGHT_BRAKE_PIN",
    "TARGET_PWM_FREQUENCY"
]
for key in required_keys:
    if key not in config:
        raise RuntimeError("Missing required config entry: {}".format(key))

# Retrieve pin names from the configuration file (no defaults)
MOTOR_LEFT_PWM_PIN_NAME = config["MOTOR_LEFT_PWM_PIN"]
MOTOR_LEFT_DIR_PIN_NAME = config["MOTOR_LEFT_DIR_PIN"]
MOTOR_LEFT_BRAKE_PIN_NAME = config["MOTOR_LEFT_BRAKE_PIN"]

MOTOR_RIGHT_PWM_PIN_NAME = config["MOTOR_RIGHT_PWM_PIN"]
MOTOR_RIGHT_DIR_PIN_NAME = config["MOTOR_RIGHT_DIR_PIN"]
MOTOR_RIGHT_BRAKE_PIN_NAME = config["MOTOR_RIGHT_BRAKE_PIN"]

TARGET_PWM_FREQUENCY = int(config["TARGET_PWM_FREQUENCY"])

# Initialize PWM outputs for motor speed control
motor_left_pwm = pwmio.PWMOut(getattr(board, MOTOR_LEFT_PWM_PIN_NAME),
                              frequency=TARGET_PWM_FREQUENCY,
                              duty_cycle=0)
motor_right_pwm = pwmio.PWMOut(getattr(board, MOTOR_RIGHT_PWM_PIN_NAME),
                               frequency=TARGET_PWM_FREQUENCY,
                               duty_cycle=0)

# Initialize digital outputs for direction and brake control
motor_left_dir = DigitalInOut(getattr(board, MOTOR_LEFT_DIR_PIN_NAME))
motor_left_dir.direction = Direction.OUTPUT
motor_left_brake = DigitalInOut(getattr(board, MOTOR_LEFT_BRAKE_PIN_NAME))
motor_left_brake.direction = Direction.OUTPUT

motor_right_dir = DigitalInOut(getattr(board, MOTOR_RIGHT_DIR_PIN_NAME))
motor_right_dir.direction = Direction.OUTPUT
motor_right_brake = DigitalInOut(getattr(board, MOTOR_RIGHT_BRAKE_PIN_NAME))
motor_right_brake.direction = Direction.OUTPUT

def set_motor_speed(motor_pwm, speed_value):
    """
    Set motor speed via PWM duty cycle.
    
    :param motor_pwm: PWMOut object controlling the motor.
    :param speed_value: An integer between 0 (stop) and 65535 (full speed).
    """
    if speed_value < 0:
        speed_value = 0
    elif speed_value > 65535:
        speed_value = 65535
    motor_pwm.duty_cycle = speed_value

def set_motor_direction(motor_dir, forward=True):
    """
    Set motor direction.
    
    :param motor_dir: Digital output controlling motor direction.
    :param forward: Boolean; True for forward, False for reverse.
    """
    motor_dir.value = forward

def engage_brake(motor_brake, engage=True):
    """
    Engage or release the brake.
    
    :param motor_brake: Digital output controlling the brake.
    :param engage: Boolean; True to engage the brake, False to release.
    """
    motor_brake.value = engage

def control_left_motor(speed, forward=True, brake=False):
    """
    Control the left motor.
    
    :param speed: PWM speed (0 to 65535).
    :param forward: Direction (True = forward, False = reverse).
    :param brake: Brake state (True = engage brake).
    """
    set_motor_speed(motor_left_pwm, speed)
    set_motor_direction(motor_left_dir, forward)
    engage_brake(motor_left_brake, brake)

def control_right_motor(speed, forward=True, brake=False):
    """
    Control the right motor.
    
    :param speed: PWM speed (0 to 65535).
    :param forward: Direction (True = forward, False = reverse).
    :param brake: Brake state (True = engage brake).
    """
    set_motor_speed(motor_right_pwm, speed)
    set_motor_direction(motor_right_dir, forward)
    engage_brake(motor_right_brake, brake)

# For testing purposes, run this module to demonstrate motor control.
if __name__ == "__main__":
    import time
    print("Motor Control Test: Ramping Left Motor Up, then braking.")
    for i in range(0, 65536, 5000):
        control_left_motor(i, forward=True, brake=False)
        print("Left motor speed set to:", i)
        time.sleep(0.2)
    print("Engaging brake on left motor.")
    control_left_motor(0, forward=True, brake=True)
    time.sleep(1)
    print("Releasing brake on left motor.")
    control_left_motor(0, forward=True, brake=False)
    print("Test complete.")
