# Modular CircuitPython Robot Control System

This repository contains a modular, configurable robot control system built using CircuitPython for the FeatherS3 (ESP32-S3 from Ultimate Maker). The project integrates multiple subsystems including RC input via S‑Bus/PPM, motor control for two ZS‑X11H controllers, manual override inputs, speed pulse feedback for future closed-loop control, and an IS31FL3741-driven 13×9 RGB LED array for status/debug display.

## Overview

The system is designed to be:
- **Modular:** Each functional block is implemented in its own file (keeping each file under 100 lines), making the code clean, modular, and easy to maintain.
- **Configurable:** All critical settings (pin mappings, PWM frequencies, debug settings, etc.) are stored in a single, human-editable file: `robot_config.txt`.
- **Debuggable:** A built-in logger provides adjustable debug output via serial logs (with support for optional WiFi logging in the future) and visual feedback (via an RGB LED array).
- **Future-Proof:** With sensor inputs—such as speed pulses for each motor—already integrated into the design, the project is ready for future closed-loop (PID) control.

## Hardware

- **MCU:** FeatherS3 (ESP32-S3 from Ultimate Maker)
- **RC Input:** FLYSKY FS-i6X using S‑Bus/PPM (all channels consolidated into a single data pin)
- **Motor Controllers:** Two ZS‑X11H motor controllers with PWM, Direction, and Brake control
- **Manual Overrides:** Left STOP, Right STOP, and Global BRAKE buttons (digital inputs)
- **Feedback & Display:** 13×9 RGB LED array driven by IS31FL3741 (via Stemma QT I2C)
- **Speed Pulse Inputs:** One speed pulse input per motor for future closed-loop control

## Project Structure

- **robot_config.txt**  
  Contains all configuration parameters (pin mappings, PWM frequency, debug settings, etc.).

- **config_loader.py**  
  Loads the configuration file and provides a dictionary of key–value pairs for use by all modules.

- **rc_receiver.py**  
  Initializes the UART to receive and decode the S‑Bus/PPM signal from the RC receiver.

- **motor_control.py**  
  Controls the two ZS‑X11H motor controllers using PWM outputs, along with digital outputs for motor direction and braking.

- **manual_overrides.py**  
  Reads manual override switches (Left STOP, Right STOP, and Global BRAKE) from digital input pins.

- **speed_pulse_reader.py**  
  Reads speed pulse signals (one per motor) using `pulseio.PulseIn`, for use in future closed-loop (PID) control.

- **logger.py**  
  Provides centralized logging with adjustable log levels (ERROR, WARN, INFO, DEBUG).

- **main.py**  
  The main orchestrator that ties together configuration, RC input, manual overrides, motor control, speed pulse feedback, and logging.
 https://github.com/yourusername/your-repo.git
   cd your-repo
