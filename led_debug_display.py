"""
led_debug_display.py

This module provides character display output for debugging using a 13x9 RGB LED array
driven by the IS31FL3741 over I2C. It defines a simple 5x7 font for a subset of characters
and includes a function to scroll text messages across the display.

Requirements:
- CircuitPython
- adafruit_is31fl3741 library (install via the Adafruit CircuitPython bundle)
- The display is assumed to be connected via a Stemma QT cable on the I2C bus.
"""

import time
import board
import busio

try:
    import adafruit_is31fl3741
except ImportError:
    raise ImportError("The adafruit_is31fl3741 library is required. Please install it from the Adafruit CircuitPython bundle.")

# Define a minimal 5x7 font for some characters.
# Each character is defined as a list of 7 integers (one per row), where each integer's 5 least significant bits
# represent the pixels in that row (1 = on, 0 = off). Bit 4 is the leftmost pixel.
FONT = {
    'A': [
        0b01110,
        0b10001,
        0b10001,
        0b11111,
        0b10001,
        0b10001,
        0b10001,
    ],
    'B': [
        0b11110,
        0b10001,
        0b10001,
        0b11110,
        0b10001,
        0b10001,
        0b11110,
    ],
    'C': [
        0b01110,
        0b10001,
        0b10000,
        0b10000,
        0b10000,
        0b10001,
        0b01110,
    ],
    'D': [
        0b11100,
        0b10010,
        0b10001,
        0b10001,
        0b10001,
        0b10010,
        0b11100,
    ],
    'E': [
        0b11111,
        0b10000,
        0b10000,
        0b11110,
        0b10000,
        0b10000,
        0b11111,
    ],
    'F': [
        0b11111,
        0b10000,
        0b10000,
        0b11110,
        0b10000,
        0b10000,
        0b10000,
    ],
    '0': [
        0b01110,
        0b10001,
        0b10011,
        0b10101,
        0b11001,
        0b10001,
        0b01110,
    ],
    '1': [
        0b00100,
        0b01100,
        0b00100,
        0b00100,
        0b00100,
        0b00100,
        0b01110,
    ],
    ' ': [  # Space
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b00000,
        0b00000,
    ],
}

# Dimensions of the LED array.
DISPLAY_WIDTH = 13
DISPLAY_HEIGHT = 9

class LEDDebugDisplay:
    def __init__(self, i2c=None):
        """
        Initialize the LED Debug Display.

        :param i2c: An initialized I2C bus (optional). If not provided, board.I2C() is used.
        """
        if i2c is None:
            i2c = board.I2C()
        # Initialize the IS31FL3741 display on the I2C bus.
        self.display = adafruit_is31fl3741.IS31FL3741(i2c)
        self.clear()

    def clear(self):
        """Turn off all the LEDs on the display."""
        for x in range(DISPLAY_WIDTH):
            for y in range(DISPLAY_HEIGHT):
                self.display.pixel(x, y, 0, 0, 0)

    def draw_char(self, char, x_offset=0, y_offset=0, color=(255, 255, 255)):
        """
        Draw a single character on the display using the 5x7 font.

        :param char: The character to draw.
        :param x_offset: The horizontal offset on the display.
        :param y_offset: The vertical offset on the display.
        :param color: A tuple (R, G, B) representing the color.
        """
        if char not in FONT:
            return
        glyph = FONT[char]
        for y, row in enumerate(glyph):
            for x in range(5):
                if row & (1 << (4 - x)):  # Check if the pixel is "on".
                    xx = x_offset + x
                    yy = y_offset + y
                    if 0 <= xx < DISPLAY_WIDTH and 0 <= yy < DISPLAY_HEIGHT:
                        self.display.pixel(xx, yy, *color)
                else:
                    # Optionally, turn off the pixel (if desired for blanking).
                    xx = x_offset + x
                    yy = y_offset + y
                    if 0 <= xx < DISPLAY_WIDTH and 0 <= yy < DISPLAY_HEIGHT:
                        self.display.pixel(xx, yy, 0, 0, 0)

    def scroll_message(self, message, delay=0.3, color=(255, 255, 255)):
        """
        Scroll a text message across the display.
        
        The display shows the message by scrolling it from right to left.
        
        :param message: The string message to scroll.
        :param delay: The delay (in seconds) between each scroll shift.
        :param color: The color for the text.
        """
        # Convert message to uppercase to match our font keys.
        message = message.upper()
        # Each character is 5 pixels wide plus 1 pixel spacing.
        total_length = len(message) * 6
        # Scroll from right edge of display to the left, over the entire message length.
        for offset in range(total_length + DISPLAY_WIDTH):
            self.clear()
            # For each character in the message:
            for i, char in enumerate(message):
                # Determine x-position for this character.
                x = DISPLAY_WIDTH - offset + i * 6
                # Only draw character if any part is on the display.
                if x < -5 or x >= DISPLAY_WIDTH:
                    continue
                self.draw_char(char, x_offset=x, y_offset=1, color=color)
            # Update the display; some libraries require an explicit show() call.
            self.display.show()
            time.sleep(delay)

# For testing purposes:
if __name__ == "__main__":
    debug_display = LEDDebugDisplay()
    while True:
        debug_display.scroll_message("DEBUG OK", delay=0.2)
