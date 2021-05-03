"""Implements a HD44780 character LCD connected via PCF8574 on I2C.
   This was tested with: https://www.wemos.cc/product/d1-mini.html"""

from lcd_api import LcdApi
from machine import I2C,Board
from time import sleep

# The PCF8574 has a jumper selectable address: 0x20 - 0x27
DEFAULT_I2C_ADDR = 0x38

# Defines shifts or masks for the various LCD line attached to the PCF8574

MASK_RS = 0x01
MASK_RW = 0x02
MASK_E = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4

def sleep_ms(ms : int):
    sleep(ms/1000)

def sleep_ns(ns:int):
    sleep(ns / 1000000)


class I2cLcd(LcdApi):
    """Implements a HD44780 character LCD connected via PCF8574 on I2C."""

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        LcdApi.__init__(self, num_lines, num_columns)
        cmd = self.LCD_FUNCTION
        if num_lines > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)

    def hal_write_init_nibble(self, nibble):
        """Writes an initialization nibble to the LCD.
        This particular function is only used during initialization.
        """
        byte = ((nibble >> 4) & 0x0f) << SHIFT_DATA
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))

    def hal_backlight_on(self):
        """Allows the hal layer to turn the backlight on."""
        self.i2c.writeto(self.i2c_addr, bytearray([1 << SHIFT_BACKLIGHT]))
        sleep(0.05)

    def hal_backlight_off(self):
        """Allows the hal layer to turn the backlight off."""
        self.i2c.writeto(self.i2c_addr, bytearray([0]))
        sleep(0.05)

    def hal_write_command(self, cmd):
        """Writes a command to the LCD.
        Data is latched on the falling edge of E.
        """
        mbyte = ((1 << 3) | (((cmd >> 4) & 0x0f) << 4))
        self.i2c.writeto(self.i2c_addr, bytearray([mbyte]))
        lbyte = ((1 << 3) | ((cmd & 0x0f) << 4))
        self.i2c.writeto(self.i2c_addr, bytearray([lbyte]))
        # print(f"cmd {cmd} {bin(mbyte)[2:]:>08} {bin(lbyte)[2:]:>08} {bin((mbyte & 0xF0) | lbyte >> 4)[2:]:>08} {bin(cmd)[2:]:>08}")

    def hal_write_data(self, data):
        """Write data to the LCD."""
        mbyte = (1 | (1 << 3) | (((data >> 4) & 0x0f) << 4))
        self.i2c.writeto(self.i2c_addr, bytearray([mbyte]))
        lbyte = (1 | (1 << 3) | ((data & 0x0f) << 4))
        self.i2c.writeto(self.i2c_addr, bytearray([lbyte]))
        # print(f"data {data} {bin(mbyte)[2:]:>08} {bin(lbyte)[2:]:>08} {bin((mbyte & 0xF0) | lbyte >> 4)[2:]:>08} {bin(data)[2:]:>08}")