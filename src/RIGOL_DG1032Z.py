"""
    Actually a RIGOL device interface.

    DG1032Z function generator

    SCPI command list: https://www.eevblog.com/forum/testgear/lists-of-rigol-scpi-commands/?action=dlattach;attach=754239;PHPSESSID=bbfstmnudumtidspc007tbfgqu

    Programming guide:

    https://people.ece.ubc.ca/~edc/4340.fall2015/datasheets/DG1000Z%20Programming%20Guide.pdf

    This object does not provide exhaustive functionality. Please update as needed.
"""

from SiglentDevices import SiglentBase

class DG1032Z(SiglentBase):
    """Control RIGOL function generator

        Attributes:

    """

    def __init__(self, hostname='tucan-awg01.triumf.ca'):
        """Init.

        Args:
            hostname (str): address of device (DNS or IP)
        """
        super().__init__(hostname=hostname)

    def _set_wave(self, wave, ch, freq, amp, offset, phase):
        """Set AWG to produce a given wave type with certain parameters

        Args:
            wave (str): wave shape, SIN|SQU|TRI
            ch (int): channel number, 1|2
            freq (float): frequency in Hz. 1 uHz to 60 MHz
            amp (float): Vpp in volts
            offset (float): DC offset in volts
            phase (float): phase in degrees. 0 to 360 deg
        """
        self.write(f"SOURce{ch}:APPLy:{wave} {freq},{amp},{offset},{phase}")

    def get_ch_state(self, ch=1):
        """Get channel on/off state

        Args:
            ch (int): channel number, 1|2

        Returns:
            bool: True if channel is on
        """
        val = self.query(f'OUTPut{ch}:STATe?')

        return val == 'ON'

    def get_wave(self, ch=1):
        """Read out waveform being applied currently by AWG

        Args:
            ch (int): channel number, 1|2

        Returns:
            dict of results:
                wave (str): wave shape, SIN|SQU|TRI
                freq (float): frequency in Hz. 1 uHz to 60 MHz
                amp (float): Vpp in volts
                offset (float): DC offset in volts
                phase (float): phase in degrees. 0 to 360 deg
        """

        # get output
        val = self.query(f'SOURce{ch}:APPLy?')
        val = val.replace('"', '').split(',')

        # convert to float where possible
        for i in range(len(val)):
            try:
                val[i] = float(val[i])
            except ValueError:
                pass

        # format output
        if val[0] == 'DC':
            out = {'wave': val[0],
                   'offset': val[3]
                }

        elif val[0] in ('SIN', 'TRI', 'SQU'):
            out = {'wave': val[0],
                'freq': val[1],
                'amp': val[2],
                'offset': val[3],
                'phase': val[4],
                }
        elif val[0] in ('RAMP', 'PULSE', 'NOISE', 'USER'):
            raise RuntimeError(f'Wave type {val[0]} not yet implemented')

        return out

    def set_ch_state(self, ch=1, state=False):
        """Turn channel on/off

        Args:
            ch (int): channel number, 1|2
            state (bool): if true, turn on channel output
        """
        if state:   self.write(f'OUTPut{ch}:STATe ON')
        else:       self.write(f'OUTPut{ch}:STATe OFF')

    def set_wave_sin(self, ch=1, freq=1000, amp=5, offset=0, phase=0):
        """Set AWG to produce a sine wave

        Args:
            ch (int): channel number, 1|2
            freq (float): frequency in Hz. 1 uHz to 60 MHz
            amp (float): Vpp in volts
            offset (float): DC offset in volts
            phase (float): phase in degrees. 0 to 360 deg
        """
        self._set_wave('SIN', ch, freq, amp, offset, phase)

    def set_wave_square(self, ch=1, freq=1000, amp=5, offset=0, phase=0):
        """Set AWG to produce a square wave

        Args:
            ch (int): channel number, 1|2
            freq (float): frequency in Hz. 1 uHz to 60 MHz
            amp (float): Vpp in volts
            offset (float): DC offset in volts
            phase (float): phase in degrees. 0 to 360 deg
        """
        self._set_wave('SQU', ch, freq, amp, offset, phase)

    def set_wave_triangle(self, ch=1, freq=1000, amp=5, offset=0, phase=0):
        """Set AWG to produce a triangle wave

        Args:
            ch (int): channel number, 1|2
            freq (float): frequency in Hz. 1 uHz to 60 MHz
            amp (float): Vpp in volts
            offset (float): DC offset in volts
            phase (float): phase in degrees. 0 to 360 deg
        """
        self._set_wave('TRI', ch, freq, amp, offset, phase)