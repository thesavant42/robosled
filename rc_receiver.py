# rc_receiver.py
"""
S-Bus/PPM Receiver Module for Robot Control System

This module initializes a UART interface to receive the S-Bus signal from your
FLYSKY FS-i6X RC receiver (via a single data pin), and decodes the 25-byte
S-Bus frame to extract 16 channel values. The channels are 11-bit values.

S-Bus specifics:
  - Baud rate: 100000
  - 8 data bits, even parity, 2 stop bits
  - Frame length: 25 bytes (start byte 0x0F, 22 data bytes, flags, end byte 0x00)

Ensure that your hardware supports the inverted logic required by the S-Bus
protocol (or use a hardware inverter if needed).

Debug:
  - When DEBUG is set to True in the config file, this module prints raw frame
    data and decoding details for testing the transceiver connection and protocol settings.
"""

import board
import busio
import time
from config_loader import load_config

# Load configuration parameters from robot_config.txt
config = load_config("robot_config.txt")
RC_SBUS_PIN_NAME = config.get("RC_SBUS_PIN", "D23")
DEBUG = config.get("DEBUG", "False").lower() in ("true", "1", "yes")
rc_sbus_pin = getattr(board, RC_SBUS_PIN_NAME)

# Initialize UART for S-Bus communication.
# Note: S-Bus requires inverted logic. Ensure that your hardware or wiring accounts for this.
uart = busio.UART(
    rx=rc_sbus_pin,
    tx=None,
    baudrate=100000,
    parity=busio.UART.EVEN,
    stop=2,
)

class SBusReceiver:
    def __init__(self, uart, timeout=0.1):
        """
        Initialize the SBusReceiver.
        
        :param uart: The UART instance to read S-Bus data from.
        :param timeout: Timeout (in seconds) to wait for a complete frame.
        """
        self.uart = uart
        self.timeout = timeout
        self.frame_length = 25  # S-Bus frame length in bytes

    def read_frame(self):
        """
        Read raw bytes from the UART until a valid frame is detected or timeout.

        :return: A bytearray representing a complete frame, or None if timeout occurs.
        """
        start_time = time.monotonic()
        buffer = bytearray()
        while (time.monotonic() - start_time) < self.timeout:
            data = self.uart.read(self.frame_length - len(buffer))
            if data:
                if DEBUG:
                    print("Read raw data:", data)
                buffer.extend(data)
                if len(buffer) >= self.frame_length:
                    start_index = buffer.find(b'\x0F')
                    if start_index != -1 and len(buffer) - start_index >= self.frame_length:
                        frame = buffer[start_index:start_index + self.frame_length]
                        if frame[-1] == 0x00:
                            # If debug, print the raw frame details
                            if DEBUG:
                                print("Valid frame detected:", frame)
                            buffer = buffer[start_index + self.frame_length:]
                            return frame
                        else:
                            buffer.pop(0)
        if DEBUG:
            print("Frame read timed out after {:.2f} seconds".format(time.monotonic() - start_time))
        return None

    def decode_frame(self, frame):
        """
        Decode a 25-byte S-Bus frame into a list of 16 channel values.
        
        :param frame: A complete S-Bus frame (bytearray)
        :return: A list of 16 integers (each an 11-bit value) or None if frame invalid.
        """
        if frame is None or len(frame) != self.frame_length:
            if DEBUG:
                print("Invalid frame length or None frame received.")
            return None
        if frame[0] != 0x0F or frame[-1] != 0x00:
            if DEBUG:
                print("Frame start/end bytes not matching: start=0x{:02X}, end=0x{:02X}".format(frame[0], frame[-1]))
            return None
        data = frame[1:23]
        raw = 0
        for i, byte in enumerate(data):
            raw |= byte << (8 * i)
        channels = []
        for ch in range(16):
            value = (raw >> (11 * ch)) & 0x7FF
            channels.append(value)
        if DEBUG:
            print("Decoded channel values:", channels)
        return channels

    def get_channels(self):
        """
        Attempt to read a frame and decode it into channel values.

        :return: List of channel values, or None if no valid frame is available.
        """
        frame = self.read_frame()
        if frame:
            return self.decode_frame(frame)
        return None

# For testing purposes, run this module to display decoded channel values.
if __name__ == "__main__":
    receiver = SBusReceiver(uart)
    print("S-Bus Receiver Initialized. Waiting for data...")
    while True:
        channels = receiver.get_channels()
        if channels:
            print("Decoded Channels:", channels)
        time.sleep(0.1)
