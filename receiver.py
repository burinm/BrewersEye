#!/usr/bin/env  python3
""" receiver.py - A Brewer's Eye gateway
    burin (c) 2019

    Responsoble from receiving messages from remote
    Zigbee nodes, repackaging and forwarding to
    remote web services

    *Note* - currently, if multiple nodes send
    messages at the same time, this code will blow up!
"""

import sys
from time import sleep
from datetime import datetime
import signal
import serial
from CircularBuffer import CircularBuffer
from MessageParser import MessageStreamParser
from MessageProtocol import beMessageType
import thingspeak


class sensorData:
    inside: float = None
    outside: float = None
    bubbles: int = None


def recieveMessageCallback(o: object) -> None:
    print("-->{0}".format(o))
    if 'type' in o:
        payload = o['data']

        # Fill in the latest date we have, overwrite current
        if o['type'] == beMessageType.BE_MSG_TYPE_TEMPERATURE.value:
            print("Processing temperature message")
            if payload['idx'] == 0:
                globals.currentData.inside = float(payload['temp'])
            elif payload['idx'] == 1:
                globals.currentData.outside = float(payload['temp'])
        elif o['type'] == beMessageType.BE_MSG_TYPE_BUBBLE.value:
            print("Processing bubble message")
            globals.currentData.bubbles = payload['avg']


class globals:
    MY_NODE = 'gateway'  # TODO, read this from environment
    running = True

    # Try to read n bytes from serial port, then unblock
    NUM_BYTES_TO_READ: int = 10

    # Ring buffer for incoming data stream
    rxBuffer: CircularBuffer = CircularBuffer()

    # Sets up serial port. Xbee is in Transparent Mode
    xBee = serial.Serial('/dev/ttyUSB0',
                         baudrate=115200,
                         bytesize=8,
                         parity='N',
                         stopbits=1,
                         timeout=1)

    msgParser: MessageStreamParser = MessageStreamParser(recieveMessageCallback)

    currentData: sensorData = sensorData()


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

timing = datetime.now().timestamp()
# Send first thingspeak updatemessage 15 seconds from now
nextThingspeakUpdate = timing + 15.0


# Loop until stopped
while(globals.running):
    if globals.xBee.is_open:
        bytes: bytearray = globals.xBee.read(globals.NUM_BYTES_TO_READ)
        # print("[got {0} bytes]".format(len(bytes)), end='')
        for i in bytes:
            globals.rxBuffer.put(i)
    else:  # This branch has never been tried...
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

    timing = datetime.now().timestamp()
    if (timing > nextThingspeakUpdate):
        if globals.currentData.inside is not None and \
           globals.currentData.outside is not None and \
           globals.currentData.bubbles is not None:
            thingspeak.updateChannel(globals.currentData.inside,
                                     globals.currentData.outside,
                                     globals.currentData.bubbles)

            # 30 second updates
            nextThingspeakUpdate = timing + 30.0


# Exit
globals.xBee.close()
print("Exiting")
