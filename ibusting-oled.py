# ibusted-oled.py
# iBUS motor control scaffold built atop proven ibus_switch_tracker logic
# OLED + iBUS packet decoding and preparation for motor PWM output
# Author: savant42
#
# ⚠️ NOTE: When using methods like ibus.read or ibus.channels,
# always call them with parentheses (e.g., ibus.read()) if it's a method,
# but avoid () for properties like ibus.channels.
# Lib: https://raw.githubusercontent.com/house4hack/circuitpython-ibus/refs/heads/master/python/ibus.py
# example script from author: https://github.com/house4hack/circuitpython-ibus/blob/master/python/main.py

import board
import busio
import time
import displayio
import terminalio
import digitalio
from adafruit_display_text import label
from adafruit_displayio_sh1107 import SH1107
from ibus import IBUS
import pwmio

# === Pin Mappings ===
PWM_LEFT_PIN = board.D13
DIR_LEFT_PIN = board.D9
STOP_LEFT_PIN = board.D10
BRAKE_PIN_LEFT = board.D6

PWM_RIGHT_PIN = board.D19
DIR_RIGHT_PIN = board.D16
BRAKE_PIN_RIGHT = board.D15
STOP_RIGHT_PIN = board.D17

IBUS_TX = board.TX
IBUS_RX = board.RX
OLED_I2C_ADDR = 0x3D

print("📱 Initializing UART...")
uart = busio.UART(
    tx=IBUS_TX,
    rx=IBUS_RX,
    baudrate=115200,
    bits=8,
    parity=None,
    stop=2,
    timeout=0.01,
    receiver_buffer_size=512
)
uart.reset_input_buffer()
print("✅ UART ready. Flushing initial iBUS packets...")

# ✅ Fix: wrap read in a lambda that ensures iterable output
ibus = IBUS(uart, lambda: uart.read(32) or b"", lambda: uart.in_waiting > 0)

# === Display Setup ===
displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=OLED_I2C_ADDR)
display = SH1107(display_bus, width=128, height=128, rotation=90)
splash = displayio.Group()
display.root_group = splash

labels = []
prev_channels = [0] * 10
for i in range(4):
    x = 0
    y = i * 10
    lbl = label.Label(terminalio.FONT, text="", x=x, y=y, color=0xFFFFFF)
    splash.append(lbl)
    labels.append(lbl)

switch_label = label.Label(terminalio.FONT, text="", x=0, y=40, color=0xFFFFFF)
splash.append(switch_label)

intent_label = label.Label(terminalio.FONT, text="", x=0, y=60, color=0xFFFFFF)
dir_label_left = label.Label(terminalio.FONT, text="", x=0, y=70, color=0xFFFFFF)
dir_label_right = label.Label(terminalio.FONT, text="", x=0, y=80, color=0xFFFFFF)

splash.append(intent_label)
splash.append(dir_label_left)
splash.append(dir_label_right)

WARMUP_COUNT = 2
warmup_packets_seen = 0
ib_ready = False

stop_left = digitalio.DigitalInOut(STOP_LEFT_PIN)
stop_left.direction = digitalio.Direction.OUTPUT
stop_left.value = False

stop_right = digitalio.DigitalInOut(STOP_RIGHT_PIN)
stop_right.direction = digitalio.Direction.OUTPUT
stop_right.value = False

brake_left = digitalio.DigitalInOut(BRAKE_PIN_LEFT)
brake_left.direction = digitalio.Direction.OUTPUT
brake_left.value = False

brake_right = digitalio.DigitalInOut(BRAKE_PIN_RIGHT)
brake_right.direction = digitalio.Direction.OUTPUT
brake_right.value = False

brakes_engaged = False
prev_ch5 = 1500

MOTORS_ARMED = False
last_arm_warning = 0
last_throttle_print = 0

def get_brake_status():
    return brakes_engaged

LEFT_PWM = pwmio.PWMOut(PWM_LEFT_PIN, frequency=2000, duty_cycle=0)
RIGHT_PWM = pwmio.PWMOut(PWM_RIGHT_PIN, frequency=2000, duty_cycle=0)

DIR_LEFT = digitalio.DigitalInOut(DIR_LEFT_PIN)
DIR_LEFT.direction = digitalio.Direction.OUTPUT
DIR_LEFT.value = False

DIR_RIGHT = digitalio.DigitalInOut(DIR_RIGHT_PIN)
DIR_RIGHT.direction = digitalio.Direction.OUTPUT
DIR_RIGHT.value = True

print(f"🔧 DIR_LEFT initialized to {'HIGH' if DIR_LEFT.value else 'LOW'}")
print(f"🔧 DIR_RIGHT initialized to {'HIGH' if DIR_RIGHT.value else 'LOW'}")

last_direction_str = ""
last_dir_left = None
last_dir_right = None

def maybe_activate_motors():
    if not MOTORS_ARMED:
        return
    stop_left.value = True
    stop_right.value = True
    print("🟢 ESC ENABLED — STOP pins HIGH")
    print(f"    🚦 stop_left = {stop_left.value}")
    print(f"    🚦 stop_right = {stop_right.value}")

def on_servo(ch_data):
    global warmup_packets_seen, ib_ready
    global brakes_engaged, prev_ch5
    global MOTORS_ARMED

    print(f"📦 on_servo called with: {ch_data}")

    if not isinstance(ch_data, (list, tuple)):
        print(f"❌ Error: ch_data is not iterable — {type(ch_data)}")
        return

    if not ib_ready:
        warmup_packets_seen += 1
        if warmup_packets_seen >= WARMUP_COUNT:
            ib_ready = True
            print(f"⚠️ Discarded first {WARMUP_COUNT} packets. iBUS now live.")
        else:
            print(f"⏳ Warming up... (packet {warmup_packets_seen})")
        return

    if MOTORS_ARMED:
        maybe_activate_motors()

    ch5_val = ch_data[4] if len(ch_data) > 4 else 1500
    if ch5_val != prev_ch5:
        prev_ch5 = ch5_val
        if ch5_val < 1200:
            brakes_engaged = True
            brake_left.value = True
            brake_right.value = True
            print("🛑 BRAKES ENGAGED")
        else:
            brakes_engaged = False
            brake_left.value = False
            brake_right.value = False
            print("✅ BRAKES RELEASED")

# Main loop
while True:
    packet = ibus.read()
    if packet:
        channels = ibus.channels  # ✅ FIXED: use property, not method call
        on_servo(channels)

        for i in range(min(len(channels), 4)):
            val = channels[i]
            if val != prev_channels[i]:
                labels[i].text = f"🎮 CH{i+1}: {val}"
                prev_channels[i] = val

        time.sleep(0.01)
