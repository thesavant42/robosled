# robot-main.py
# Author: savant42

import time
from ibus_receiver import get_latest_packet

print("🤖 Robot Main Starting Up...")

while True:
    ch_data = get_latest_packet()
    time.sleep(0.1)
