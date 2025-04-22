# /main_robot.py
# Drive controller with IBUS + Brake state machine + OLED + Speed Pulse RPM
# Author: savant42

import time
import board
import pwmio
import digitalio
import displayio
import busio
import terminalio

from adafruit_display_text import label
from adafruit_displayio_sh1107 import SH1107
from ibus_receiver import get_channel_raw
from motor_driver import MotorController
from speed_pulse_reader import get_rpm  # Import RPM reader

# --- Constants ---
BRAKE_FORCED_ON = 0
BRAKE_SWITCH_CONTROLLED = 1
BRAKE_FORCED_OFF = 2

SWITCH_CHANNEL = 5  # SWA
BRAKE_TOGGLE_CHANNEL = 6  # SWB to change brake mode (optional)

# --- Brake State ---
brake_mode = BRAKE_SWITCH_CONTROLLED
brake_engaged = False

# --- I2C + OLED Display ---
oled_ready = False
oled_lines = []

try:
    i2c = busio.I2C(scl=board.IO9, sda=board.IO8)
    while not i2c.try_lock():
        pass
    i2c.unlock()

    display_bus = displayio.I2CDisplay(i2c, device_address=0x3D)
    display = SH1107(display_bus, width=128, height=128, rotation=270)
    splash = displayio.Group()
    display.root_group = splash

    oled_lines = [
        label.Label(terminalio.FONT, text="Line 1", x=0, y=10),
        label.Label(terminalio.FONT, text="Line 2", x=0, y=25),
        label.Label(terminalio.FONT, text="Line 3", x=0, y=40),
        label.Label(terminalio.FONT, text="Line 4", x=0, y=55),
    ]
    for line in oled_lines:
        splash.append(line)

    oled_ready = True
    print("[OLED] Display initialized successfully")

except Exception as e:
    print(f"[OLED ERROR] Could not initialize display: {e}")
    oled_ready = False

def oled_log(lines):
    if not oled_ready:
        return
    for i in range(min(4, len(lines))):
        oled_lines[i].text = lines[i]
    print(" | ".join(lines))

# --- Utility: Clamp ---
def clamp(value, minimum=-100, maximum=100):
    return max(min(value, maximum), minimum)

# --- Channel Scaling ---
def scale_channel_to_percent(raw_val, center=1500, deadzone=5, scale=500):
    """
    Maps a raw IBUS channel value (e.g., 1000–2000) to -100 to +100%
    with clamping and deadzone handling.
    """
    delta = raw_val - center
    if abs(delta) < deadzone:
        return 0
    percent = (delta / scale) * 100
    return clamp(percent)

# --- Motor Setup ---
left_motor = MotorController(pwm_pin=board.D17, dir_pin=board.D20, brake_pin=board.D15, enable_pin=board.D18, forward_is_low=False)
right_motor = MotorController(pwm_pin=board.D9, dir_pin=board.D10, brake_pin=board.D6, enable_pin=board.D8, forward_is_low=True)

def set_brake_mode(mode):
    global brake_mode
    brake_mode = mode

def apply_brakes(engaged):
    global brake_engaged
    brake_engaged = engaged
    left_motor.set_brake(engaged)
    right_motor.set_brake(engaged)

def update_brakes(ch5_switch):
    # Three-way control logic
    if brake_mode == BRAKE_FORCED_ON:
        apply_brakes(True)
        return "FORCED_ON"
    elif brake_mode == BRAKE_FORCED_OFF:
        apply_brakes(False)
        return "FORCED_OFF"
    else:
        apply_brakes(ch5_switch)
        return "SWITCH:%s" % ("ON" if ch5_switch else "OFF")

# --- Main Loop ---
print("[RUNNING] Robot control active")
oled_log(["Robot Ready", "CH2 = Throttle", "CH4 = Pivot", "SWA = Brake"])

while True:
    raw_ch2 = get_channel_raw(2)  # throttle forward/reverse
    raw_ch4 = get_channel_raw(4)  # pivot
    raw_ch5 = get_channel_raw(5)  # SWA
    raw_ch6 = get_channel_raw(6)  # SWB

    ch2 = scale_channel_to_percent(raw_ch2)
    ch4 = scale_channel_to_percent(raw_ch4)
    ch5_switch = raw_ch5 > 1500
    ch6_val = scale_channel_to_percent(raw_ch6)

    print(f"✅ Throttle: {raw_ch2} → {ch2:+.0f}%")

    # Optional: use CH6 as toggle input for brake_mode
    if ch6_val > 90:
        set_brake_mode(BRAKE_FORCED_OFF)
    elif ch6_val < -90:
        set_brake_mode(BRAKE_FORCED_ON)
    else:
        set_brake_mode(BRAKE_SWITCH_CONTROLLED)

    # Brake logic
    brake_state = update_brakes(ch5_switch)

    # Directional logic (safe reverse only when idle)
    if ch2 > 0:
        left_motor.forward(duty=ch2)
        right_motor.forward(duty=ch2)
    elif ch2 < 0:
        left_motor.reverse(duty=abs(ch2))
        right_motor.reverse(duty=abs(ch2))
    else:
        left_motor.stop()
        right_motor.stop()

    # Pivot logic layers on top of throttle
    if ch4 > 50:
        left_motor.reverse(duty=abs(ch4))
        right_motor.forward(duty=abs(ch4))
    elif ch4 < -50:
        left_motor.forward(duty=abs(ch4))
        right_motor.reverse(duty=abs(ch4))

    # --- Speed Pulse RPM ---
    rpm = get_rpm()  # Pull latest RPM reading from speed pulse reader

    oled_log([
        f"Throttle: {ch2:+.0f}%",
        f"Pivot:    {ch4:+.0f}%",
        f"Brake:    {brake_state}",
        f"RPM:      {rpm:.0f}"
    ])

    print(f"[RPM] Measured speed: {rpm:.2f} RPM")
    time.sleep(0.05)
