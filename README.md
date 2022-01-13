# CerealTest
This tool automates serial tests via a JSON configuration file where you specify port settings and the array of tests that will be run.

You can specify the message to send as text or as hexadecimal data,  expected answer via a regular expression, or you can set a Python script to compute the message to send as well as a reception script that can process the answer for maximum flexibility.


## Contributions
This repository is open to contributions, but it has a special requirement: Code must be compatible with Python 3.8, the last version compatible with Windows 7.

## License
The main source code is licensed under Mozilla Public License v2.0. Long story short, it is like a LGPL but at a file level; this means that if you want modifications to be kept private, you must do them on separate files from those marked with the MPL notice.
