# /motor_controller.py
# Author: savant42
# zs-x11h motor controller for CircuitPython 9.2

import pwmio
import digitalio
import board

class MotorController:
    def __init__(self, pwm_pin, dir_pin, reverse=False):
        self.pwm = pwmio.PWMOut(pwm_pin, frequency=2000, duty_cycle=0)
        self.dir = digitalio.DigitalInOut(dir_pin)
        self.dir.direction = digitalio.Direction.OUTPUT
        self.reverse = reverse

    def set_speed(self, speed_percent):
        speed_percent = max(0, min(100, speed_percent))
        self.pwm.duty_cycle = int(speed_percent * 65535 / 100)

    def forward(self):
        self.dir.value = not self.reverse

    def backward(self):
        self.dir.value = self.reverse

    def stop(self):
        self.pwm.duty_cycle = 0
