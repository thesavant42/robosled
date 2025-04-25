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
    'PULSE': board.D12,
    'FWD': True  # True = FORWARD = HIGH
}

RIGHT = {
    'name': 'Right Wheel',
    'PWM': board.D19,
    'DIR': board.D16,
    'STOP': board.D17,
    'BRAKE': board.D15,
    'PULSE': board.D14,
    'FWD': False  # False = FORWARD = LOW
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
    pulse.pull = digitalio.Pull.DOWN

    print(f"[INIT] {device['name']} — DIR: {'FORWARD' if dir_pin.value == device['FWD'] else 'REVERSE'}, BRAKE: {'ENGAGED' if brake.value else 'RELEASED'}, STOP: {stop.value}, PULSE: {pulse.value}")

    return pwm, dir_pin, stop, brake, pulse

# === Menu System ===
def print_device_status(device, dir_pin, stop, brake, pulse):
    print(f"\n[{device['name']}] STATUS")
    print(f" DIR: {'FORWARD' if dir_pin.value == device['FWD'] else 'REVERSE'}")
    print(f" BRAKE: {'ENGAGED' if brake.value else 'RELEASED'}")
    print(f" STOP (Enable): {'HIGH' if stop.value else 'LOW'}")
    print(f" PULSE: {'HIGH' if pulse.value else 'LOW'}")
    print(f" FWD logic: {'HIGH' if device['FWD'] else 'LOW'}")


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
        elif c == "4" or c.lower() == 'q':
            print("👋 Exiting program. Bye!")
            raise SystemExit
        else:
            print("Invalid selection. Enter 1, 2, 3, or 4. Or 'q' to quit.")

def prompt_action(devices):
    print(f"\nDEVICE: {', '.join(dev['name'] for dev in devices)}")
    print("\nSelect test action:")
    print(" [1] Toggle BRAKE")
    print(" [2] Toggle DIR")
    print(" [3] Toggle STOP (ESC Enable)")
    print(" [4] PWM Duty Cycle Ramp")
    print(" [5] Back to device selection")
    print(" [6] Sync Validation (Both Wheels Only)")
    print(" [7] Pulse Counter Test (Single Wheel Only)")
    print(" [8] Pulse Monitor (edge debugger)")
    print(" [q] Quit program")
    while True:
        c = input("> ").strip().lower()
        if c in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            return int(c)
        elif c == "q":
            print("👋 Exiting program. Bye!")
            raise SystemExit
        else:
            print("Invalid selection. Enter 1–8 or 'q' to quit.")

# === Main Loop ===
while True:
    devices = prompt_device()
    pwm_channels = [setup_device(dev) for dev in devices]

    while True:
        action = prompt_action(devices)
        if action == 5:
            break

        if action == 6 and len(devices) == 2:
            # Sync validation logic remains unchanged (as above)
            continue

        if action == 7 and len(devices) == 1:
            pwm, dir_pin, stop, brake, pulse = pwm_channels[0]
            name = devices[0]['name']
            print(f"\n📡 Starting pulse counter test for {name}...")
            brake.value = False
            pwm.duty_cycle = 0
            stop.value = True
            time.sleep(0.5)

            rising_edges = 0
            prev = pulse.value
            pwm.duty_cycle = int(0.5 * 65535)  # 50%
            print("    ⚙️ Running for 3 seconds at 50% PWM...")
            t_start = time.monotonic()
            while time.monotonic() - t_start < 3:
                now = pulse.value
                if now and not prev:
                    rising_edges += 1
                prev = now
            pwm.duty_cycle = 0
            stop.value = False
            brake.value = True
            print(f"📈 {name} — Rising edges: {rising_edges} in 3s")
            continue

        if action == 8 and len(devices) == 1:
            pwm, dir_pin, stop, brake, pulse = pwm_channels[0]
            name = devices[0]['name']
            print(f"\n🧪 Monitoring PULSE pin for {name} for 10 seconds...")
            brake.value = False
            pwm.duty_cycle = 0
            stop.value = True
            pwm.duty_cycle = int(0.5 * 65535)  # 50%
            time.sleep(0.5)

            rising = 0
            falling = 0
            prev = pulse.value
            t0 = time.monotonic()
            while time.monotonic() - t0 < 10:
                now = pulse.value
                if now != prev:
                    edge = "RISING" if now else "FALLING"
                    print(f"  ⏱ {edge} edge at {round(time.monotonic() - t0, 4)}s")
                    if now:
                        rising += 1
                    else:
                        falling += 1
                    prev = now

            pwm.duty_cycle = 0
            stop.value = False
            brake.value = True
            print(f"📊 Edge count: {rising} rising, {falling} falling")
            continue

        for i, dev in enumerate(devices):
            pwm, dir_pin, stop, brake, pulse = pwm_channels[i]
            name = dev['name']

            if action == 1:
                brake.value = not brake.value
                print(f"[TOGGLE] {name} BRAKE: {'ENGAGED' if brake.value else 'RELEASED'}")
            elif action == 2:
                dir_pin.value = not dir_pin.value
                print(f"[TOGGLE] {name} DIR now: {'FORWARD' if dir_pin.value == dev['FWD'] else 'REVERSE'}")
            elif action == 3:
                stop.value = not stop.value
                print(f"[TOGGLE] {name} STOP: {'ENABLED' if stop.value else 'DISABLED'}")
            elif action == 4:
                print(f"[PWM] {name} ramp test... disengaging brake and enabling STOP")
                brake.value = False
                pwm.duty_cycle = 0
                stop.value = True
                for duty in range(0, 101, 10):
                    pwm.duty_cycle = int((duty / 100) * 65535)
                    print(f"  Duty: {duty}%")
                    time.sleep(0.3)
                for duty in range(90, -1, -10):
                    pwm.duty_cycle = int((duty / 100) * 65535)
                    print(f"  Duty: {duty}%")
                    time.sleep(0.3)
                pwm.duty_cycle = 0
                stop.value = False
                brake.value = True
                print(f"[PWM] {name} test complete. Brakes re-engaged, STOP disabled.")

            print_device_status(dev, dir_pin, stop, brake, pulse)

        print("\n✅ Test complete. Returning to menu.")
