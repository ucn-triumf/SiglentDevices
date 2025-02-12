"""
    Base class for SCPI connection via USB connection

    Derek Fuijmoto
    April 2023
"""

import pyvisa
from . import SiglentBase

class Keithley_DMM6500(SiglentBase):
    """Control keithley DMM and send messages via USB connection
    """

    def __init__(self, hostname='USB0::0x05e6::0x6500::04550534::INSTR'):
        """
        Args:
            hostname (str): ip address or DNC lookup of device
        """

        # connect to device
        rm = pyvisa.ResourceManager()
        self.sds = rm.open_resource(hostname)

        # setup connection
        self.sds.read_termination = '\n'
        self.sds.write_termination = '\n'

    def get_volt_ac(self):
        """Get AC voltage readback, single value"""
        return float(self.query('MEAS:VOLT:AC?'))

    def get_volt_dc(self):
        """Get DC voltage readback, single value"""
        return float(self.query('MEAS:VOLT:DC?'))