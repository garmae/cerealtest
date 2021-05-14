# Copyright (C) 2021 Guillermo Eduardo Garcia Maynez Rocha.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import serial
import json
import sys
import re
import getopt
import subprocess


def run_test(test):
    pass


def open_port(config):
    ser = serial.Serial(config['port'], config['baudRate'])
    print('Port opened: ' + ser.name)
    ser.write(b'Penis')
    ser.close()


def load_config_file(path):
    with open(path, "r") as config_file:
        try:
            config_data = json.load(config_file)
        except ValueError as err:
            print('Invalid JSON file: ' + str(err))
            sys.exit(1)
        open_port(config_data['serialConfig'])


def parse_args(argv):
    input_path = ''
    output_path = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('cerealtest.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: cerealtest.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_path = arg
        elif opt in ("-o", "--ofile"):
            output_path = arg

    if not input_path:
        print('No input file specified. Usage: cerealtest.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    else:
        load_config_file(input_path)


if __name__ == '__main__':
    print('CerealTest v0.1')
    parse_args(sys.argv[1:])
