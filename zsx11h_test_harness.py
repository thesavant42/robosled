# zsx11h_test_harness.py
# Manual ZS-X11H motor tester for Left/Right/Both wheels with feedback logging and enhanced menu flow
# Author: savant42

import board
import digitalio
import pwmio
import time
import os
import rtc
import supervisor
import countio

# === Pin Map with Forward Logic, Speed Pulse, and Desired Start State ===
LEFT = {
    'name': 'Left Wheel',
    'PWM': board.D13,
    'DIR': board.D9,
    'STOP': board.D10,
    'BRAKE': board.D6,
    'PULSE': board.D12,
    'FWD': True,
    'DESIRED_DIR': 'FWD'
}

RIGHT = {
    'name': 'Right Wheel',
    'PWM': board.D19,
    'DIR': board.D16,
    'STOP': board.D17,
    'BRAKE': board.D15,
    'PULSE': board.D14,
    'FWD': False,
    'DESIRED_DIR': 'FWD'
}

# Track existing resources to avoid reinitialization errors
last_pwm = None
last_dir = None
last_stop = None
last_brake = None

# === Setup IO ===
def setup_device(device):
    global last_pwm, last_dir, last_stop, last_brake
    print(f"\nDEVICE: {device['name']}")
    for key in ['PWM', 'DIR', 'STOP', 'BRAKE', 'PULSE']:
        print(f" {key}: {device[key]}")
    print(f" FWD = {'HIGH' if device['FWD'] else 'LOW'}")

    if last_pwm:
        last_pwm.deinit()
    if last_dir:
        last_dir.deinit()
    if last_stop:
        last_stop.deinit()
    if last_brake:
        last_brake.deinit()

    pwm = pwmio.PWMOut(device['PWM'], frequency=2000, duty_cycle=0)
    last_pwm = pwm

    dir_pin = digitalio.DigitalInOut(device['DIR'])
    dir_pin.direction = digitalio.Direction.OUTPUT
    last_dir = dir_pin

    if device['DESIRED_DIR'] == 'FWD':
        dir_pin.value = device['FWD']
    else:
        dir_pin.value = not device['FWD']

    stop = digitalio.DigitalInOut(device['STOP'])
    stop.direction = digitalio.Direction.OUTPUT
    stop.value = False
    last_stop = stop

    brake = digitalio.DigitalInOut(device['BRAKE'])
    brake.direction = digitalio.Direction.OUTPUT
    brake.value = False
    last_brake = brake

    pulse = device['PULSE']

    print(f"[INIT] {device['name']} — DIR: {'FORWARD' if dir_pin.value == device['FWD'] else 'REVERSE'}, BRAKE: {'ENGAGED' if brake.value else 'RELEASED'}, STOP: {stop.value}")

    return pwm, dir_pin, stop, brake, pulse

# === Menu System ===
def print_device_status(device, dir_pin, stop, brake, pulse):
    print(f"\n[{device['name']}] STATUS")
    print(f" DIR: {'FORWARD' if dir_pin.value == device['FWD'] else 'REVERSE'}")
    print(f" BRAKE: {'ENGAGED' if brake.value else 'RELEASED'}")
    print(f" STOP (Enable): {'HIGH' if stop.value else 'LOW'}")
    print(f" FWD logic: {'HIGH' if device['FWD'] else 'LOW'}")

def sniff_pulse_pin_active(device):
    print(f"\n🔍 Starting single-pin pulse scan for {device['name']}...")

    candidate_pins = [board.IO6]    # IO6 Right Wheel, IO10 Left
    duration = 10

    brake = last_brake
    stop = last_stop
    pwm = last_pwm

    for pin in candidate_pins:
        print(f"\n🚦 Testing pin {pin} for {duration} seconds...")

        try:
            counter = countio.Counter(pin, edge=countio.Edge.RISE)
            brake.value = False
            pwm.duty_cycle = 0
            stop.value = True
            time.sleep(0.2)
            pwm.duty_cycle = int(60 * 655.35)
            print(f"[RUN] Motor active. Sampling {pin}...")

            start = time.monotonic()
            last = 0
            while time.monotonic() - start < duration:
                now = counter.count
                if now > last:
                    print(f" 🌀 {now - last} edge(s) — total = {now}")
                    last = now
                time.sleep(0.5)

            pwm.duty_cycle = 0
            brake.value = True
            stop.value = False
            print(f"[DONE] {counter.count} rising edges detected on pin {pin}. Motor stopped.\n")
            counter.deinit()
            break

        except Exception as e:
            print(f" ⚠️ Skipping pin {pin}: {e}")

def wheel_test_menu(device, pwm, dir_pin, stop, brake, pulse):
    while True:
        print(f"\n{device['name']} Test Menu:")
        print(" [1] Toggle BRAKE")
        print(" [2] Toggle DIR")
        print(" [3] Toggle STOP (ESC Enable)")
        print(" [4] PWM Duty Cycle Ramp")
        print(" [5] Pulse Pin Activity Scan (motor spins)")
        print(" [6] Back to device selection")
        choice = input("> ").strip()

        if choice == "1":
            brake.value = not brake.value
            print(f"[BRAKE] {'ENGAGED' if brake.value else 'RELEASED'}")
        elif choice == "2":
            dir_pin.value = not dir_pin.value
            print(f"[DIR] Now {'FORWARD' if dir_pin.value == device['FWD'] else 'REVERSE'}")
        elif choice == "3":
            stop.value = not stop.value
            print(f"[STOP] ESC {'ENABLED' if stop.value else 'DISABLED'}")
        elif choice == "4":
            if brake.value:
                brake.value = False
                print("[BRAKE] RELEASED before ramp")
            pwm.duty_cycle = 0
            stop.value = True
            print("[RAMP] Starting PWM ramp...")
            for duty in range(0, 101, 10):
                pwm.duty_cycle = int(duty * 655.35)
                print(f" PWM {duty}%")
                time.sleep(0.25)
            for duty in range(100, -1, -10):
                pwm.duty_cycle = int(duty * 655.35)
                print(f" PWM {duty}%")
                time.sleep(0.25)
            pwm.duty_cycle = 0
            brake.value = True
            stop.value = False
            print("[RAMP] Done. Wheel stopped and brake engaged.")
        elif choice == "5":
            sniff_pulse_pin_active(device)
        elif choice == "6":
            print("🔙 Returning to main menu.")
            break
        else:
            print("❌ Invalid selection. Try again.")

# === Entry Point ===
if __name__ == "__main__":
    while True:
        print("\nMain Menu — Select device to test:")
        print(" [1] Left Wheel")
        print(" [2] Right Wheel")
        print(" [3] Both Wheels")
        print(" [4] Exit program")
        choice = input("> ").strip()

        if choice == "1":
            pwm, dir_pin, stop, brake, pulse = setup_device(LEFT)
            print_device_status(LEFT, dir_pin, stop, brake, pulse)
            wheel_test_menu(LEFT, pwm, dir_pin, stop, brake, pulse)
        elif choice == "2":
            pwm, dir_pin, stop, brake, pulse = setup_device(RIGHT)
            print_device_status(RIGHT, dir_pin, stop, brake, pulse)
            wheel_test_menu(RIGHT, pwm, dir_pin, stop, brake, pulse)
        elif choice == "3":
            print("🚧 Both Wheel testing not implemented yet.")
        elif choice == "4" or choice.lower() == "q":
            print("👋 Exiting test harness.")
            break
        else:
            print("❌ Invalid selection. Try again.")
