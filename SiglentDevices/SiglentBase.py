"""
    Base class for SCPI connection with Siglent Devices

    Derek Fuijmoto
    April 2023
"""

import pyvisa

class SiglentBase(object):
    """Control siglent digital device and send messages

        Attributes:

            ADDRESS (str): format to connect to device
    """

    # global variables

    ADDRESS = 'TCPIP::{host}::INSTR'

    def __init__(self, hostname):
        """ Init.

        Args:
            hostname (str): ip address or DNC lookup of device
        """

        # connect to device
        rm = pyvisa.ResourceManager()
        self.sds = rm.open_resource(self.ADDRESS.format(host=hostname))

        # setup connection
        self.sds.read_termination = '\n'
        self.sds.write_termination = '\n'

    # useful read and write passing to pyvisa.resources.TCPIPInstrument class
    def close(self):
        """Close remote connection."""
        self.sds.close()

    def flush(self):
        """Flush connection buffer."""
        self.sds.flush()

    def read(self, *args, **kwargs):
        """Read from stream."""
        return self.sds.read(*args, **kwargs)

    def read_raw(self, *args, **kwargs):
        """Read raw data from stream.

        Arguments passed to pyvisa.TCPIPInstrument.read_raw
        """
        return self.sds.read_raw(*args, **kwargs)

    def read_bytes(self, *args, **kwargs):
        """Read raw bytes from stream.

        Arguments passed to pyvisa.TCPIPInstrument.read_bytes
        """
        return self.sds.read_bytes(*args, **kwargs)

    def query(self, *args, **kwargs):
        """Push query to device, read back response.

        Arguments passed to pyvisa.TCPIPInstrument.query
        """
        return self.sds.query(*args, **kwargs)

    def write(self, *args, **kwargs):
        """Write string to device.

        Arguments passed to pyvisa.TCPIPInstrument.write
        """
        return self.sds.write(*args, **kwargs)

    def write_raw(self, *args, **kwargs):
        """Write raw bytestring to device.

        Arguments passed to pyvisa.TCPIPInstrument.write_raw
        """
        return self.sds.write_raw(*args, **kwargs)