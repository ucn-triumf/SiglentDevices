"""
    Communication with the SPD3303X Programmable DC Power Supply from Siglent over ethernet
    Derek Fujimoto
    April 2023

    See manual for SCPI command list and other examples:
        https://siglentna.com/wp-content/uploads/dlm_uploads/2022/11/SPD3303X_QuickStart_E02A.pdf
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import struct, math
from SiglentDevices import SiglentBase

class SPD3303(SiglentBase):
    """Control siglent programmable power supply

        Attributes:

    """

    def __init__(self, hostname='tucan-dcps1.triumf.ca'):
        """Init.

        Args:
            hostname (str): address of device (DNS or IP)
        """
        super().__init__(hostname=hostname)

    def get_ch(self):
        """Get channel which will be operated

        Returns:
            int: channel number
        """
        ch = self.query(f'INSTrument?').strip()
        return (int(ch[-1]))

    def get_current(self, ch=None):
        """Query current value for specified channel, if there is no specified channel,
        query the current channel.

        Args:
            ch (int): channel number. If None, query current channel (id with get_ch())

        Returns:
            float: current in Amps
        """

        if ch is None:
            val = self.query('MEASure: CURRent?')
        else:
            val = self.query(f'MEASure: CURRent? CH{int(ch)}')

        return float(val.strip())

    def get_id(self):
        """Get ID of device

        Returns:
            str: manufacturer, product type, series No., software version and hardware version
        """
        return self.query('*IDN?').strip()

    def get_power(self, ch=None):
        """Query power value for specified channel, if there is no specified channel,
        query the current channel.

        Args:
            ch (int): channel number. If None, query current channel (id with get_ch())

        Returns:
            float: Power in VA
        """

        if ch is None:
            val = self.query('MEASure: POWEr?')
        else:
            val = self.query(f'MEASure: POWEr? CH{int(ch)}')

        return float(val.strip())

    def get_timer_par(self, ch, group=None):
        """Get timing parameters of specified channel

            Either ch or group should be int, both should not be none

        Args:
            ch (int): channel number, if None don't get channel
            group (int): 1|2|3|4|5, if None, don't get group

        Returns:
            dict: values keyed by units
        """

        # set group string
        if group is None:
            group = ''
        else:
            group = f'{int(group)}'

        # set channel string
        if ch is None:
            ch = ''
        else:
            ch = f'CH{int(ch)}'

        # write message
        val = self.query('TIMEr:SET? ' + ','.join((ch, group)))

        # format output
        return {key : float(val) for key, val in zip(('volt', 'amp', 'sec'), val.split(','))}

    def get_voltage(self, ch=None):
        """Query voltage value for specified channel, if there is no specified channel,
        query the current channel.

        Args:
            ch (int): channel number. If None, query current channel (id with get_ch())

        Returns:
            float: Voltage in Volts
        """

        if ch is None:
            val = self.query('MEASure: VOLTage?')
        else:
            val = self.query(f'MEASure: VOLTage? CH{int(ch)}')

        return float(val.strip())

    def set_ch(self, ch):
        """Set channel which will be operated

        Args:
            ch (int): channel number
        """
        self.write(f'INSTrument CH{int(ch)}')

    def set_ch_state(self, ch, on=True):
        """Turn on/off the selected channel

        Args:
            ch (int): channel number
            on (bool): if True turn channel on, if False turn channel off
        """
        val = 'ON' if on else 'OFF'
        self.write(f'OUTPut CH{int(ch)},{val}')

    def set_ch_mode(self, mode):
        """Set operation mode.

        Args:
            mode (str): independent|series|parallel
        """

        # clean input
        mode = mode.strip().lower()

        # mode to code
        if mode in 'independent':
            val = 0
        elif mode in 'series':
            val = 1
        elif mode in 'parallel':
            val = 2

        # write message
        self.write(f'OUTPut:TRACK {val}')

    def set_ch_disp(self, ch, on=True):
        """Turn on/off the waveform display for each channel

        Args:
            ch (int): channel number
            on (bool): if True turn channel display on, if False turn channel display off
        """
        val = 'ON' if on else 'OFF'
        self.write(f'OUTPut:WAVE CH{int(ch)},{val}')

    def set_current(self, ch, value):
        """Set current value of selected channel

        Args:
            ch (int): channel number
            value (float): current in amps
        """
        self.write(f'CH{int(ch)}:CURRent {float(value)}')

    def set_timer(self, ch, on=True):
        """Set timer function of channel on/off.

        Args:
            ch (int): channel number
            on (bool): if True, turn timer on, if False turn timer off
        """
        val = 'ON' if on else 'OFF'
        self.write(f'TIMEr CH{int(ch)},{val}')

    def set_timer_par(self, ch, volt, amp, sec, group=None):
        """Set timing parameters of specified channel

            Either ch or group should be int, both should not be none

        Args:
            ch (int): channel number, if None don't set channel
            volt (float): voltage in volts
            amp (float): current in amps
            sec (float): time in seconds
            group (int): 1|2|3|4|5, if None, don't set group
        """

        # set group string
        if group is None:
            group = ''
        else:
            group = f'{int(group)},'

        # set channel string
        if ch is None:
            ch = ''
        else:
            ch = f'CH{int(ch)},'

        # write message
        self.write(f'TIMEr:SET {ch}{group}{volt},{amp},{sec}')

    def set_voltage(self, ch, value):
        """Set voltage value of selected channel

        Args:
            ch (int): channel number
            value (float): voltage in volts
        """
        self.write(f'CH{int(ch)}:VOLTage {float(value)}')
