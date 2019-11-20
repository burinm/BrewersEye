#!/usr/bin/env  python3
""" max31855.py - Code to read the type-k SPI peripheral

    Template from here:
        https://learn.adafruit.com/thermocouple/python-circuitpython

    TODO:
    This code probably needs some error checking!
    We are always assuming max31855.temperature
    returns a sane value.
"""

import board
import busio
import digitalio
import adafruit_max31855

ERROR = True
OK = False


class TypeKReader:
    SCK = board.SCK  # 11
    MOSI = board.MOSI  # 10 unused on max31855
    MISO = board.MISO  # 9

    def __init__(self):
        self.spi = busio.SPI(self.SCK, MOSI=self.MOSI, MISO=self.MISO)
        self.cs = digitalio.DigitalInOut(board.D5)
        self.max31855 = adafruit_max31855.MAX31855(self.spi, self.cs)

    def teardown():
        pass  # TODO?

    def getTemperatureC(self):
        try:
            return [OK, self.max31855.temperature]
        except RuntimeError as e:
            print("Type-k read failed:{0}".format(e))
            return [ERROR, None]

""" Test
import time
print('Temperature: {} degrees C'.format(max31855.temperature))

while True:
    tempC = max31855.temperature
    tempF = tempC * 9 / 5 + 32
    print('Temperature: {} C {} F '.format(tempC, tempF))
    time.sleep(2.0)
"""
