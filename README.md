# Robosled Project Summary

## 🚀 Project Goals
- Robosled is the project to give my animatronic Master Yoda from Home Depot some mobility, by way of a scratch-built autonomous vehicle. 
- The Roboseld features wheels repurposed from wrecked "hover boards", known elsewhere as self-stabilizing electric-unicycles (gee, wonder why they changed the name?) 
- The goal of the Robosled code is to create a modular, reliable, and testable forward-driven 3-wheeled robot (2WD + rear caster)
  -- controlled via an FS-i6X transmitter (OpenI6X firmware) and
  -- FlySky iA6B receiver
    - Connected via UART
  - Using the I-BUS16 protocol
    - For 14-usable channels over 1-wire
    - Sends telemetry from robot over UART back to the RC transciever
  
- The robot uses two ZS-X11H BLDC motor controllers
- Features real-time feedback and control via:
  -- OLED display, NeoKey, and Qwiic Twist inputs.

### Key Objectives:
- 🧠 Smart throttle and pivot logic with safe reverse enforcement
- 🛑 Braking via hardware BRAKE pins and override logic
- 📟 Visual feedback using SH1107 OLED and Qwiic Twist LED ring
- ⚙️ RPM monitoring via speed pulse pins
- 🔋 Modular I2C handling to eliminate initialization errors
- 🎮 Full integration with FS-i6X transmitter channel mappings

---

## 📊 Project Progress
- ✅ Working throttle, pivot, and braking control
- ✅ OLED display initialized with rotation fix (90 degrees)
- ✅ RPM measured from speed pulse (1 wheel verified)
- ✅ Brake logic (3-way: FORCED_ON, FORCED_OFF, SWITCH)
- ✅ Channel mapping and scale validation for CH1–CH14
- ✅ IBUS packet validation + safe boot sequence for UART/I2C
- 🔄 Qwiic Twist and NeoKey currently disabled but staged for reintegration
- 🔧 Display mirroring and low-speed PWM logic under development

---

## ✅ TODO Summary (Top-Level)
- [ ] Reinstate Qwiic Twist and NeoKey input modules
- [ ] Fully test both left/right RPM speed pulse pins
- [ ] Add PID or pulse-based workaround for stall-prone low speeds
- [ ] Abstract I2C boot sequencing into a shared loader module
- [ ] Finalize safe reverse lockout logic
- [ ] Complete OLED mirroring to console output
- [ ] Module limit goal: ~100 lines per file for clarity

---

## 🔧 Hardware Reference

### 🧠 Controller & Firmware
| Component | Details |
|-----------|---------|
| Transmitter | FlySky FS-i6X (OpenI6X v2.1.0 2025-03-09, eeprom 222) |
| Receiver    | FlySky iA6B |
| Protocol    | I-BUS (115200 baud, 8N2) |

### 📡 IBUS Channel Mapping (CH1–CH14)
| Channel | Input         | Use                          | Range (Expected)      |
|---------|---------------|-------------------------------|------------------------|
| CH1     | Right Stick X | Veering (Unused)             | -1500 to +1500        |
| CH2     | Right Stick Y | Direction (FWD/REV intent)   | -1500 to +1500        |
| CH3     | Left Stick Y  | Throttle scaling             | 988–2000 (approx.)     |
| CH4     | Left Stick X  | Pivot (L/R)                  | -1500 to +1500        |
| CH5     | SWA 2POS      | Brake activation switch      | <1500 = OFF, >1500 = ON|
| CH6     | SWB 2POS      | Brake override mode          | -1500 to +1500        |
| CH7     | SWC 3POS      | Enables CH8 on HIGH          | 0/50140/50652          |
| CH8     | SWD 2POS      | Custom control (e.g., LEDs)  | -100 to +100          |
| CH9     | VARA Knob     | Unused                       | -1500 to +1500        |
| CH10    | VARB Knob     | Unused                       | -100 to +100          |
| CH11–14 | -             | Unused                       | Varies                 |

### 🛞 Left Wheel Pin Map

| Signal | `board.Dxx` | Actual `IOxx` | Notes                   |
|--------|-------------|---------------|-------------------------|
| PWM    | `board.D13` | `IO11`        | Confirmed functional    |
| DIR    | `board.D9`  | `IO1`         | Forward = HIGH          |
| STOP   | `board.D10` | `IO3`         | ESC Enable, HIGH = on   |
| BRAKE  | `board.D6`  | `IO38`        | Brake Active = HIGH     |
| PULSE  | `board.D12` | `IO10`        | ✅ Confirmed pulse input |

### 🛞 Right Wheel Pin Map

| Signal | `board.Dxx` | Actual `IOxx` | Notes                   |
|--------|-------------|---------------|-------------------------|
| PWM    | `board.D19` | `IO5`         | Confirmed functional    |
| DIR    | `board.D16` | `IO14`        | Forward = LOW           |
| STOP   | `board.D17` | `IO12`        | ESC Enable, HIGH = on   |
| BRAKE  | `board.D15` | `IO18`        | Brake Active = HIGH     |
| PULSE  | `board.D14` | `IO6`         | ✅ Confirmed pulse input |
| UARTTX | `board.D1`  | `IO43`        | main UART TX            |
| UARTRX | `board.D0`  | `IO44`        | main UART TX            |

### 📠 I2C Addresses
| Device         | Address | Notes |
|----------------|---------|-------|
| SH1107 OLED    | `0x3D`  | Uses `displayio` + rotation 90°   |
| GPS (DFRobot)  | `0x20`  | Proprietary register format        |
| NeoKey 1x4     | `0x30`  | On hold for brake/confirm buttons  |
| Qwiic Twist    | `0x3F`  | Encoder + NeoPixel visual          |
| TCA9548A (Mux) | `0x70`  | Optional expansion                 |


---

## 🧱 Suggested I2C Module Map
| Module File            | Device        | Role |
|------------------------|---------------|------|
| `oled_display.py`      | SH1107 OLED   | Page rotation, text write |
| `gnss_module.py`       | DFRobot GPS   | Structured location export |
| `neokey_controller.py` | NeoKey 1x4    | Input & LED feedback |
| `twist_controller.py`  | Qwiic Twist   | Rotary + LED feedback |
| `i2c_device_loader.py` | All           | Init, retry, bus stabilization |


---

## ⚠️ Known Issues / Observations
- OLED driver must be initialized **first** or SCL errors will crash bus
- RPM currently working for 1 motor; both speed pins need assignment
- Low duty PWM = motor stall; workaround planned with PWM pulsing
- SWC (CH7) controls whether CH8 sends values at all
- Brake logic must support desync between switch and internal state
- Channel scaling requires normalization + clamping for safety
- UART and I2C should not init in parallel to avoid collision at boot

---

## 🪛 Recommended Boot Sequence
1. Initialize UART for IBUS
2. Initialize I2C with bus lock retries
3. Load OLED **first** and test screen
4. Scan bus and load other modules: GPS, NeoKey, Twist
5. Begin control loop

---

## 📌 Next Steps Checklist (Condensed)
- [ ] Modularize Qwiic + NeoKey input again
- [ ] Validate speed pulse inputs for both motors
- [ ] Add PWM pulsing workaround for stall-prone low speeds
- [ ] Integrate display mirroring for OLED + console
- [ ] Implement `i2c_device_loader.py`
- [ ] PID logic evaluation for future expansion
