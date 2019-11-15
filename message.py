#!/usr/bin/env  python3
from enum import Enum
from datetime import datetime


TEMPERATURE_MSG = 1
BUBBLESTAMP_MSG = 2


def createTemperatureMessage(t: float):
    m = bytearray('@', 'utf-8')
    m += bytes(TEMPERATURE_MSG)

    temperatureString = str(round(t, 3))
    m += temperatureString.encode('utf-8')

    print("Message:{0}".format(m))
    return m
    

currentTime = datetime.now().timestamp()
createTemperatureMessage(currentTime)
      
    
