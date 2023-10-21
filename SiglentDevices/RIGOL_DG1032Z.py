"""
    Actually a RIGOL device interface.

    DG1032Z function generator

    SCPI command list: https://www.eevblog.com/forum/testgear/lists-of-rigol-scpi-commands/?action=dlattach;attach=754239;PHPSESSID=bbfstmnudumtidspc007tbfgqu

    Programming guide:

    https://people.ece.ubc.ca/~edc/4340.fall2015/datasheets/DG1000Z%20Programming%20Guide.pdf

    This object does not provide exhaustive functionality. Please update as needed.
"""

from . import SiglentBase
import numpy as np

class DG1032Z(SiglentBase):
    """Control RIGOL function generator

        Attributes:
            block_until_finished (bool): if true, block set operations until finished

    """

    FUNCTIONS = ('SINusoid', 'SQUare', 'RAMP', 'PULSe', 'NOISe', 'USER',
                 'HARMonic', 'CUSTom', 'DC', 'KAISER', 'ROUNDPM', 'SINC',
                 'NEGRAMP', 'ATTALT', 'AMPALT', 'STAIRDN', 'STAIRUP',
                 'STAIRUD', 'CPULSE', 'PPULSE', 'NPULSE', 'TRAPEZIA',
                 'ROUNDHALF', 'ABSSINE', 'ABSSINEHALF', 'SINETRA', 'SINEVER',
                 'EXPRISE', 'EXPFALL', 'TAN', 'COT', 'SQRT', 'X2DATA', 'GAUSS',
                 'HAVERSINE', 'LORENTZ', 'DIRICHLET', 'GAUSSPULSE', 'AIRY',
                 'CARDIAC', 'QUAKE', 'GAMMA', 'VOICE', 'TV', 'COMBIN',
                 'BANDLIMITED', 'STEPRESP', 'BUTTERWORTH', 'CHEBYSHEV1',
                 'CHEBYSHEV2', 'BOXCAR', 'BARLETT', 'TRIANG', 'BLACKMAN',
                 'HAMMING', 'HANNING', 'DUALTONE', 'ACOS', 'ACOSH', 'ACOTCON',
                 'ACOTPRO', 'ACOTHCON', 'ACOTHPRO', 'ACSCCON', 'ACSCPRO',
                 'ACSCHCON', 'ACSCHPRO', 'ASECCON', 'ASECPRO', 'ASECH', 'ASIN',
                 'ASINH', 'ATAN', 'ATANH', 'BESSELJ', 'BESSELY', 'CAUCHY',
                 'COSH', 'COSINT', 'COTHCON', 'COTHPRO', 'CSCCON', 'CSCPRO',
                 'CSCHCON', 'CSCHPRO', 'CUBIC', 'ERF', 'ERFC', 'ERFCINV',
                 'ERFINV', 'LAGUERRE', 'LAPLACE', 'LEGEND', 'LOG', 'LOGNORMAL',
                 'MAXWELL', 'RAYLEIGH', 'RECIPCON', 'RECIPPRO', 'SECCON',
                 'SECPRO', 'SECH', 'SINH', 'SININT', 'TANH', 'VERSIERA',
                 'WEIBULL', 'BARTHANN', 'BLACKMANH', 'BOHMANWIN', 'CHEBWIN',
                 'FLATTOPWIN', 'NUTTALLWIN', 'PARZENWIN', 'TAYLORWIN',
                 'TUKEYWIN', 'CWPUSLE', 'LFPULSE', 'LFMPULSE', 'EOG', 'EEG',
                 'EMG', 'PULSILOGRAM', 'TENS1', 'TENS2', 'TENS3', 'SURGE',
                 'DAMPEDOSC', 'SWINGOSC', 'RADAR', 'THREEAM', 'THREEFM',
                 'THREEPM', 'THREEPWM', 'THREEPFM', 'RESSPEED', 'MCNOSIE',
                 'PAHCUR', 'RIPPLE', 'ISO76372TP1', 'ISO76372TP2A',
                 'ISO76372TP2B', 'ISO76372TP3A', 'ISO76372TP3B', 'ISO76372TP4',
                 'ISO76372TP5A', 'ISO76372TP5B', 'ISO167502SP', 'ISO167502VR',
                 'SRC', 'IGNITION', 'NIMHDISCHARGE', 'GATEVIBR',
                 'SIN', 'SQU', 'RAMP', 'PULS', 'NOIS', 'HARM', 'CUST', )

    def __init__(self, hostname='tucan-awg01.triumf.ca'):
        """Init.

        Args:
            hostname (str): address of device (DNS or IP)
        """
        super().__init__(hostname=hostname)

        # setup block set values
        self.block_until_finished = True

    def get_ch_state(self, ch=1):
        """Get channel on/off state

        Args:
            ch (int): channel number, 1|2

        Returns:
            bool: True if channel is on
        """
        val = self.query(f'OUTPut{ch}:STATe?')

        return val == 'ON'

    def get_mod_am_state(self, ch=1):
        """Get output modification state

        Args:
            ch (int): channel number 1|2

        Returns:
            bool: True if modification active, else False
        """
        return self.query(f'SOUR{ch}:AM:STAT?') == 'ON'

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

    def set_amp(self, ch=1, amp=0):
        """Set channel amplitude

        Args:
            ch (int): channel number, 1|2
            amp (float): Vpp in volts
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        self.write(f'SOUR{ch}:VOLT {amp}')

    def set_freq(self, ch=1, freq=1):
        """Set channel frequency in Hz

        Args:
            ch (int): channel number, 1|2
            freq (float): frequency in Hz
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        self.write(f'SOUR{ch}:FREQ {freq}')

    def set_offset(self, ch=1, offset=1):
        """Set channel offset in volts

        Args:
            ch (int): channel number, 1|2
            offset (float): voltage in volts
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        self.write(f'SOUR{ch}:VOLT:OFFS {offset}')

    def set_state(self, ch=1, state=False):
        """Turn channel on/off

        Args:
            ch (int): channel number, 1|2
            state (bool): if true, turn on channel output
        """
        if state:   self.write(f'OUTPut{ch}:STATe ON')
        else:       self.write(f'OUTPut{ch}:STATe OFF')

    def set_mod_am(self, ch=1, waveform='SIN', depth=100, freq=1):
        """Set waveform modification for internal modulation

        Args:
            ch (int): channel number 1|2
            waveform (str): SINusoid|SQUare|TRIangle|RAMP|NRAMp|NOISe|USER
            depth (int): percentage of amplitude variation [0, 120]
            freq (float): frequency in Hz
        """
        # specify internal modulation
        self.write(f'SOUR{ch}:AM:SOUR INT')

        # set waveform
        self.write(f'SOUR{ch}:AM:INT:FUNC {waveform}')

        # set depth
        self.write(f'SOUR{ch}:AM {depth}')

        # set frequency
        self.write(f'SOUR{ch}:AM:INT:FREQ {freq}')

    def set_mod_am_state(self, ch=1, state=False):
        """Get output modification state

        Args:
            ch (int): channel number 1|2
            state (bool): if True, turn mod on

        Returns:
            None
        """
        if state:
            self.write(f'SOUR{ch}:AM:STAT ON')
        else:
            self.write(f'SOUR{ch}:AM:STAT OFF')

    def set_wave(self, ch=1, waveform='', freq=1000, amp=1, offset=0, phase=0):
        """Setup arbitrary waveforms

        Args:
            ch (int): channel number, 1|2
            waveform (str): one of SINusoid|SQUare|RAMP|PULSe|NOISe|USER|HARMonic|CUSTom|DC|KAISER|
                                ROUNDPM|SINC|NEGRAMP|ATTALT|AMPALT|STAIRDN|STAIRUP|STAIRUD|CPULSE|
                                PPULSE|NPULSE|TRAPEZIA|ROUNDHALF|ABSSINE|ABSSINEHALF|SINETRA|
                                SINEVER|EXPRISE|EXPFALL|TAN|COT|SQRT|X2DATA|GAUSS|HAVERSINE|LORENTZ
                                |DIRICHLET|GAUSSPULSE|AIRY|CARDIAC|QUAKE|GAMMA|VOICE|TV|COMBIN|
                                BANDLIMITED|STEPRESP|BUTTERWORTH|CHEBYSHEV1|CHEBYSHEV2|BOXCAR|
                                BARLETT|TRIANG|BLACKMAN|HAMMING|HANNING|DUALTONE|ACOS|ACOSH|
                                ACOTCON|ACOTPRO|ACOTHCON|ACOTHPRO|ACSCCON|ACSCPRO|ACSCHCON|
                                ACSCHPRO|ASECCON|ASECPRO|ASECH|ASIN|ASINH|ATAN|ATANH|BESSELJ|
                                BESSELY|CAUCHY|COSH|COSINT|COTHCON|COTHPRO|CSCCON|CSCPRO|
                                CSCHCON|CSCHPRO|CUBIC|ERF|ERFC|ERFCINV|ERFINV|LAGUERRE|LAPLACE|
                                LEGEND|LOG|LOGNORMAL|MAXWELL|RAYLEIGH|RECIPCON|RECIPPRO|SECCON|
                                SECPRO|SECH|SINH|SININT|TANH|VERSIERA|WEIBULL|BARTHANN|BLACKMANH|
                                BOHMANWIN|CHEBWIN|FLATTOPWIN|NUTTALLWIN|PARZENWIN|TAYLORWIN|
                                TUKEYWIN|CWPUSLE|LFPULSE|LFMPULSE|EOG|EEG|EMG|PULSILOGRAM|TENS1|
                                TENS2|TENS3|SURGE|DAMPEDOSC|SWINGOSC|RADAR|THREEAM|THREEFM|
                                THREEPM|THREEPWM|THREEPFM|RESSPEED|MCNOSIE|PAHCUR|RIPPLE|
                                ISO76372TP1|ISO76372TP2A|ISO76372TP2B|ISO76372TP3A|ISO76372TP3B|
                                ISO76372TP4|ISO76372TP5A|ISO76372TP5B|ISO167502SP|ISO167502VR|SRC|
                                IGNITION|NIMHDISCHARGE|GATEVIBR
            freq (float): frequency in Hz. 1 uHz to 60 MHz
            amp (float): Vpp in volts
            offset (float): DC offset in volts
            phase (float): phase in degrees. 0 to 360 deg
        """

        # check input
        if waveform not in self.FUNCTIONS:
            raise RuntimeError(f'waveform "{waveform}" not one of {self.FUNCTIONS}')

        # set parameters
        if waveform not in ('SINusoid', 'SQUare', 'RAMP', 'PULSe', 'NOISe', 'SIN', 'SQU', 'RAMP', 'PULS', 'NOIS'):

            # if arb
            mode = 'USER'

            # freq mode easiest to work with
            self.write(f"SOUR{ch}:FUNC:ARB:MODE FREQ")

            # set waveform
            self.write(f'SOUR{ch}:FUNC {waveform}')

        else:
            mode = waveform

        # set waveform
        self.write(f'SOUR{ch}:APPL:{mode} {freq},{amp},{offset},{phase}')

    def set_wave_custom(self, ch, voltages, period):
        """Send a custom waveform to the AWG

        Args:
            ch (int): channel number, 1|2
            voltages (iterable): list of voltages to set
            period (float): duration of voltage sequence, assuming equally spaced points.
        """

        # data type
        voltages = np.array(voltages)

        # normalize voltages
        maxv = max(voltages)
        minv = min(voltages)

        npts = len(voltages)
        amp = maxv - minv
        offset = (maxv+minv)/2

        voltages = (voltages - offset) / amp

        # set amp values
        self.set_offset(ch, offset*2)
        self.set_amp(ch, amp*4)

        # convert voltages to bytes
        voltages = voltages * 8191.5 + 8191.5
        voltages = voltages.astype('<H')
        voltages = voltages.tobytes()

        # make header line
        nchar = len(str(npts*2))
        header = f'SOUR{ch}:DATA:DAC16 VOLATILE,END,#{nchar}{npts*2}'

        # write voltages to out
        self.write_raw(bytes(header, 'ascii') + voltages)

        # set arb in srate mode
        self.write(f'SOURCE{ch}:FUNCTION:ARB:MODE SRATE')

        # set readback rate
        dt = npts/period
        self.write(f'SOURCE{ch}:FUNCTION:ARB:SRATE {dt:E}')

    def wait(self):
        """Wait until operation has completed. Block operation until completed"""
        self.query('*OPC?')

    def write(self, *args, block=None, **kwargs):
        """Write string to device.

        Args:
            block (bool, None): if true, block output until write is finished.
                if None, use self.block_until_finshed as default condition

            remaining arguments passed to SiglentBase.write
        """
        super().write(*args, **kwargs)

        if block is None:
            block = self.block_until_finished

        if block:
            self.wait()

