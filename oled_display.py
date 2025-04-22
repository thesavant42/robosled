# /code/oled_display.py
# SH1107 OLED init function — expects external I2C bus
# 📌 DEVICE ADDRESS IS 0x3D — SET BY HARDWARE, DO NOT ASSUME
# 📐 ROTATION IS 90 — NEVER USE 270
# confirmed working as of 13:00 04/22/2025
# no SCL in use bug

import displayio
from adafruit_displayio_sh1107 import SH1107

def init_display(i2c):
    displayio.release_displays()
    try:
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3D)
        display = SH1107(
            display_bus,
            width=128,
            height=128,
            rotation=90
        )
        return display
    except Exception as e:
        return None  # Caller is responsible for error reporting and fallback

# invoke like:
#   splash = displayio.Group()
#   display.root_group = splash

