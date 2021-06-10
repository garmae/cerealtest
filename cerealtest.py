# Copyright (C) 2021 Guillermo Eduardo Garcia Maynez Rocha.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time

import serial

test_collection = []
working_directory = ''
testing_type = ''


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
        SerialPort.__serial_handle.PARITIES = config['writeTimeout']

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
            setattr(self, re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower(), test_dict[key])

    def validate_attribs(self):
        if self.is_hex:
            if not is_hex_string(self.message):
                raise Exception("Message is not HEX and it is marked as such")

    def __print_details(self):
        radix = ' (HEX)' if self.is_hex else ''
        print(f'Message sent:\n{self.message}{radix}')
        print(f'Expected Regex: {self.expected_regex}')
        print(f'Delay: {self.delay}')
        print(f'Script: {self.script}')

    def run(self):
        self.validate_attribs()
        print(f'{datetime.datetime.now().strftime("%Y/%m/%d %I:%M:%S %p")} - Running test \"{self.name}\"...')
        self.__print_details()

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
            response = response.hex().upper() + ' (HEX)'
        else:
            response = response.decode('ascii')
        print(f'\nResponse:\n{response}')

        if self.script is not None:
            subprocess.call(f'python {os.getcwd()}{working_directory}{self.script} {response}', shell=True)

        SerialPort.close()
        print('\n')


def is_hex_string(string):
    return True if re.fullmatch("[0-9A-Fa-f]{2,}", string) else False


def show_test_menu():
    test_num = 1
    print("Test Selection")
    for element in test_collection:
        print(f'{test_num}. {element.name}')
        test_num += 1
    selected_test = input('Select test to run: ')
    test_collection[int(selected_test) - 1].run()

    show_test_menu()


def load_config_file(path):
    with open(path, "r") as config_file:
        try:
            config_data = json.load(config_file)
        except ValueError as err:
            print('Invalid JSON file: ' + str(err))
            sys.exit(1)

        global working_directory
        global testing_type
        working_directory = config_data['workingDirectory']
        testing_type = config_data['testingType']

        SerialPort.setup(config_data['serialConfig'])

        for test_spec in config_data['tests']:
            test_collection.append(Test(test_spec))


def parse_args():
    input_path = ''

    # TODO: Add test result writer
    output_path = ''

    arg_parser = argparse.ArgumentParser(description='Serial Test Automation')
    arg_parser.add_argument('-i', '--input', help='Input File', required=True)
    args = vars(arg_parser.parse_args())

    input_path = args['input']

    load_config_file(input_path)


if __name__ == '__main__':
    print('CerealTest v0.2')
    print('Copyright (c) Guillermo Eduardo Garcia Maynez Rocha.\n')
    parse_args()

    if testing_type == 'continuous':
        for test in test_collection:
            test.run()
    else:
        show_test_menu()
