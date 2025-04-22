# /wheel_test_harness.py
# Dual-wheel motor tester with NeoKey and Twist UI feedback
# hard-coded everything, not good for being modular
import time
import board
import pwmio
import digitalio
import displayio
from adafruit_display_text import label
from adafruit_displayio_sh1107 import SH1107
from adafruit_seesaw.neopixel import NeoPixel
from adafruit_seesaw.seesaw import Seesaw
from adafruit_neokey.neokey1x4 import NeoKey1x4

import busio
import adafruit_rgb_display.ssd1306 as ssd1306

# -- Constants --
BRAKE_ON = True
BRAKE_OFF = False
ENABLE_ON = True
ENABLE_OFF = False

# -- Shared I2C Setup --
displayio.release_displays()
i2c = busio.I2C(scl=board.IO9, sda=board.IO8)
while not i2c.try_lock():
    pass
found = i2c.scan()
i2c.unlock()

# -- NeoKey Setup --
neokey = NeoKey1x4(i2c, addr=0x30)
neokey_pixel = None
if 0x30 in found:
    try:
        neokey = NeoKey1x4(i2c_bus, addr=0x30)
        neokey_pixel = NeoPixel(neokey, 4, 0x1B)
        for i in range(4):
            neokey_pixel[i] = (0, 0, 0)
        neokey_pixel.brightness = 0.1
        print("✅ NeoKey initialized on 0x30")
    except Exception as e:
        print("❌ NeoKey init error:", e)
else:
    print("⚠️  NeoKey not found on I2C bus")

# -- Twist Setup --
twist = None
try:
    from adafruit_seesaw import seesaw, rotaryio, digitalio as ssdio
    twist = seesaw.Seesaw(i2c, addr=0x36)
    twist.pin_mode(24, ssdio.INPUT_PULLUP)  # button
    twist_pixel = NeoPixel(twist, 1, 0x0E)
    twist_pixel.brightness = 0.05
    twist_pixel[0] = (0, 0, 0)
    print("✅ Twist encoder ready on 0x36")
except Exception as e:
    print("⚠️  Twist encoder not found or failed init:", e)

# -- Display Setup --
displayio.release_displays()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3D)
display = SH1107(display_bus, width=128, height=128, rotation=90)
main_group = displayio.Group()
display.root_group = main_group
label_out = label.Label(terminalio.FONT, text="Starting...", x=0, y=8, line_spacing=1.25)
main_group.append(label_out)

def show(text):
    print(text)
    label_out.text = text

def wait_for_neokey(index=0):
    if not neokey:
        time.sleep(2)
        return
    while True:
        if neokey.digital_read(index) == False:
            while neokey.digital_read(index) == False:
                pass
            return
        time.sleep(0.05)

def wheel_test(name, pwm_pin, dir_pin, enable_pin, brake_pin):
    # Setup Pins
    pwm = pwmio.PWMOut(pwm_pin, frequency=2000, duty_cycle=0)
    dir_out = digitalio.DigitalInOut(dir_pin)
    dir_out.direction = digitalio.Direction.OUTPUT

    en = digitalio.DigitalInOut(enable_pin)
    en.direction = digitalio.Direction.OUTPUT
    en.value = ENABLE_ON

    brake = digitalio.DigitalInOut(brake_pin)
    brake.direction = digitalio.Direction.OUTPUT
    brake.value = BRAKE_OFF

    show(f"🔧 {name} ENABLE {enable_pin}\nPress to continue")
    wait_for_neokey()

    show(f"BRAKE OFF {brake_pin}\nCan you spin? Press")
    brake.value = BRAKE_OFF
    if neokey_pixel:
        neokey_pixel[0] = (0, 255, 0)
    wait_for_neokey()

    show(f"BRAKE ON {brake_pin}\nStill spin? Press")
    brake.value = BRAKE_ON
    if neokey_pixel:
        neokey_pixel[0] = (255, 0, 0)
    wait_for_neokey()

    show("Ramping PWM...")
    for duty in range(0, 65535, 4096):
        pwm.duty_cycle = duty
        print("Duty:", duty)
        if twist_pixel:
            twist_pixel[0] = (duty >> 8, 0, 255 - (duty >> 8))
        time.sleep(0.1)

    show("Holding 50%")
    pwm.duty_cycle = 32768
    time.sleep(2)

    show("Flip DIR LOW -> HIGH")
    dir_out.value = False
    wait_for_neokey()
    dir_out.value = True
    wait_for_neokey()

    show("Stopping PWM")
    pwm.duty_cycle = 0
    brake.value = BRAKE_ON
    if neokey_pixel:
        neokey_pixel[0] = (255, 0, 0)
    pwm.deinit()
    show(f"✅ {name} complete")
    time.sleep(1)

# Run both wheels
wheel_test("RIGHT WHEEL", board.D19, board.D16, board.D17, board.D15)
wheel_test("LEFT WHEEL", board.D13, board.D9, board.D10, board.D6)

show("🎉 All tests done")
if neokey_pixel:
    for i in range(4):
        neokey_pixel[i] = (0, 0, 255)
if twist_pixel:
    twist_pixel[0] = (0, 0, 255)
