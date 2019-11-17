#!/usr/bin/env  python3

import sys
from time import sleep
import signal
import serial
from queue import Queue
from CircularBuffer import CircularBuffer


class globals:
    MY_NODE = 'gateway'  # TODO, read this from environment
    running = True

    # TODO, make this a ring buffer
    queue_buffer_max = 2500
    rxBuffer: CircularBuffer = CircularBuffer()

    xBee = serial.Serial('/dev/ttyUSB0', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)


# Setup ctrl-C
def ctrl_c(signum, frame):
    print("Stopping Gateway")
    globals.running = False
    globals.xBee.close()


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
        bytes: bytearray = globals.xBee.read(100)
        print("[got {0} bytes]".format(len(bytes)), end='')
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
            print("[{0}]".format(hex(item)), end='')
        else:
            print("Couldn't read in buffer!")
        
    print(".", flush=True, end='')


print("Exiting")
