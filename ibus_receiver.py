# ibus_receiver_debug.py
# Reads FlySky IBUS packets from UART and prints CH1–CH4 with CRC verification and raw scaling
# hardcoded uart pins, not ready for modular
# bugs: only shows 1-4 instead of 1-14

import time
import board
import busio

# === CONFIGURATION ===
IBUS_UART = busio.UART(
    tx=board.IO43,    # Change this to your RX pin if different
    rx=board.IO44,    # Change this to your RX pin if different
    baudrate=115200,
    bits=8,            # 8N2
    parity=None,       # 8N2 
    stop=2,            # 8N2
    timeout=0.01,
    receiver_buffer_size=512
)

IBUS_CHANNEL_COUNT = 14
IBUS_PACKET_SIZE = 32
IBUS_HEADER = b"\x20\x40"
FAILSAFE_CH4_VALUE = 50661
print("🎮 CH1–CH14 monitor with CRC debug and raw 16-bit scaling...")

last_values = [None] * 4  # For CH1 to CH4
buffer = bytearray()

# Track min/max for each channel
channel_ranges = [
    [None, None],           # CH1
    [None, None],           # CH2
    [None, None],           # CH3
    [0, 65535]              # CH4 (fixed 16-bit range)
]

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

def map_range(val, min_val, max_val, is_throttle=False):
    if min_val is None or max_val is None or min_val == max_val:
        return 0
    if is_throttle:
        return round((val / 65535) * 100)
    else:
        return round(((val - min_val) / (max_val - min_val)) * 200 - 100)

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
                    for ch in range(4):
                        lo = packet[2 + ch * 2]
                        hi = packet[3 + ch * 2]
                        val = (hi << 8) | lo

                        # Update range only for CH1–CH3
                        if ch < 3:
                            ch_min, ch_max = channel_ranges[ch]
                            if ch_min is None or val < ch_min:
                                channel_ranges[ch][0] = val
                            if ch_max is None or val > ch_max:
                                channel_ranges[ch][1] = val

                        if val != last_values[ch]:
                            last_values[ch] = val

                            if ch == 3 and val == FAILSAFE_CH4_VALUE:
                                print("🚨 CH4 appears to be in failsafe state!")

                            # Always scale CH4 as a percentage of 65535
                            if ch == 3:
                                scaled = round((val / 65535) * 100)
                                min_disp = 0
                                max_disp = 65535
                            else:
                                scaled = map_range(val, channel_ranges[ch][0], channel_ranges[ch][1])
                                min_disp = channel_ranges[ch][0]
                                max_disp = channel_ranges[ch][1]

                            units = "%" if ch == 3 else "±%"
                            label = "Throttle" if ch == 3 else f"CH{ch+1}"
                            print(f"✅ {label}: {val} → {scaled}{units}  [Min: {min_disp}, Max: {max_disp}]")

                    buffer = buffer[i + IBUS_PACKET_SIZE:]
                    break

    time.sleep(0.01)
