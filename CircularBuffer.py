#!/usr/bin/env  python3
"""
  CircularBuffer.py - A tiny circular buffer
    burin (2019)

    An implementation of the circular buffer described
    in Making Embedded Systems, Elecia White, (C) 2012

    Ported from my C version (2016)
        https://github.com/burinm/drivers/blob/master/mylib/circbuf_tiny.h
        https://github.com/burinm/drivers/blob/master/mylib/circbuf_tiny.c
"""
import math


class CircularBuffer:
    max_size: int = int(math.pow(2, 11))  # 2048 bytes, must be a power of 2
    MAX_SIZE: int = max_size - 1

    # Current size of the circular bufffer
    def SIZE(c: 'CircularBuffer'):
        return ((c.write_ptr - c.read_ptr) & CircularBuffer.MAX_SIZE)

    def __init__(self):
        self.read_ptr = 0
        self.write_ptr = 0
        self.buffer: bytearray = bytearray(CircularBuffer.max_size)

    def has_items(self):
        return CircularBuffer.SIZE(self) > 0

    def put(self, b: bytes):
        if CircularBuffer.SIZE(self) < CircularBuffer.MAX_SIZE:
            self.buffer[self.write_ptr] = b
            self.write_ptr += 1
            self.write_ptr &= CircularBuffer.MAX_SIZE  # Wrap around
            return True
        else:
            return False

    def get(self):
        if CircularBuffer.SIZE(self) > 0:
            b = self.buffer[self.read_ptr]
            self.read_ptr += 1
            self.read_ptr &= CircularBuffer.MAX_SIZE  # Wrap around
            return [True, b]
