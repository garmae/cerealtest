# Copyright (C) 2021 Guillermo Eduardo Garcia Maynez Rocha.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.
import datetime
import getopt
import json
import re
import sys
import time

import serial

test_collection = []


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SerialPort(metaclass=SingletonMeta):
    __serial_handle = serial.Serial()

    @staticmethod
    def setup(config):
        SerialPort.__serial_handle.baudrate = int(config['baudRate'])
        SerialPort.__serial_handle.port = config['port']
        SerialPort.__serial_handle.timeout = config['timeout']
        SerialPort.__serial_handle.bytesize = config['dataBits']
        SerialPort.__serial_handle.parity = config['parity'][:1]
        SerialPort.__serial_handle.stopbits = config['stopBits']
        SerialPort.__serial_handle.xonxoff = config['xonxoff']
        SerialPort.__serial_handle.rtscts = config['rtscts']
        SerialPort.__serial_handle.dsrdtr = config['dsrdtr']
        SerialPort.__serial_handle.write_timeout = config['writeTimeout']

    @staticmethod
    def open():
        SerialPort.__serial_handle.open()

    @staticmethod
    def close():
        SerialPort.__serial_handle.close()

    @staticmethod
    def write(data):
        SerialPort.__serial_handle.write(data)

    @staticmethod
    def read(size):
        return SerialPort.__serial_handle.read(size)


class Test(object):
    """Individual Test definition"""

    def __init__(self, test_dict):
        self.name = None
        self.is_hex = None
        self.message = None
        self.expected_regex = None
        self.delay = None
        self.script = None
        for key in test_dict:
            setattr(self, re.sub(
                r'(?<!^)(?=[A-Z])', '_', key).lower(), test_dict[key])

    def validate_attribs(self):
        if self.is_hex:
            if not is_hex_string(self.message):
                raise Exception("Message is not HEX and it is marked as such")

    def print_details(self):
        radix = ' (HEX)' if self.is_hex else ''
        print(f'Message: {self.message}{radix}')
        print(f'Expected Regex: {self.expected_regex}')
        print(f'Delay: {self.delay}')
        print(f'Script: {self.script}')

    def run(self):
        self.validate_attribs()
        print(f'{datetime.datetime.now().strftime("%Y/%m/%d %I:%M:%S %p")} - Running test \"{self.name}\"...')
        self.print_details()

        try:
            SerialPort.open()
        except serial.SerialException as err:
            print('Serial error: ' + str(err))
            sys.exit(1)

        data = bytearray.fromhex(self.message) if self.is_hex else str.encode(self.message)
        SerialPort.write(data)
        time.sleep(self.delay)
        response = SerialPort.read(1024)

        if self.is_hex:
            response = response.hex().upper()
        else:
            response = response.decode('ascii')
        print(f'\nResponse: {response}')

        SerialPort.close()
        print('\n')


def is_hex_string(string):
    return True if re.fullmatch("[0-9A-Fa-f]{2,}", string) else False


def load_config_file(path):
    with open(path, "r") as config_file:
        try:
            config_data = json.load(config_file)
        except ValueError as err:
            print('Invalid JSON file: ' + str(err))
            sys.exit(1)

        SerialPort.setup(config_data['serialConfig'])

        for test_spec in config_data['tests']:
            test_collection.append(Test(test_spec))


def parse_args(argv):
    input_path = ''

    # TODO: Add test result writer
    output_path = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('cerealtest.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: cerealtest.py -i <inputfile> -o <outputfile>')
            sys.exit(0)
        elif opt in ("-i", "--ifile"):
            input_path = arg
        elif opt in ("-o", "--ofile"):
            output_path = arg

    if not input_path:
        print(
            'No input file specified. Usage: cerealtest.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    else:
        load_config_file(input_path)


if __name__ == '__main__':
    print('CerealTest v0.2')
    print('Copyright (c) Guillermo Eduardo Garcia Maynez Rocha.\n')
    parse_args(sys.argv[1:])

    for test in test_collection:
        test.run()
