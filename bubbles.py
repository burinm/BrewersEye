#!/usr/bin/env  python3

import threading
from MessageProtocol import getCurrentTimestamp
from datetime import datetime
import board as BOARD
import RPi.GPIO as GPIO
from typing import Callable

# Use portable pin numbers
GPIO.setmode(GPIO.BCM)  # "board" library uses this scheme
GPIO.setwarnings(False)


class BubbleDetector:

    portBubblesIn: int = BOARD.D6.id
    bubbleCount: int = 0
    bubbleEvent: Callable[[float], None] = None

    @staticmethod
    def bubbleCountDebounce():
        """ Really cheap debounce. The signal could
            conceivably have gone high and low again
        """

        # See if signal is still low after 25 millisecond timer pop
        if (GPIO.input(BubbleDetector.portBubblesIn) == GPIO.LOW):
            BubbleDetector.bubbleCount += 1
            BubbleDetector.bubbleEvent(BubbleDetector.bubbleCount, getCurrentTimestamp())

    @staticmethod
    def countBubblesCallback(channel):
        """ Supposedly the GPIO library queues up edge events,
            so start a callback for each
        """
        threading.Timer(.025, BubbleDetector.bubbleCountDebounce).start()

    def __init__(self, callback: Callable[[int, float], None]):
        """ Takes a callback function that will return:
                int - total count/index of bubble event since start
                float - timestamp for event
        """
        self.channelList: list = None
        BubbleDetector.bubbleEvent = callback

    def setup(self):

        print("Opening bubbler input on port:{0}".format(self.portBubblesIn))

        self.channelList = [self.portBubblesIn]

        # Set up bubble detector falling edge of input, pull-up ON
        # https://elinux.org/RPi_Low-level_peripherals#Internal_Pull-Ups_.26_Pull-Downs
        #   pull up is 50-65k Ohms
        #   pull down is 50-60k Ohms
        GPIO.setup(self.portBubblesIn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.portBubblesIn,
                              GPIO.FALLING,
                              callback=BubbleDetector.countBubblesCallback)

    def teardown(self):
        GPIO.cleanup(self.channelList)
