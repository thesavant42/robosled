# config.py
# Pin configuration for ZS-X11H motor tester
# Author: savant42
import board
# Define the pin mappings for the motors
MOTOR_CONFIG = {
    'LEFT': {
        'name': 'Left Wheel',
        'PWM': board.D13,       # aka IO11
        'DIR': board.D9,        # aka IO1
        'STOP': board.D10,      # aka IO3
        'BRAKE': board.D6,      # aka IO38
        'PULSE': board.D12,     # aka IO10
        'FWD': True,
        'DESIRED_DIR': 'FWD'
    },
    'RIGHT': {
        'name': 'Right Wheel',
        'PWM': board.D19,       # aka IO5
        'DIR': board.D16,       # aka IO14
        'STOP': board.D17,      # aka IO12
        'BRAKE': board.D15,     # aka IO18
        'PULSE': board.D18,     # aka IO16
        'FWD': False,
        'DESIRED_DIR': 'FWD'
    }
}    
