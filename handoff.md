# Robosled Project Handoff Package

This package contains a consolidated summary of the Robosled robot development effort as of April 2025. It is suitable for sharing, pausing development, or onboarding new contributors.

---

## ✅ Project Goals

- Build a **2WD differential-drive robot** using ZS-X11H BLDC motor controllers
- Controlled via **Flysky FS-i6X RC transmitter** using **IBUS** protocol
- Implement modular control logic in CircuitPython 9
- Provide debug visualization via **OLED display** and **console mirror output**
- Support advanced features like:
  - Brake state machine
  - Speed pulse RPM reading per wheel
  - PID-ready architecture for future tuning
  - Input via NeoKey and Qwiic Twist

---

## 📈 Progress Summary

- ✅ Fully working motor control (PWM + DIR + BRAKE + ENABLE)
- ✅ Confirmed working IBUS receiver (FS-iA6B → UART RX)
- ✅ NeoKey and Qwiic Twist integrated for test harness
- ✅ I2C OLED working with displayio (rotation 90°)
- ✅ GNSS module decoded via I2C using DFRobot protocol
- ✅ `main_robot.py` shows live feedback on throttle, pivot, brake, RPM
- ✅ GitHub repo live at: https://github.com/thesavant42/robosled
- ⚠️ Still dealing with SCL bug (shared I2C bus timing/initialization)

---

## 📋 TODO Summary

| ID | Task | Status |
|----|------|--------|
| 1️⃣ | Map CH2 (IBUS) to direction intent (+1500 = FWD, -1500 = REV) | Pending |
| 2️⃣ | Pulse the gas strategy for low-speed motor startup | Pending |
| 3️⃣ | Validate dual-speed pulse inputs per wheel | Partial (1 working) |
| 4️⃣ | Implement i2c_loader module for consistent init order | Planned |
| 5️⃣ | Improve OLED layout, pagination for channel debug | WIP |
| 6️⃣ | Add GPS telemetry over IBUS16 sensor packets | Planned |
| 7️⃣ | Test PID control loop with LIS3DH or speed pulse | Future |
| 8️⃣ | Enable CH3 scaling logic for throttle multiplier | Done |
| 9️⃣ | Confirm all I2C devices behave with shared SCL/SDA | Partial |
| 🔟 | Confirm RPM math matches real-world movement | TBD |

---

## 🧰 Hardware Reference (Short Summary)

**MCU:** Unexpected Maker FeatherS3 (ESP32-S3)
**Motors:** ZS-X11H controllers (left & right)
**Radio:** FlySky FS-i6X (OpenI6X v2.1.0)
**Receiver:** FS-iA6B (IBUS RX/TX)
**Display:** SH1107 128x128 OLED, rotation = 90
**Input:** NeoKey 1x4, Qwiic Twist rotary encoder
**GNSS:** DFRobot GNSS via I2C, proprietary binary protocol

See full `hardware_reference.md` for GPIO map, I2C addresses, etc.

---

## 📦 Suggested I2C Loader Module Structure

```
├── i2c_loader.py
│   ├── Initializes I2C bus
│   ├── Probes and verifies connected devices
│   └── Initializes drivers in safe order
│
├── devices/
│   ├── oled_display.py
│   ├── neokey_pad.py
│   ├── qwiic_twist.py
│   └── gnss_dfrobot.py
```

- Each device module is self-contained
- All use the shared `busio.I2C()` instance from `i2c_loader`
- Prevents timing race on OLED + GNSS + NeoKey

---

## 🔍 Additional Notes & Gotchas

- ❗**SH1107 OLED + GNSS + NeoKey** timing bug: one device often fails during cold boot if init is not sequenced carefully.
- **FlySky FS-i6X** switch mapping quirks required editing input curves
- **CH3** now works as a **throttle multiplier**, useful for "pulsing" motion
- OLED display shows: throttle, pivot, brake state, and RPM — mirrored to console
- Speed pulse math is based on rising edge frequency and conversion to RPM

---

## 🧭 Final Guidance

To onboard or continue development:
1. Start with `main_robot.py` for motor behavior
2. Check `hardware_reference.md` for pin assignments and protocols
3. Use `README.md` as the source of truth for goals and architecture
4. Confirm I2C boot order is respected via `i2c_loader`
5. Use the console mirror output to debug behavior headlessly

---

**Maintainer:** `savant42`  
**Project:** [https://github.com/thesavant42/robosled](https://github.com/thesavant42/robosled)

