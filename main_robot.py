# /code/main_robot.py
# Entry point — Initializes shared I2C, OLED, and Qwiic Twist

import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
from oled_display import init_display
from twist_module import check_twist_events
import sparkfun_qwiictwist
import time

# 1. Release any preexisting display locks
displayio.release_displays()

# 2. Set up the shared I2C bus
i2c = busio.I2C(scl=board.SCL, sda=board.SDA)
while not i2c.try_lock():
    pass
try:
    devices = i2c.scan()
    print("🔍 I2C scan:", [hex(d) for d in devices])
finally:
    i2c.unlock()

# 3. Initialize OLED display
display = init_display(i2c)
if display is None:
    print("❌ OLED init failed")
    while True:
        pass

splash = displayio.Group()
display.root_group = splash

text_area = label.Label(terminalio.FONT, text="🤖 I'M ALIVE", x=10, y=64)
splash.append(text_area)

# 4. Initialize Qwiic Twist
try:
    twist = sparkfun_qwiictwist.Sparkfun_QwiicTwist(i2c)
    print("✅ Twist initialized")
except Exception as e:
    print("❌ Twist init failed:", e)
    twist = None
    text_area.text = "❌ TWIST NOT FOUND"
    while True:
        pass

# 5. Main loop to poll twist and update screen
last_position = twist.count if twist else 0

while True:
    if twist:
        event = check_twist_events(twist)
        if event:
            print("🎛️ Twist event:", event)
            new_text = f"Twist: {event}"
            if text_area.text != new_text:
                text_area.text = new_text

        new_position = twist.count
        if new_position != last_position:
            delta = new_position - last_position
            print(f"🔄 Twist moved: {new_position} (Δ {delta})")
            new_text = f"Rot: {new_position}"
            if text_area.text != new_text:
                text_area.text = new_text
            last_position = new_position

    time.sleep(0.05)
