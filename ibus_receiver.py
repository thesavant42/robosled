# ibus_receiver_debug.py
# Reads FlySky IBUS packets from UART and prints CH1–CH4 with CRC verification

import time
import board
import busio

# === CONFIGURATION ===
IBUS_UART = busio.UART(
    tx=board.IO43,
    rx=board.IO44,  # Change this to your RX pin if different
    baudrate=115200,
    bits=8,
    parity=None,
    stop=2,
    timeout=0.01,
    receiver_buffer_size=512
)

IBUS_CHANNEL_COUNT = 14
IBUS_PACKET_SIZE = 32
IBUS_HEADER = b"\x20\x40"
FAILSAFE_CH4_VALUE = 50661

print("🎮 CH1–CH4 monitor with CRC debug active...")

last_values = [None] * 4  # For CH1 to CH4
buffer = bytearray()

def validate_crc(packet):
    raw_sum = sum(packet[0:30])
    calc_crc = 0xFFFF - raw_sum
    packet_crc = packet[30] | (packet[31] << 8)

    if calc_crc != packet_crc:
        print("❌ CRC mismatch:")
        print(f"   → Raw sum   : {raw_sum} (0x{raw_sum:04X})")
        print(f"   → Computed  : 0x{calc_crc:04X}")
        print(f"   → Received  : 0x{packet_crc:04X}")
        print(f"   → Packet    : {[hex(b) for b in packet]}")
        return False
    return True

while True:
    data = IBUS_UART.read(64)
    if data:
        buffer.extend(data)
        if len(buffer) > 256:
            buffer = buffer[-256:]  # prevent runaway growth

        for i in range(len(buffer) - IBUS_PACKET_SIZE + 1):
            if buffer[i:i+2] == IBUS_HEADER:
                packet = buffer[i:i + IBUS_PACKET_SIZE]
                if len(packet) == IBUS_PACKET_SIZE and validate_crc(packet):
                    updates = []
                    for ch in range(4):
                        lo = packet[2 + ch * 2]
                        hi = packet[3 + ch * 2]
                        val = (hi << 8) | lo

                        if val != last_values[ch]:
                            updates.append((ch + 1, val))
                            last_values[ch] = val

                    for ch_num, val in updates:
                        if ch_num == 4 and val == FAILSAFE_CH4_VALUE:
                            print("🚨 CH4 appears to be in failsafe state!")
                        print(f"✅ CH{ch_num}: {val}")

                    buffer = buffer[i + IBUS_PACKET_SIZE:]
                    break

    time.sleep(0.01)
