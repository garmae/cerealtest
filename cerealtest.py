# Copyright (C) 2021 Guillermo Eduardo Garcia Maynez Rocha.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import binascii
import datetime
import json
import os
import re
import subprocess
import sys
import textwrap
import time

import serial

working_directory = ''
testing_type = ''
test_collection = []
ser = serial.Serial()


def print_hex_ascii_detail(hex_str: str):
    offset = 0
    hex_lines = textwrap.fill(hex_str, width=34).splitlines()
    print("Offset\t00 01 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F")
    print("----------------------------------------------------------")
    for line in hex_lines:
        ascii_line = binascii.unhexlify(line).decode(encoding='ascii', errors='replace')
        line = " ".join(line[i:i + 2] for i in range(0, len(line), 2))
        print("{0:06X}\t{1}\t{2}".format(offset, line.ljust(50), ascii_line))
        offset += 16


def is_hex_string(string: str):
    if re.fullmatch("[0-9A-Fa-f]{2,}", string):
        if len(string) % 2 == 0:
            return True
    return False


def setup_serial(config):
    ser.baudrate = int(config['baudRate'])
    ser.port = config['port']
    ser.timeout = config['timeout']
    ser.bytesize = config['dataBits']
    ser.parity = config['parity'][:1]
    ser.stopbits = config['stopBits']
    ser.xonxoff = config['xonxoff']
    ser.rtscts = config['rtscts']
    ser.dsrdtr = config['dsrdtr']
    ser.write_timeout = config['writeTimeout']

    try:
        ser.open()
        time.sleep(2)
    except serial.SerialException as err:
        print('Serial error: ' + str(err))
        sys.exit(1)


class HexBytesAdapter:

    def __init__(self, base_bytes: bytes):
        self.base_bytes = base_bytes

    def __getattr__(self, item):
        return getattr(self.base_bytes, item)

    def hex(self) -> str:
        print(self.base_bytes)
        return self.base_bytes.decode("ascii")


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
        print("Message to send{0}: {1}".format(radix, textwrap.fill(self.message, width=64)))
        print("Expected Regex: {0}".format(self.expected_regex))
        print("Delay: {0}".format(self.delay))
        print("Script: {0}".format(self.script))

    def run(self):
        self.validate_attribs()
        current_time = datetime.datetime.now().strftime("%Y/%m/%d %I:%M:%S %p")
        print(
            "{0} - Running test \"{1}\"...".format(current_time, self.name))
        self.__print_details()

        data = bytearray.fromhex(self.message) if self.is_hex else str.encode(self.message)
        ser.write(data)
        time.sleep(self.delay)
        response = ser.readline()
        response = HexBytesAdapter(response)

        if self.is_hex:
            response = textwrap.fill(response.hex().upper(), width=64) + ' (HEX)'
        else:
            response = response.decode('ascii')
        print("\nResponse:\n{0}".format(response))

        if self.script is not None:
            subprocess.call("python {0}/{1}/{2} {3}".format(os.getcwd(), working_directory, self.script, response),
                            shell=True)

        print('\n')


def show_test_menu():
    test_num = 1
    print("Test Menu")
    for element in test_collection:
        print("{0}. {1}".format(test_num, element.name))
        test_num += 1
    print("{0}. {1}".format(test_num, "Quit"))
    selected_test = input('Select test to run: ')

    if int(selected_test) == test_num:
        return

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

        setup_serial(config_data['serialConfig'])

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
    print('Copyright (c) 2021 Guillermo Eduardo Garcia Maynez Rocha.\n')
    parse_args()

    if testing_type == 'continuous':
        for test in test_collection:
            test.run()
    else:
        show_test_menu()

    ser.close()
