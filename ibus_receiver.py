# ibus_receiver.py
# Author: savant42

import struct
import board
import busio

# Set to True to print raw channel data for debugging
debug = False

# UART config for IBUS (FlySky protocol)
# 115200 baud, 8 data bits, no parity, 2 stop bits
uart = busio.UART(board.IO44, board.IO43, baudrate=115200, stop=2, timeout=0.01)

packet_size = 32
buffer = bytearray(packet_size * 2)

# Channel state cache
last_ch_values = [0] * 16

# Track previous brake state to prevent spamming
brake_prev_state = None

def checksum_is_valid(data):
    received = struct.unpack_from("<H", data, 30)[0]
    computed = 0xFFFF - sum(data[0:30])
    return received == (computed & 0xFFFF)

def decode_channels(data):
    channels = []
    for i in range(14):
        ch_val = struct.unpack_from("<H", data, 2 + i * 2)[0]
        channels.append(ch_val)
    return channels

def get_latest_packet():
    global last_ch_values, brake_prev_state
    uart.readinto(buffer)
    new_packet_found = False
    for offset in range(len(buffer) - packet_size):
        if buffer[offset] == 0x20 and buffer[offset + 1] == 0x40:
            packet = buffer[offset:offset + packet_size]
            if len(packet) == packet_size and checksum_is_valid(packet):
                ch = decode_channels(packet)
                last_ch_values = ch  # update cached state
                new_packet_found = True
                break

    # Print mapped intent outputs in normal mode
    if not debug:
        # BRAKES = CH5
        brakes_val = last_ch_values[4]
        brake_now = brakes_val > 1500

        if brake_now != brake_prev_state:
            print("BRAKES: ON" if brake_now else "BRAKES: OFF")
            brake_prev_state = brake_now
    else:
        for i, val in enumerate(last_ch_values):
            print(f"CH{i + 1}: {val}", end='  ')
        print("\n")

    return last_ch_values
