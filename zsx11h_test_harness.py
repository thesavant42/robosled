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

# === Pin Map with Forward Logic and Speed Pulse ===
LEFT = {
    'name': 'Left Wheel',
    'PWM': board.D13,
    'DIR': board.D9,
    'STOP': board.D10,
    'BRAKE': board.D6,
    'PULSE': board.D39,
    'FWD': True  # True = FORWARD (logic HIGH)
}

RIGHT = {
    'name': 'Right Wheel',
    'PWM': board.D19,
    'DIR': board.D16,
    'STOP': board.D17,
    'BRAKE': board.D15,
    'PULSE': board.D12,
    'FWD': False  # False = FORWARD (logic LOW)
}

# === Setup IO ===
def setup_device(device):
    print(f"\nDEVICE: {device['name']}")
    for key in ['PWM', 'DIR', 'STOP', 'BRAKE', 'PULSE']:
        print(f" {key}: {device[key]}")
    print(f" FWD = {'HIGH' if device['FWD'] else 'LOW'}")

    pwm = pwmio.PWMOut(device['PWM'], frequency=2000, duty_cycle=0)
    dir_pin = digitalio.DigitalInOut(device['DIR'])
    dir_pin.direction = digitalio.Direction.OUTPUT
    dir_pin.value = not device['FWD']  # Set direction so that default is FORWARD

    stop = digitalio.DigitalInOut(device['STOP'])
    stop.direction = digitalio.Direction.OUTPUT
    stop.value = False

    brake = digitalio.DigitalInOut(device['BRAKE'])
    brake.direction = digitalio.Direction.OUTPUT
    brake.value = False

    pulse = digitalio.DigitalInOut(device['PULSE'])
    pulse.direction = digitalio.Direction.INPUT

    print(f"[INIT] {device['name']} — DIR: {'FORWARD' if dir_pin.value == device['FWD'] else 'REVERSE'}, BRAKE: {'ENGAGED' if brake.value else 'RELEASED'}, STOP: {stop.value}, PULSE: {pulse.value}")

    # Optional: Print RPM from pulse interval
    print("⏱️ Measuring pulse interval for RPM...")
    last_val = pulse.value
    print("⏳ Waiting for first rising edge...")
    while not pulse.value:
        pass
    while pulse.value:
        pass
    t1 = time.monotonic_ns()
    while not pulse.value:
        pass
    while pulse.value:
        pass
    t2 = time.monotonic_ns()
    interval_ns = t2 - t1
    if interval_ns > 0:
        freq_hz = 1_000_000_000 / interval_ns
        rpm = freq_hz * 60
        print(f"⚙️ {device['name']} RPM: {rpm:.2f}")
    else:
        print(f"⚠️ {device['name']} pulse interval too short to measure")

    return pwm, dir_pin, stop, brake, pulse

# === Menu System ===
def prompt_device():
    print("\nMain Menu — Select device to test:")
    print(" [1] Left Wheel")
    print(" [2] Right Wheel")
    print(" [3] Both Wheels")
    print(" [4] Exit program")
    while True:
        c = input("> ").strip()
        if c == "1":
            return [LEFT]
        elif c == "2":
            return [RIGHT]
        elif c == "3":
            return [LEFT, RIGHT]
        elif c == "4":
            print("👋 Exiting program. Bye!")
            raise SystemExit
        else:
            print("Invalid selection. Enter 1, 2, 3, or 4.")

def prompt_action(devices):
    print(f"\nDEVICE: {', '.join(dev['name'] for dev in devices)}")
    for dev in devices:
        for key in ['PWM', 'DIR', 'STOP', 'BRAKE', 'PULSE']:
            print(f" {dev['name']} {key}: {dev[key]}")
        print(f" {dev['name']} FWD = {'HIGH' if dev['FWD'] else 'LOW'}")
    print("\nSelect test action:")
    print(" [1] Toggle BRAKE")
    print(" [2] Toggle DIR")
    print(" [3] Toggle STOP (ESC Enable)")
    print(" [4] PWM Duty Cycle Ramp")
    print(" [5] Back to device selection")
    while True:
        c = input("> ").strip()
        if c in ["1", "2", "3", "4", "5"]:
            return int(c)
        else:
            print("Invalid selection. Enter a number from 1 to 5.")

# === Main Loop ===
while True:
    devices = prompt_device()
    pwm_channels = []
    for dev in devices:
        pwm_channels.append(setup_device(dev))

    while True:
        action = prompt_action(devices)
        if action == 5:
            break

        for i, dev in enumerate(devices):
            pwm, dir_pin, stop, brake, pulse = pwm_channels[i]
            name = dev['name']

            if action == 1:
                brake.value = not brake.value
                print(f"[{i}] {name} brake toggled: {'ENGAGED' if brake.value else 'RELEASED'}")

            elif action == 2:
                dir_pin.value = not dir_pin.value
                current_dir = 'FORWARD' if dir_pin.value == dev['FWD'] else 'REVERSE'
                print(f"[{i}] {name} direction set to: {current_dir}")

            elif action == 3:
                stop.value = not stop.value
                print(f"[{i}] {name} STOP toggled: {'ENABLED' if stop.value else 'DISABLED'}")

            elif action == 4:
                print(f"[{i}] Starting PWM ramp for {name}...")
                brake.value = False
                pwm.duty_cycle = 0
                stop.value = True
                time.sleep(0.5)

                for dc in range(0, 101, 10):
                    pwm.duty_cycle = int(dc / 100 * 65535)
                    print(f"    {name} PWM: {dc}%")
                    time.sleep(0.3)

                for dc in range(100, -1, -10):
                    pwm.duty_cycle = int(dc / 100 * 65535)
                    print(f"    {name} PWM: {dc}%")
                    time.sleep(0.3)

                pwm.duty_cycle = 0
                brake.value = True
                stop.value = False
                print(f"[{i}] PWM ramp complete. Brake re-engaged, ESC disabled.")

        print("
✅ Test complete. Returning to menu.")
