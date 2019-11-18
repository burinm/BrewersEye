#!/usr/bin/env  python3

import sys
import signal
import time
from queue import Queue
from threading import Timer
from bubbles import BubbleDetector
from max31855 import TypeKReader
from message import getCurrentTimestamp, parseMessage, createTemperatureMessage, createBubbleMessage, printRawMessage, parseMessage
import serial


def queueMessage(m: bytearray):
    if globals.sendQ.full():  # More recent data take precedence
        globals.sendQ.get(block=False)
        print("!send queue full, removed item!")

    try:
        globals.sendQ.put(m, block=False, timeout=.250)
    except globals.sendQ.Full:
        print("Akk - send queue still full!")
        pass


def queueBubbleMessage(count: int, timestamp: float):
    m = createBubbleMessage(globals.MY_NODE, timestamp)
    print("[bubble:{0} {1}]".format(timestamp, count))
    queueMessage(m)


def queueTemperarureMessage(timestamp: float, temperature: float):
    m = createTemperatureMessage(globals.MY_NODE, timestamp, temperature)
    print("[temperature:{0} {1}]".format(timestamp, temperature))
    queueMessage(m)


def readTemperature():
    tempC = globals.temperatureReader.getTemperatureC()
    queueTemperarureMessage(getCurrentTimestamp(), tempC)
    globals.temperatureTimer = Timer(2.0,  readTemperature)
    globals.temperatureTimer.start()


def publishMessage(m: bytearray):
    parseMessage(m)
    globals.xBee.write(m)
    pass


class globals:
    MY_NODE = 88  # TODO, read this from environment
    max_messages = 100
    message_count = 0

    running = True
    bubbleCounter = BubbleDetector(queueBubbleMessage)
    temperatureReader = TypeKReader()
    temperatureTimer: Timer = Timer(2.0,  readTemperature)
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


# Loop until stopped
while(globals.running):
    if (globals.sendQ.empty() is False):
        try:
            msg = globals.sendQ.get_nowait()
            globals.sendQ.task_done()
            publishMessage(msg)
        except Queue.Empty:
            print("Tried to read empty Q")


globals.xBee.close()
print("Exiting")
