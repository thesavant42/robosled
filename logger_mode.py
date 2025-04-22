# /log__to_oled_display.py
# hardcoded non-shared bus
# Do not use as-is on a shared bus
# hard coded rotation and resolution
import time
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_displayio_sh1107 import SH1107
import board
import busio
from adafruit_bitmap_font import bitmap_font

# External data modules
import gps  # Replaces direct import to avoid import error
from robot_state import get_robot_state

# LIS3DH setup
import adafruit_lis3dh

# I2C and Display setup
i2c = busio.I2C(scl=board.IO9, sda=board.IO8)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3D)
display = SH1107(display_bus, width=128, height=128, rotation=90)

# LIS3DH init
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x18)
lis3dh.range = adafruit_lis3dh.RANGE_2_G

# Load Droid font
font = bitmap_font.load_font("/DroidobeshDepot-12.bdf") # We made this

# Display group
main_group = displayio.Group()
display.show(main_group)

# Label for output
output_label = label.Label(font=font, text="...", x=0, y=8, line_spacing=1.1)
main_group.append(output_label)

# Page state
page = 0
last_update = time.monotonic()
PAGE_INTERVAL = 2  # seconds

while True:
    now = time.monotonic()
    if now - last_update >= PAGE_INTERVAL:
        last_update = now
        page = (page + 1) % 3

        # Get live robot state
        state = get_robot_state()  # dict with keys: throttle_pct, pivot_pct, brake, mode
        gps_data = gps.get_gnss_data()  # dict with speed_kph, lat, lon, sats
        accel_xyz = lis3dh.acceleration  # tuple (x, y, z)

        accel = {
            "x": accel_xyz[0] / 9.806,  # convert m/s^2 to g approx
            "y": accel_xyz[1] / 9.806,
            "z": accel_xyz[2] / 9.806
        }

        if page == 0:
            # Throttle, Pivot, Brake, Mode
            text = ""
            text += f"THR {state['throttle_pct']:>3}%\n"
            text += f"PVT {state['pivot_pct']:>3}%\n"
            if state['brake']:
                output_label.color = 0xFF0000  # Red
                text += "[ BRAKE ]\n"
            else:
                output_label.color = 0xFFFFFF  # White
                text += "[   RUN  ]\n"
            text += f"MODE {state['mode']}"

        elif page == 1:
            # GPS Page
            text = ""
            text += f"SPD: {gps_data['sog']:.1f} kt\n"
            text += f"LAT: {gps_data['lat']:.5f}\n"
            text += f"LON: {gps_data['lon']:.5f}\n"
            text += f"SAT: {gps_data['sats']}"
            output_label.color = 0xFFFF00  # Yellow for speed emphasis

        elif page == 2:
            # Accelerometer Page
            text = ""
            text += f"X: {accel['x']:.2f}g\n"
            text += f"Y: {accel['y']:.2f}g\n"
            text += f"Z: {accel['z']:.2f}g"
            output_label.color = 0xFFFFFF

        output_label.text = text

    time.sleep(0.05)
