#!/usr/bin/env  python3

import threading
import time
from datetime import datetime
import signal
import board as BOARD
import RPi.GPIO as GPIO
GPIO.setwarnings(True)


class globals():
    running = True
    bubbleCount = 0


# Setup ctrl-C
def ctrl_c(signum, frame):
    GPIO.cleanup(channelList)
    globals.running = False


def bubbleCountDebounce():
    """ Really cheap debounce. The signal could
        conceivably have gone high and low again
    """

    # See if signal is still low after 25 millisecond timer pop
    if (GPIO.input(portBubblesIn) == GPIO.LOW):
        globals.bubbleCount += 1
        print(time.time(), globals.bubbleCount)
        print(time.localtime())
        print(round(datetime.now().timestamp(), 3))


def countBubblesCallback(channel):
    """ Supposedly the GPIO library queues up edge events,
        so start a callback for each
    """
    threading.Timer(.025, bubbleCountDebounce).start()


signal.signal(signal.SIGINT, ctrl_c)

# Use portable pin numbers
GPIO.setmode(GPIO.BCM)  # "board" library uses this scheme

# portBubblesIn = BOARD.D6
portBubblesIn = BOARD.D6.id
print(portBubblesIn)

channelList = [portBubblesIn]


# Set up bubble detector Port6
GPIO.setup(portBubblesIn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(portBubblesIn, GPIO.FALLING, callback=countBubblesCallback)

# Loop until stopped
while(globals.running):
    pass

print("Exiting")
