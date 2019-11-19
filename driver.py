#!/usr/bin/env  python3

import sys
import signal
from enum import IntEnum
from queue import Queue
from threading import Timer
from bubbles import BubbleDetector
from max31855 import TypeKReader
from MessageProtocol import getCurrentTimestamp, parseMessage, createTemperatureMessage, createBubbleMessage, printRawMessage
import serial
import max31820
# https://docs.python.org/2/library/functools.html
from functools import partial
from datetime import datetime

class sensorsState:
    temp1: int = None
    temp2: int = None
    temp3: int = None
    bubbles: int = 0


def countBubbles():
    print('[b]', end = '')
    globals.sensors.bubbles += 1


def queueMessage(m: bytearray):
    if globals.sendQ.full():  # More recent data take precedence
        globals.sendQ.get(block=False)
        print("!send queue full, removed item!")

    try:
        globals.sendQ.put(m, block=False, timeout=.250)
    except globals.sendQ.Full:
        print("Akk - send queue still full!")
        pass


def queueBubbleMessage(timestamp: float, count: int):
    m = createBubbleMessage(globals.MY_NODE, timestamp, count)
    print("[bubble:{0} {1}]".format(timestamp, count))
    queueMessage(m)


def queueTemperarureMessage(timestamp: float, temperature: float):
    m = createTemperatureMessage(globals.MY_NODE, timestamp, temperature)
    print("[temperature:{0} {1}]".format(timestamp, temperature))
    queueMessage(m)


# Loop through sensors each timer pop
def readTemperature():
    if globals.temperatureState == readState.TYPE_K:
        tempC = globals.temperatureReaderTypeK.getTemperatureC()
        print("Read type-k:{0}".format(tempC))
        globals.sensors.temp1 = tempC
    elif globals.temperatureState == readState.INSIDE:
        tempC = globals.temperatureReaderInside()
        globals.sensors.temp2 = tempC
        print("Read inside:{0}".format(tempC))
    elif globals.temperatureState == readState.OUTSIDE:
        tempC = globals.temperatureReaderOutside()
        globals.sensors.temp2 = tempC
        print("Read outside:{0}".format(tempC))

    globals.temperatureState += 1
    if globals.temperatureState == readState.LAST:
        globals.temperatureState = readState.TYPE_K

    if (globals.running):
        globals.temperatureTimer = Timer(2.0,  readTemperature)
        globals.temperatureTimer.start()


def publishMessage(m: bytearray):
    parseMessage(m)  # Sanity check format
    globals.xBee.write(m)
    pass


class readState(IntEnum):
    TYPE_K = 0
    INSIDE = 1
    OUTSIDE = 2
    LAST = 3


class globals:
    MY_NODE = 88  # TODO, read this from environment
    max_messages = 100
    message_count = 0

    running = True
    sensors: sensorsState = sensorsState()

    # Sensor hooks
    bubbleCounter = BubbleDetector(countBubbles)
    temperatureReaderTypeK = TypeKReader()
    temperatureReaderInside = partial(max31820.getTempC, 'inside')
    temperatureReaderOutside = partial(max31820.getTempC, 'outside')

    # Sensor read timer
    temperatureTimer: Timer = Timer(2.0,  readTemperature)
    temperatureState: int = readState.TYPE_K

    # Queue for outgoing messages
    sendQ: Queue = Queue(max_messages)

    xBee = serial.Serial('/dev/ttyUSB0', baudrate=115200, bytesize=8, parity='N', stopbits=1)


# Setup ctrl-C
def ctrl_c(signum, frame):
    globals.running = False
    print("Deconfigure bubbler port:{0}".format(globals.bubbleCounter.portBubblesIn))
    globals.bubbleCounter.teardown()
    globals.temperatureTimer.cancel()


signal.signal(signal.SIGINT, ctrl_c)

if globals.xBee.is_open:
    try:
        globals.xBee.close()
    except serial.SerialException as e:
        print(e)
        sys.exit()

try:
    globals.xBee.open()
except serial.SerialException as e:
    print(e)
    sys.exit()

globals.bubbleCounter.setup()
globals.temperatureTimer.start()

timing = datetime.now().timestamp()
nextSend = timing + 5.0  # Send first message 5 seconds from now
NEXT_M = 5.0  # Messages send every NEXT_M seconds

# Loop until stopped
while(globals.running):
    if (globals.sendQ.empty() is False):
        try:
            msg = globals.sendQ.get_nowait()
            globals.sendQ.task_done()
            publishMessage(msg)
        except Queue.Empty:
            print("Tried to read empty Q")

    timing = datetime.now().timestamp()
    if (timing > nextSend):
        """ TODO -
                Timers/interrupts are still running and updating
                the counters. Possibly pause timers?

                For now, read/reset bubbles right away
        """
        bubble_count = globals.sensors.bubbles
        globals.sensors.bubbles = 0

        if globals.sensors.temp1 is not None:
            queueTemperarureMessage(getCurrentTimestamp(),
                                    globals.sensors.temp1)

        if globals.sensors.bubbles is not None:
            timediff = timing - nextSend + NEXT_M
            if (timediff > 0):  # Shouldn't happen, but...
                # Bubble average is bubbles per hundred seconds
                bubbleAverage = bubble_count * 100 / timediff
                queueBubbleMessage(getCurrentTimestamp(),
                                   int(bubbleAverage))

        nextSend = timing + NEXT_M  # Schedule next message


globals.xBee.close()
print("Exiting")
