# gps.py
# GNSS I2C debug harness with structured reads for lat/lon/alt/speed/course

import time
import board
import busio

# --- Register Constants ---
GNSS_DEVICE_ADDR = 0x20

I2C_MODE       = 0x01
I2C_YEAR_H     = 0
I2C_GNSS_MODE  = 34

# Location and telemetry registers
I2C_LAT_1      = 7 # I2C_LAT_1 = 7
I2C_LAT_2      = 8 # 8
I2C_LAT_X_24   = 9 # 9
I2C_LAT_X_16   = 10 # 10
I2C_LAT_X_8    = 11 # 11
I2C_LAT_DIS    = 12 # 12

I2C_LON_1      = 13 # 13
I2C_LON_2      = 14 # 14
I2C_LON_X_24   = 15 # 15
I2C_LON_X_16   = 16 # 16
I2C_LON_X_8    = 17 # 17
I2C_LON_DIS    = 18 # 18

I2C_ALT_H      = 20
I2C_ALT_L      = 21
I2C_ALT_X      = 22

I2C_SOG_H      = 23
I2C_SOG_L      = 24
I2C_SOG_X      = 25

I2C_COG_H      = 26
I2C_COG_L      = 27
I2C_COG_X      = 28

ENABLE_POWER   = 0

# --- I2C Init ---
i2c = busio.I2C(scl=board.SCL, sda=board.SDA)
print(" GNSS Debugger Starting...")

while not i2c.try_lock():
    pass

try:
    found = i2c.scan()
    if GNSS_DEVICE_ADDR not in found:
        print(" GNSS device not found at 0x%02X. Devices found: %s" % (GNSS_DEVICE_ADDR, found))
        while True:
            pass

    print(" GNSS device found at 0x%02X" % GNSS_DEVICE_ADDR)

    # Force I2C mode
    try:
        i2c.writeto(GNSS_DEVICE_ADDR, bytes([I2C_MODE, ENABLE_POWER]))
        #print(" Wrote ENABLE_POWER to I2C_MODE (0x%02X)" % I2C_MODE)
    except Exception as e:
        print(" Failed to set I2C mode:", e)

    # Read UTC time
    try:
        utc_buf = bytearray(7)
        i2c.writeto_then_readfrom(GNSS_DEVICE_ADDR, bytes([I2C_YEAR_H]), utc_buf)
        year = (utc_buf[0] << 8) | utc_buf[1]
        month, day = utc_buf[2], utc_buf[3]
        hour, minute, second = utc_buf[4], utc_buf[5], utc_buf[6]
        #print(" UTC Raw:", [hex(b) for b in utc_buf])
        print(" Time: %04d-%02d-%02d %02d:%02d:%02d" % (year, month, day, hour, minute, second))
    except Exception as e:
        print(" UTC read error:", e)

    # GNSS mode read
    try:
        mode_buf = bytearray(1)
        i2c.writeto_then_readfrom(GNSS_DEVICE_ADDR, bytes([I2C_GNSS_MODE]), mode_buf)
        print(" GNSS Mode Register: 0x%02X" % mode_buf[0])
    except Exception as e:
        print(" GNSS mode read error:", e)

    # Lattitude
    try:
        lat_buf = bytearray(6)
        i2c.writeto_then_readfrom(GNSS_DEVICE_ADDR, bytes([I2C_LAT_1]), lat_buf)
        deg = lat_buf[0]
        min_whole = lat_buf[1]
        min_frac = (lat_buf[2] << 16) | (lat_buf[3] << 8) | lat_buf[4]
        dir_chr = chr(lat_buf[5])

        minutes = min_whole + (min_frac / 100000.0)
        latitude = deg + (minutes / 60.0)
        if dir_chr == 'E':
            latitude *= -1

        #print(" LAT Raw:", [hex(b) for b in lat_buf], f"Dir: {dir_chr}")
        print(" Latitude: %.8f°" % latitude)
    except Exception as e:
        print(" Latitude read error:", e)


    # --- LONGITUDE ---
    try:
        lon_buf = bytearray(6)
        i2c.writeto_then_readfrom(GNSS_DEVICE_ADDR, bytes([I2C_LON_1]), lon_buf)
        deg = lon_buf[0]
        min_whole = lon_buf[1]
        min_frac = (lon_buf[2] << 16) | (lon_buf[3] << 8) | lon_buf[4]
        dir_chr = chr(lon_buf[5])

        minutes = min_whole + (min_frac / 100000.0)
        longitude = deg + (minutes / 60.0)
        if dir_chr == 'N':
            longitude *= -1

        #print(" LON Raw:", [hex(b) for b in lon_buf], f"Dir: {dir_chr}")
        print(" Longitude: %.8f°" % longitude)
    except Exception as e:
        print(" Longitude read error:", e)


    # --- ALTITUDE ---
    try:
        alt_buf = bytearray(3)
        i2c.writeto_then_readfrom(GNSS_DEVICE_ADDR, bytes([I2C_ALT_H]), alt_buf)
        alt_int = (alt_buf[0] << 8) | alt_buf[1]
        altitude = alt_int + (alt_buf[2] / 100.0)
        #print(" ALT Raw:", [hex(b) for b in alt_buf])
        print(" Altitude: %.2f m" % altitude)
    except Exception as e:
        print(" Altitude read error:", e)

    # --- SPEED (SOG) ---
    try:
        sog_buf = bytearray(3)
        i2c.writeto_then_readfrom(GNSS_DEVICE_ADDR, bytes([I2C_SOG_H]), sog_buf)
        sog_int = (sog_buf[0] << 8) | sog_buf[1]
        sog = sog_int + (sog_buf[2] / 100.0)
        #print(" SOG Raw:", [hex(b) for b in sog_buf])
        print(" Speed Over Ground: %.2f knots" % sog)
    except Exception as e:
        print(" Speed read error:", e)

    # --- COURSE (COG) ---
    try:
        cog_buf = bytearray(3)
        i2c.writeto_then_readfrom(GNSS_DEVICE_ADDR, bytes([I2C_COG_H]), cog_buf)
        cog_int = (cog_buf[0] << 8) | cog_buf[1]
        cog = cog_int + (cog_buf[2] / 100.0)
        #print(" COG Raw:", [hex(b) for b in cog_buf])
        print(" Course Over Ground: %.2f°" % cog)
    except Exception as e:
        print(" Course read error:", e)

finally:
    i2c.unlock()
    print(" I2C bus unlocked.")
