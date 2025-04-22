# /gnss_dfrobot.py
# DFRobot GNSS module parser over I2C (proprietary format)
# Author: savant42

import time

GNSS_I2C_ADDR = 0x20
GNSS_REG_LAT = 0x10
GNSS_REG_LON = 0x18
GNSS_REG_ALT = 0x20
GNSS_REG_SPD = 0x28
GNSS_REG_CRS = 0x2C
GNSS_REG_SATS = 0x30
GNSS_REG_TIME = 0x00

from struct import unpack

class GNSS:
    def __init__(self, i2c, address=GNSS_I2C_ADDR):
        self.i2c = i2c
        self.addr = address

    def _read_bytes(self, reg, length):
        buf = bytearray(length)
        with self.i2c_device() as i2c:
            i2c.writeto_then_readfrom(self.addr, bytes([reg]), buf)
        return buf

    def i2c_device(self):
        from adafruit_bus_device.i2c_device import I2CDevice
        return I2CDevice(self.i2c, self.addr)

    def get_gnss_data(self):
        data = {}

        # Time
        t = self._read_bytes(GNSS_REG_TIME, 7)
        data['utc'] = f"20{t[0]:02d}-{t[1]:02d}-{t[2]:02d}T{t[3]:02d}:{t[4]:02d}:{t[5]:02d}Z"

        # Latitude
        lat_buf = self._read_bytes(GNSS_REG_LAT, 8)
        lat_deg, lat_min_whole, lat_min_frac, lat_dir = lat_buf[0], lat_buf[1], (lat_buf[2] << 8) + lat_buf[3], chr(lat_buf[7])
        data['lat'] = self._convert_degmin(lat_deg, lat_min_whole, lat_min_frac, lat_dir)

        # Longitude
        lon_buf = self._read_bytes(GNSS_REG_LON, 8)
        lon_deg, lon_min_whole, lon_min_frac, lon_dir = lon_buf[0], lon_buf[1], (lon_buf[2] << 8) + lon_buf[3], chr(lon_buf[7])
        data['lon'] = self._convert_degmin(lon_deg, lon_min_whole, lon_min_frac, lon_dir)

        # Altitude
        alt_buf = self._read_bytes(GNSS_REG_ALT, 4)
        data['alt'] = unpack('<f', alt_buf)[0]

        # Speed (m/s)
        spd_buf = self._read_bytes(GNSS_REG_SPD, 4)
        data['speed_mps'] = unpack('<f', spd_buf)[0]

        # Course (degrees)
        crs_buf = self._read_bytes(GNSS_REG_CRS, 4)
        data['course'] = unpack('<f', crs_buf)[0]

        # Satellites
        sats_buf = self._read_bytes(GNSS_REG_SATS, 1)
        data['sats'] = sats_buf[0]

        return data

    def _convert_degmin(self, deg, min_whole, min_frac, direction):
        minutes = min_whole + (min_frac / 10000.0)
        decimal = deg + (minutes / 60.0)
        if direction in ['S', 'W']:
            decimal *= -1
        return decimal
