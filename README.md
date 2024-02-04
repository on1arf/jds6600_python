# jds6600_python

Python class to remote-control a Junce-Instrument JDS6600 signal generator, using the USB-connection (serial-line emulation)

- version 0.0.1 (2018/01/19): initial release, reading basic parameters
- version 0.0.2 (2018/01/28): added "measure" menu + support functions, documtation
- version 0.0.3 (2018/02/07): added "counter" and "sweep" menu
- version 0.0.4 (2018/02/14): added "pulse" and "burst" menu + codecleanup
- version 0.0.5 (2018/02/16): added system menu
- version 0.1.0 (2018/02/17): added arbitrary waveform 


## API
For the API-calls, see api.txt

## CLI
The class can be used from the command-line by calling `jds6600-cli.py`. It is a simple command line wrapper around the class. It can be used to read and set parameters, and to read the counter. 

## Installation
The class is written in Python3 and uses the pyserial library. To install the class, use the following command:
```
pip install -r requirements.txt
```

## Examples
See examples/readjds.py


## License
MIT license. See "LICENSE" for more info


ENJOY!!!


TO DO:
- document serial protocol
- add docstrings


Kristoff (ON1ARF)
