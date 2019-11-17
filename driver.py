#!/usr/bin/env  python3

import signal
import time
from bubbles import BubbleDetector
from max31855 import TypeKReader


def sendBubbleMessage(count: int, timestamp: float):
    print("![{0}]{1}".format(count, timestamp))


class globals():
    running = True
    bubbleCounter = BubbleDetector(sendBubbleMessage)
    temperatureReader = TypeKReader()


# Setup ctrl-C
def ctrl_c(signum, frame):
    print("Deconfigure bubbler port:{0}".format(globals.bubbleCounter.portBubblesIn))
    globals.bubbleCounter.teardown()
    globals.running = False


signal.signal(signal.SIGINT, ctrl_c)

globals.bubbleCounter.setup()

# Loop until stopped
while(globals.running):
    # Template from here:
    # https://learn.adafruit.com/thermocouple/python-circuitpython
    tempC = globals.temperatureReader.getTemperatureC()
    tempF = tempC * 9 / 5 + 32
    print('Temperature: {} C {} F '.format(tempC, tempF))
    time.sleep(2.0)

    pass

print("Exiting")
