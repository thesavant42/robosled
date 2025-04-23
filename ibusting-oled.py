# ibusted-oled.py
# iBUS motor control scaffold built atop proven ibus_switch_tracker logic
# OLED + iBUS packet decoding and preparation for motor PWM output
# Author: savant42
# not stable yet

import board
import busio
import time
import displayio
import terminalio
import digitalio
from adafruit_display_text import label
from adafruit_displayio_sh1107 import SH1107
from ibus import IBUS

# === Pin Mappings ===
# Motor ESCs and Control Pins
PWM_LEFT_PIN = board.D13
DIR_LEFT_PIN = board.D9
STOP_LEFT_PIN = board.D10
BRAKE_PIN_LEFT = board.D6

PWM_RIGHT_PIN = board.D19
DIR_RIGHT_PIN = board.D16
BRAKE_PIN_RIGHT = board.D15
STOP_RIGHT_PIN = board.D17

# iBUS UART
IBUS_TX = board.TX
IBUS_RX = board.RX

# Display
OLED_I2C_ADDR = 0x3D

# === UART Setup ===
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

# === Display Setup ===
displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=OLED_I2C_ADDR)
display = SH1107(display_bus, width=128, height=128, rotation=90)
splash = displayio.Group()
display.root_group = splash

# OLED layout for CH1–CH10 + DIR_L/ DIR_R + BRAKE feedback
labels = []
prev_channels = [0] * 10
for i in range(10):
    x = 0
    y = i * 10
    lbl = label.Label(terminalio.FONT, text="", x=x, y=y, color=0xFFFFFF)
    splash.append(lbl)
    labels.append(lbl)

# Directional intent and brake status labels (now moved to bottom rows)
intent_label = label.Label(terminalio.FONT, text="", x=0, y=110, color=0xFFFFFF)
dir_label_left = label.Label(terminalio.FONT, text="", x=0, y=120, color=0xFFFFFF)
dir_label_right = label.Label(terminalio.FONT, text="", x=64, y=110, color=0xFFFFFF)
brake_label = label.Label(terminalio.FONT, text="", x=64, y=120, color=0xFFFFFF)

splash.append(intent_label)
splash.append(dir_label_left)
splash.append(dir_label_right)
splash.append(brake_label)

# Warmup packet discard logic
WARMUP_COUNT = 2
warmup_packets_seen = 0
ib_ready = False

# Brake pin definitions

def get_brake_status():
    return brakes_engaged

MOTORS_ARMED = False

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

# Scale CH3 (throttle) to 0–100% based on initial value at startup
last_ghost_warning = 0
ghost_ch3_val = None
ghost_repeat_count = 0
MAX_GHOST_REPEAT = 30
startup_throttle = None

# PWM initialization (motors default to 0% duty)
import pwmio

LEFT_PWM = pwmio.PWMOut(PWM_LEFT_PIN, frequency=2000, duty_cycle=0)
RIGHT_PWM = pwmio.PWMOut(PWM_RIGHT_PIN, frequency=2000, duty_cycle=0)

# Direction pin outputs
DIR_LEFT = digitalio.DigitalInOut(DIR_LEFT_PIN)
DIR_LEFT.direction = digitalio.Direction.OUTPUT
DIR_RIGHT = digitalio.DigitalInOut(DIR_RIGHT_PIN)
DIR_RIGHT.direction = digitalio.Direction.OUTPUT

# Track direction state for change detection
last_direction_str = ""
last_dir_left = None
last_dir_right = None

# Motor arming function
def maybe_activate_motors():
    if not MOTORS_ARMED:
        return

    LEFT_PWM.duty_cycle = 0
    RIGHT_PWM.duty_cycle = 0
    stop_left.value = True
    stop_right.value = True
    print("🟢 ESC ENABLED — STOP pins HIGH")

# Callback once iBUS packet is received
def on_servo(ch_data):
    global last_ghost_warning
    global warmup_packets_seen, ib_ready
    global brakes_engaged, prev_ch5, startup_throttle
    global last_direction_str, last_dir_left, last_dir_right

    if not ib_ready:
        warmup_packets_seen += 1
        if warmup_packets_seen >= WARMUP_COUNT:
            ib_ready = True
            print(f"⚠️ Discarded first {WARMUP_COUNT} packets. iBUS now live.")
        else:
            print(f"⏳ Warming up... (packet {warmup_packets_seen})")
        return

    ch5_val = ch_data[4] if len(ch_data) > 4 else 1500
    if ch5_val != prev_ch5:
        prev_ch5 = ch5_val
        if ch5_val < 1200:
            brakes_engaged = True
            brake_left.value = True
            brake_right.value = True
            brake_label.text = "BRAKE: ON"
            print("🛑 BRAKES ENGAGED")
        else:
            brakes_engaged = False
            brake_left.value = False
            brake_right.value = False
            brake_label.text = "BRAKE: OFF"
            print("✅ BRAKES RELEASED")

    if len(ch_data) >= 2:
        ch1_val = ch_data[0]
        ch2_val = ch_data[1]

        direction_str = "IDLE"
        left_forward = False
        right_forward = False

        if ch2_val > 1550:
            direction_str = "FORWARD"
            left_forward = True
            right_forward = True
        elif ch2_val < 1450:
            direction_str = "REVERSE"
            left_forward = False
            right_forward = False

        if ch1_val > 1550:
            direction_str += " + RIGHT BIAS"
            left_forward = True
            right_forward = False
        elif ch1_val < 1450:
            direction_str += " + LEFT BIAS"
            left_forward = False
            right_forward = True

        if (direction_str != last_direction_str or
            left_forward != last_dir_left or
            right_forward != last_dir_right):

            print(f"🧡 Intent: {direction_str}")
            print(f"🔁 LEFT DIR: {'FORWARD' if left_forward else 'REVERSE'}")
            print(f"🔁 RIGHT DIR: {'FORWARD' if right_forward else 'REVERSE'}")

            intent_label.text = f"INTENT: {direction_str}"
            dir_label_left.text = f"DIR_L: {'FWD' if left_forward else 'REV'}"
            dir_label_right.text = f"DIR_R: {'FWD' if right_forward else 'REV'}"

            last_direction_str = direction_str
            last_dir_left = left_forward
            last_dir_right = right_forward

        DIR_LEFT.value = not left_forward
        DIR_RIGHT.value = not right_forward

    if len(ch_data) >= 3:
        ch3_val = ch_data[2]
        global ghost_ch3_val, ghost_repeat_count, startup_throttle

        if startup_throttle is None:
            if ghost_ch3_val is None:
                ghost_ch3_val = ch3_val
                ghost_repeat_count = 1
            elif ch3_val == ghost_ch3_val:
                ghost_repeat_count += 1
            else:
                ghost_repeat_count = 1
                ghost_ch3_val = ch3_val

            if ghost_repeat_count >= MAX_GHOST_REPEAT and ch3_val != ghost_ch3_val:
                throttle_pct = (ch3_val - ghost_ch3_val) / 10
                if throttle_pct > 5:
                    startup_throttle = ch3_val
                    MOTORS_ARMED = True
                    maybe_activate_motors()
                    print(f"🧪 Startup throttle set baseline: {startup_throttle}")
                else:
                    print("⚠️ Throttle too low to arm — must exceed 5%")

        else:
            duty_pct = (ch3_val - startup_throttle) / 10
            duty_pct = max(0, min(100, duty_pct))
            if not hasattr(on_servo, "last_throttle_print") or time.monotonic() - on_servo.last_throttle_print > 0.2:
                print(f"🚀 Throttle raw={ch3_val}, mapped={duty_pct:.1f}%")
                on_servo.last_throttle_print = time.monotonic()

    any_change = False
    for i in range(10):
        if i >= len(ch_data):
            continue
        val = ch_data[i]
        changed = val != prev_channels[i]
        if changed:
            prev_channels[i] = val
            labels[i].text = f"CH{i+1}:{val}"
            labels[i].color = 0xFFFF00
            print(f"🎮 CH{i+1}: {val}")
            any_change = True
        else:
            labels[i].color = 0x888888
    if any_change:
        print("-" * 30)

ibus = IBUS(uart, sensor_types=[], servo_cb=on_servo)
ibus.start_loop()

print("🔧 ibusted-oled.py running. Waiting for iBUS packets...")
