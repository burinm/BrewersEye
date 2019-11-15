#!/usr/bin/env  python3

import threading
import time
from datetime import datetime
import board as BOARD
import RPi.GPIO as GPIO
GPIO.setwarnings(True)


class BubbleDetector:

    portBubblesIn: int = BOARD.D6.id
    bubbleCount: int = 0

    @staticmethod
    def bubbleCountDebounce():
        """ Really cheap debounce. The signal could
            conceivably have gone high and low again
        """

        # See if signal is still low after 25 millisecond timer pop
        if (GPIO.input(BubbleDetector.portBubblesIn) == GPIO.LOW):
            BubbleDetector.bubbleCount += 1
            print(time.time(), BubbleDetector.bubbleCount)
            print(time.localtime())
            print(round(datetime.now().timestamp(), 3))

    @staticmethod
    def countBubblesCallback(channel):
        """ Supposedly the GPIO library queues up edge events,
            so start a callback for each
        """
        threading.Timer(.025, BubbleDetector.bubbleCountDebounce).start()

    def __init__(self):
        self.channelList: list = None

    def setup(self):
        # Use portable pin numbers
        GPIO.setmode(GPIO.BCM)  # "board" library uses this scheme

        print(self.portBubblesIn)

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




