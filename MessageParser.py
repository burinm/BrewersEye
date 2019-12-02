#!/usr/bin/env  python3
""" MessageParser.py - State machine to parse Brewers' Eye Messages from a stream
    burin (c) 2019
"""
import MessageProtocol as beMessage
from typing import Callable
from enum import Enum


class msgStageEnum(Enum):
    NODE_NUM = 0
    MSG_TYPE = 1
    MSG_LEN = 2
    MSG_PAYLOAD = 3


# State machine current state
class msg_flags:
    # State machine reset state
    synced = False
    stage: msgStageEnum = msgStageEnum.NODE_NUM
    payload_index: int = 0
    payload_length: int = 0
    # For some reason, this doesn't clear the bytearray, grrr
    payload_buffer: bytearray = bytearray()


class MessageStreamParser:

    def __init__(self, callback: Callable[[object], None]):
        self.flags = msg_flags()
        self.messageComplete = callback

    # Start over: either reset, finished or error
    def resetState(self):
        del self.flags
        self.flags = msg_flags()
        self.flags.payload_buffer.clear()  # *really* clear
        # print("size of buffer is {0}".format(len(self.flags.payload_buffer)))

    # Call over and over again, one byte at a time
    def parseDataStream(self, b: bytes):
        # The '@' token always marks start of message, and resets
        if b == beMessage.BE_MESSAGE_HEADER:
            # print("Got Sync character")
            self.resetState()
            self.flags.synced = True
            self.flags.payload_buffer.append(b)
            return

        if self.flags.synced:
            if self.flags.stage is msgStageEnum.NODE_NUM:
                # print("Got Node Number:{0}".format(b))
                self.flags.payload_buffer.append(b)
                self.flags.stage = msgStageEnum.MSG_TYPE
                return
            elif self.flags.stage is msgStageEnum.MSG_TYPE:
                # print("Got message type:{0}".format(b))
                self.flags.payload_buffer.append(b)
                self.flags.stage = msgStageEnum.MSG_LEN
                return
            elif self.flags.stage is msgStageEnum.MSG_LEN:
                # print("Got message length:{0}".format(b))
                self.flags.payload_buffer.append(b)
                self.flags.payload_length = b
                self.flags.stage = msgStageEnum.MSG_PAYLOAD
                return
            elif self.flags.stage is msgStageEnum.MSG_PAYLOAD:
                # print("Got payload byte #{0} [{1}]".format(self.flags.payload_index, b))
                self.flags.payload_buffer.append(b)
                self.flags.payload_index += 1
                if self.flags.payload_index == self.flags.payload_length:
                    # print("Got message!")
                    o = beMessage.parseMessage(self.flags.payload_buffer)
                    self.resetState()
                    if o is not None:
                        self.messageComplete(o)
