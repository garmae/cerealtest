# Copyright (C) 2021-2022 Guillermo Eduardo Garcia Maynez Rocha.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import binascii
import textwrap


def print_hex_ascii_detail(hex_str: str):
    offset = 0
    hex_lines = textwrap.fill(hex_str, width=34).splitlines()
    print(f'Offset\t00 01 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F')
    print('----------------------------------------------------------')
    for line in hex_lines:
        ascii_line = binascii.unhexlify(line).decode(encoding='ascii', errors='replace')
        line = " ".join(line[i:i + 2] for i in range(0, len(line), 2))
        print(f'{offset:06X}\t{line.ljust(50)}\t{ascii_line}')
        offset += 16