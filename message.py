#!/usr/bin/env  python3
from enum import IntEnum
from datetime import datetime
import json

""" Brewer's Eye message format  utf-8

   [0][1][2][3] .... data (json)  [59]
     \  \  \  \
      \  \  \  Message payload length (0-255)
       \  \  Message Type
        \  Node number (0-255)
         '@' Message start identifier

    JSON keys:
        temp = temperature in Celcius, float
        time = timestamp, local time in seconds past epoch

"""

BE_MESSAGE_MAX_LEN = 60
BE_MESSAGE_HEADER = ord('@'.encode('utf-8'))


class beMessageType(IntEnum):
    BE_MSG_TYPE_TEMPERATURE = 0
    BE_MSG_TYPE_BUBBLE = 1


class beMessage(IntEnum):
    HEADER = 0
    NODE = 1
    TYPE = 2
    LENGTH = 3
    MESSAGE = 4


def getCurrentTimestamp() -> float:
    return round(datetime.now().timestamp(), 3)


def createMessageHeader(node: int, t: beMessageType) -> bytearray:
    if node > 255:
        raise Exception('beNodeNumerOutOfRange')

    if t > 255:
        raise Exception('beMessageTypeOutOfRange')

    m = bytearray([BE_MESSAGE_HEADER, ])
    m += bytes([node, ])
    m += bytes([t.value, ])

    return m


def parseMessage(m: bytearray) -> object:
    if len(m) > BE_MESSAGE_MAX_LEN:
        raise Exception('beMessageIncorrectFormat')

    if m[beMessage.HEADER.value] != BE_MESSAGE_HEADER:
        print("Found:[{0}]".format(m[beMessage.HEADER.value]))
        raise Exception('beMessageHeaderFormat')

    # for i in m:
    #    print("[{0}]".format(i))

    node = m[beMessage.NODE.value]
    messageType = m[beMessage.TYPE.value]
    messageLength = m[beMessage.LENGTH.value]

    if messageLength > BE_MESSAGE_MAX_LEN:
        raise Exception('beMessageDataLengthOverflow')

    print("Node: {0}".format(node))
    print("Type: [{0}]".format(beMessageType(messageType).name))
    print("Length: {0}".format(messageLength))

    jsonMessage = m[beMessage.MESSAGE.value: beMessage.MESSAGE.value + messageLength + 1]
    jsonObject = json.loads(jsonMessage)
    print(jsonObject)

    return jsonObject


def createTemperatureMessage(node: int, timestamp: float, temperature: float) -> bytearray:

    m = createMessageHeader(node, beMessageType.BE_MSG_TYPE_TEMPERATURE)

    dataObject = {'temp': str(round(temperature, 3)), 'time': timestamp}
    data = json.dumps(dataObject)

    # Next byte in the protocol is length of data payload
    dataLength = len(data)
    m += bytes([dataLength, ])

    if dataLength + len(m) > BE_MESSAGE_MAX_LEN:
        raise Exception('beTemperatureMessageTooBig')

    # Payload data
    m += data.encode('utf-8')

    return m


def createBubbleMessage(node: int, timestamp: float) -> bytearray:
    m = createMessageHeader(node, beMessageType.BE_MSG_TYPE_BUBBLE)

    dataObject = {'time': timestamp}
    data = json.dumps(dataObject)

    # Next byte in the protocol is length of data payload
    dataLength = len(data)
    m += bytes([dataLength, ])

    if dataLength + len(m) > BE_MESSAGE_MAX_LEN:
        raise Exception('beTemperatureMessageTooBig')

    # Payload data
    m += data.encode('utf-8')

    return m


myNode = 8

temperature = float(34.23)
m = createTemperatureMessage(myNode, getCurrentTimestamp(), temperature)
print("Message:{0}".format(['0x' + str(i) for i in m]))
parseMessage(m)

m = createBubbleMessage(myNode, getCurrentTimestamp())
print("Message:{0}".format(['0x' + str(i) for i in m]))
parseMessage(m)




""" Experiment, pickling vs json string

    pickled object = 98 bytes
    json string = 42 bytes

    Conclusion:
        To keep messages under 60 bytes (zigbee packet),
        use json strings with short identifiers.


def pickleData(d):
    p = pickle.dumps(d)

    print("Pickle:{0}".format(p))
    return p


class beTemperatureMessage:
    temperature: float
    timestamp: float

    def __init__(self, temperature, timestamp):
        self.temperature = temperature
        self.timestamp = timestamp


message = beTemperatureMessage(32.34, currentTime)
pMessage = pickleData(message)

print("Length of picked object:{0}".format(len(pMessage)))
print(pickleData(pMessage))

jsonMessage = {'temp': 32.34, 'time': currentTime}
jsonMessageString = json.dumps(jsonMessage)
jsonByteArray = bytearray(jsonMessageString, 'utf-8')
print("Jsoned:{0}".format(jsonByteArray))
print("Len:{0}".format(len(jsonByteArray)))
"""
