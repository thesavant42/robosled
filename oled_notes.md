# OLED Display Reference – SH1107 (Adafruit 1.12" 128x128)

## 🖼️ Display Overview
- **Model:** Adafruit 1.12" 128x128 Monochrome OLED
- **Driver:** SH1107
- **Dimensions:** 128 × 128 (square)
- **Color:** Monochrome (1-bit)
- **Bus:** I2C
- **I2C Address:** `0x3D` (⚠️ not the default `0x3C`)
- **Rotation:** `rotation=90` (✅ never 270, always 90 for proper upright text)

---

## ⚠️ CircuitPython 9.x Display Quirks

### 1. `.show()` Removed
- ❌ `display.show(group)` → removed in CP9+
- ✅ Replace with `display.root_group = group`

### 2. `SCL in use` Bug on FeatherS3
- On soft reboot or exception, `busio.I2C` may retain lock state on the SCL pin.
- This causes silent failures when initializing display hardware.

### ✅ Fix:
```python
while not i2c.try_lock():
    pass
try:
    devices = i2c.scan()  # Optional, helps confirm OLED presence (expect '0x3d')
finally:
    i2c.unlock()
```
This safely resets the bus lock and clears hardware contention.

---

## ✅ Working Configuration

```python
from adafruit_displayio_sh1107 import SH1107

# Display bus
display_bus = displayio.I2CDisplay(i2c, device_address=0x3D)

# Display instance
display = SH1107(
    display_bus,
    width=128,
    height=128,
    rotation=90
)

# Display group handling (CircuitPython 9.x)
display.root_group = displayio.Group()
```

---

## 🧠 Notes
- Never assume I2C address; always validate via scan.
- Always clear lock state before initializing peripherals.
- Always set display rotation explicitly — default may be wrong.
- This display is square, not rectangular — layout logic must account for vertical space.

