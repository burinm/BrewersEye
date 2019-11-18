#!/usr/bin/env  python3

import sys
from time import sleep
import signal
import serial
from CircularBuffer import CircularBuffer
from MessageParser import MessageStreamParser


class globals:
    MY_NODE = 'gateway'  # TODO, read this from environment
    running = True

    # Try to read n bytes from serial port, then unblock
    NUM_BYTES_TO_READ: int = 10

    # Ring buffer for incoming data stream
    rxBuffer: CircularBuffer = CircularBuffer()

    xBee = serial.Serial('/dev/ttyUSB0', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)
    msgParser: MessageStreamParser = MessageStreamParser()


# Setup ctrl-C
def ctrl_c(signum, frame):
    print("Stopping Gateway")
    globals.running = False


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


# Loop until stopped
while(globals.running):
    if globals.xBee.is_open:
        bytes: bytearray = globals.xBee.read(globals.NUM_BYTES_TO_READ)
        # print("[got {0} bytes]".format(len(bytes)), end='')
        for i in bytes:
            globals.rxBuffer.put(i)
    else:
        sleep(2.0)
        try:
            globals.xBee.open()
        except serial.SerialException as e:
            print(e)

    while(globals.rxBuffer.has_items()):
        [result, item] = globals.rxBuffer.get()
        if result is True:
            # print("[{0}]".format(hex(item)), end='')
            globals.msgParser.parseDataStream(item)
        else:
            print("Couldn't read in buffer!")

    print(".", flush=True, end='')


globals.xBee.close()
print("Exiting")
