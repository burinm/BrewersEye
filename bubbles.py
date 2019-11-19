#!/usr/bin/env  python3
""" bubbles.py - Count bubbles from a custom infrared sensor
        burin (c) 2019

    Currently the sensor is active low when it detects a bubble.
    An interrupt on low fires a timer 25 milli-seconds later. If
    the pin is still low, we count it as a bubble

    Input from the sensor is sent through an op-amp chain that:
        0) Takes the signal's derivative (DC blocking capacitor)
        1) High pass (.72Hz)
        2) Low pass (3.4Hz) and gain x101
        3) High pass (.72Hz)
        4) Low pass (3.4Hz) and gain x101
        5) Buffer stage
        6) Invert with BJT

    Gain = 1 + (R2/R1)
        R2 = 470K, R1 = 4.7K, gain = 101

    High pass
        f Hz (cutoff) = 1 / (2Pi * R * C)
        R = 47K, C = 4.7uF, f(cuttoff) = .72Hz  (1.4 seconds)

    Low Pass
        f Hz (cutoff) = 1 / (2Pi * R * C)
        R = 470K, C q 100 nF, f(cutoff) = 3.4Hz (.295 seconds)

    This means (in thoery) that any change in LED intensity
    that isn't at least .295 seconds long, and isn't longer
    than 1.4 seconds shouldn't even make it into the GPIO pin


"""

import threading
from MessageProtocol import getCurrentTimestamp
import board as BOARD
import RPi.GPIO as GPIO
from typing import Callable

# Use portable pin numbers
GPIO.setmode(GPIO.BCM)  # "board" library uses this scheme
GPIO.setwarnings(False)


class BubbleDetector:

    portBubblesIn: int = BOARD.D6.id
    bubbleCount: int = 0
    bubbleEvent: Callable[[None], None] = None

    @staticmethod
    def bubbleCountDebounce():
        """ Really cheap debounce. The signal could
            conceivably have gone high and low again
        """

        # See if signal is still low after 25 millisecond timer pop
        if (GPIO.input(BubbleDetector.portBubblesIn) == GPIO.LOW):
            BubbleDetector.bubbleCount += 1
            BubbleDetector.bubbleEvent()

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
