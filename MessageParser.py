#!/usr/bin/env  python3
import message
from enum import Enum


class msgStageEnum(Enum):
    NODE_NUM = 0
    MSG_TYPE = 1
    MSG_LEN = 2
    MSG_PAYLOAD = 3


class msg_flags:
    synced = False
    stage: msgStageEnum = msgStageEnum.NODE_NUM
    payload_index: int = 0
    payload_length: int = 0
    payload_buffer: bytearray = bytearray()


class MessageStreamParser:

    def __init__(self):
        self.flags = msg_flags()

    def resetState(self):
        del self.flags
        self.flags = msg_flags()
        self.flags.payload_buffer.clear()
        # print("size of buffer is {0}".format(len(self.flags.payload_buffer)))

    def parseDataStream(self, b: bytes):
        if b == message.BE_MESSAGE_HEADER:
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
                # self.message.payload.extend(b)
                # Apparently you can't extend by 1 item?
                self.flags.payload_buffer.append(b)
                self.flags.payload_index += 1
                if self.flags.payload_index == self.flags.payload_length:
                    # print("Got message!")
                    message.parseMessage(self.flags.payload_buffer)
                    self.resetState()
