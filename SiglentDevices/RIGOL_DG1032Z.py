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

    # Max number of points to send to device in a single batch
    ARB_MAX_SEND = 5000

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

    def get_freq(self, ch=1):
        """Get channel frequency in Hz

        Args:
            ch (int): channel number, 1|2
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        return self.query(f'SOUR{ch}:FREQ?')

    def get_mod_am_state(self, ch=1):
        """Get output modification state

        Args:
            ch (int): channel number 1|2

        Returns:
            bool: True if modification active, else False
        """
        return self.query(f'SOUR{ch}:AM:STAT?') == 'ON'

    def get_offset(self, ch=1):
        """Get channel offset in volts

        Args:
            ch (int): channel number, 1|2
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        return self.query(f'SOUR{ch}:VOLT:OFFS?')

    def get_phase(self, ch=1):
        """Get channel phase

        Args:
            ch (int): channel number, 1|2
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        return self.query(f'SOUR{ch}:PHAS?')

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

    def get_vpp(self, ch=1):
        """Get channel peak-peak amplitude

        Args:
            ch (int): channel number, 1|2
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        return self.query(f'SOUR{ch}:VOLT?')

    def set_ch_state(self, ch=1, state=False):
        """Turn channel on/off

        Args:
            ch (int): channel number, 1|2
            state (bool): if true, turn on channel output
        """
        if state:   self.write(f'OUTPut{ch}:STATe ON')
        else:       self.write(f'OUTPut{ch}:STATe OFF')

    def set_freq(self, ch=1, freq=1):
        """Set channel frequency in Hz

        Args:
            ch (int): channel number, 1|2
            freq (float): frequency in Hz
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        self.write(f'SOUR{ch}:FREQ {freq}')

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

    def set_offset(self, ch=1, offset=1):
        """Set channel offset in volts

        Args:
            ch (int): channel number, 1|2
            offset (float): voltage in volts
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        self.write(f'SOUR{ch}:VOLT:OFFS {offset}')

    def set_phase(self, ch=1, phase=0):
        """Set channel phase

        Args:
            ch (int): channel number, 1|2
            phase (float): phase in degrees
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        return self.write(f'SOUR{ch}:PHAS {phase}')

    def set_vpp(self, ch=1, vpp=0):
        """Set channel peak-peak amplitude

        Args:
            ch (int): channel number, 1|2
            vpp (float): peak-peak voltage in volts
        """
        if ch not in (1, 2):
            raise RuntimeError('ch must be one of 1 or 2')

        self.write(f'SOUR{ch}:VOLT {vpp}')

    def set_wave(self, ch=1, waveform='', freq=1000, vpp=1, offset=0, phase=0):
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
            vpp (float): peak-peak voltage in volts
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
        self.write(f'SOUR{ch}:APPL:{mode} {freq},{vpp},{offset},{phase}')

    def set_wave_custom(self, ch, voltages, period):
        """Send a custom waveform to the AWG

        See this article for details:

        https://rigol.my.site.com/support/s/article/methods-for-programmatically-creating-arbitrary-waves1

        Args:
            ch (int): channel number, 1|2
            voltages (iterable): list of voltages to set
            period (float): duration of voltage sequence, assuming equally spaced points.
        """

        # data type
        voltages = np.array(voltages)

        # get length and point spacing
        npts = len(voltages)
        dt = npts/period

        # center and normalize voltages
        offset = np.mean(voltages)
        voltages -= offset
        maxv = max(voltages)
        minv = min(voltages)

        norm = max(abs(maxv), abs(minv))
        vpp = abs(maxv-minv)
        voltages = voltages / norm

        # set amp values to counteract normalization
        self.set_offset(ch, offset)
        self.set_vpp(ch, vpp)

        # make sure data is sent in small enough groups
        npartitions = int(np.ceil(npts / self.ARB_MAX_SEND))
        volts_send = np.array_split(voltages, npartitions)

        # send data in groups
        for i in range(npartitions):

            # get data to send
            volts = volts_send[i]
            npts = len(volts)

            # convert voltages to bytes
            volts = volts * 8191.5 + 8191.5
            volts = volts.astype('<H')
            volts = volts.tobytes()

            # make header line
            nchar = len(str(npts*2))
            if i+1 < npartitions:
                flag = 'CON'
            else:
                flag = 'END'

            header = f'SOUR{ch}:DATA:DAC16 VOLATILE,{flag},#{nchar}{npts*2}'

            # write voltages to out
            self.write_raw(bytes(header, 'ascii') + volts)

        # set arb in srate mode
        self.write(f'SOURCE{ch}:FUNCTION:ARB:MODE SRATE')

        # set readback rate
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

