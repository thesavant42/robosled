# oled_display.py
# note: Directly initializes i2c, do not use as is for a shared bus.

import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_displayio_sh1107 import SH1107

def init_oled():
    """
    Initializes the OLED display and returns the display and the label reference.
    """
    displayio.release_displays()
    i2c = busio.I2C(scl=board.IO9, sda=board.IO8)
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3D)
    display = SH1107(display_bus, width=128, height=64)
    
    main_group = displayio.Group()
    display.root_group = main_group

    channel_label = label.Label(
        terminalio.FONT, text="", x=0, y=0, line_spacing=1.2
    )
    main_group.append(channel_label)

    return display, channel_label

def update_output(channel_map, label, verbose=False):
    """
    Updates the OLED label with 8-channel data.
    """
    label.text = "\n".join(
        [f"CH{i}: {channel_map[i]}" for i in sorted(channel_map.keys())]
    )

    if verbose:
        print("------------------------------")
        for i in sorted(channel_map.keys()):
            print(f"CH{i}: {channel_map[i]}")

