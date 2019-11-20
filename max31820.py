#!/usr/bin/env  python3
"""
    Read a max32820/DS18B20 1-wire temperature sensor

    *NOTE* - max3820 datasheet and  "+" on device are wrong!
      (gets really hot if hooked up backwards)


                    _FRONT_
                   |       |
                   |31820  |
                   |       |
This is not + -->  |+      |
                   ---------
                  /    |    \
                 |     |     |
                 |     |     |
                 |     |     |
                 |     |     |
                
                (GND) (DQ)  (Vdd)
                  -    out    +

           This is the correct pinout

    (*) Use a 4.7k - 10k pullup
    (*) sudo raspi-config -> 5 Interfacing Options -> P7 1-Wire -> Yes
    (*) Rasperry Pi 3b+ - Pin7, GPIO4


"""

""" Driver/code taken verbatim from:
#    https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing

    modified by burin (c) 2019
        - table of devices
        - exception handling on open errors
"""


import glob
import time

base_dir = '/sys/bus/w1/devices/'
# burin
#device_folder = glob.glob(base_dir + '28*')[0]
device_1 = base_dir + '28-00000a6722b8'
device_2 = base_dir + '28-00000a673da2'

device_file_1 = device_1 + '/w1_slave'
device_file_2 = device_2 + '/w1_slave'

device_table = {'inside': device_file_1, 'outside': device_file_2}

ERROR = True
OK = False


def read_temp_raw(device_file):
    try:
        f = open(device_file, 'r')
        lines = f.readlines()
    except FileNotFoundError:
        return [ERROR, None]
    else:
        f.close()
        return [OK, lines]


def read_temp(device):
    [error, lines] = read_temp_raw(device_table[device])
    if error:
        return [ERROR, None, None]

    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)  # TODO - this is blocking
        [error, lines] = read_temp_raw(device_table[device])
        # TODO handle error
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return [OK, temp_c, temp_f]


def getTempC(device):
    error, c, f = read_temp(device)
    return [error, c]


""" test
while True:
    print("Inside:{0}".format(read_temp('inside')))
    print("Outside:{0}".format(read_temp('outside')))
    time.sleep(1)
"""
