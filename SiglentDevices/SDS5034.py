"""
    Communication with the SDS5034X Digital Oscilloscope from Siglent over ethernet
    Derek Fujimoto
    March 2023

    See manual for SCPI command list and other examples:
        https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf
"""

from . import SiglentBase
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import struct, math, time
from tqdm import tqdm

class SDS5034(SiglentBase):
    """Control siglent digital oscilloscope and read waveforms

        Attributes:

            HORI_NUM (int): Number of horizontal divisions
            MEASURE_ADV_MODE1_MAX (int): Number of advanced measurements allowable for mode 1
            preambles (dict): preamble values, saved when measured
            sds (pyvisa resource): allows write/read/query to the device
            TDIV_ENUM (list): time division values from table 2 of https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf (page 559)
            waveforms (pd.DataFrame): waveform data in volts (includes all channels)
            MEASUREMENT_ITEMS (list): things which can be read as simple measurements from the scope
            block_until_finished (bool): if true, block set operations until finished
    """

    # global variables

    HORI_NUM = 10
    MEASURE_ADV_MODE1_MAX = 5

    # see table 2 from https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf
    # page 559

    TDIV_ENUM = (   200e-12,
                    500e-12,
                    1e-9,
                    2e-9,
                    5e-9,
                    10e-9,
                    20e-9,
                    50e-9,
                    100e-9,
                    200e-9,
                    500e-9,
                    1e-6,
                    2e-6,
                    5e-6,
                    10e-6,
                    20e-6,
                    50e-6,
                    100e-6,
                    200e-6,
                    500e-6,
                    1e-3,
                    2e-3,
                    5e-3,
                    10e-3,
                    20e-3,
                    50e-3,
                    100e-3,
                    200e-3,
                    500e-3,
                    1,
                    2,
                    5,
                    10,
                    20,
                    50,
                    100,
                    200,
                    500,
                    1000,
                )

    MEASUREMENT_ITEMS = ['PKPK','MAX','MIN','AMPL','TOP','BASE','LEVELX','CMEAN',
                                     'MEAN','STDEV','VSTD','RMS','CRMS','MEDIAN','CMEDIAN',
                                     'OVSN','FPRE','OVSP','RPRE','PER','FREQ','TMAX','TMIN',
                                     'PWID','NWID','DUTY','NDUTY','WID','NBWID','DELAY','TIMEL',
                                     'RISE','FALL','RISE20T80','FALL80T20','CCJ','PAREA','NAREA',
                                     'AREA','ABSAREA','CYCLES','REDGES','FEDGES','EDGES',
                                     'PPULSES','NPULSES','PACArea','NACArea','ACArea',
                                     'ABSACArea']

    def __init__(self, hostname='tucan-scope1.triumf.ca'):
        """ Init.

        Args:
            hostname (str): ip address or DNC lookup of device
        """

        # setup
        super().__init__(hostname=hostname)

        # set chunk size for communication
        self.sds.chunk_size = 20*1024*1024

        # set data storage
        self.preambles = {}
        self.waveforms = pd.DataFrame()

        # setup block set values
        self.block_until_finished = True

    def _check_measure_mode(self, target_mode):
        """Check that the measurement state is correct

        Args:
            target_mode (str): simple|advanced
        """

        # check measurment state
        if not self.get_measure_state():
            self.set_measure_state(True)
            time.sleep(0.5)

        # check mode
        if target_mode == 'advanced':
            if self.get_measure_mode(return_is_simple=True):
                self.set_measure_mode('advanced')
                time.sleep(0.5)
                print('Set measurement mode simple to advanced')
        else:
            if self.get_measure_mode(return_is_simple=True):
                self.set_measure_mode('simple')
                time.sleep(0.5)
                print('Set measurement mode advanced to simple')

    # simple basic commands
    def default(self):
        """Resets the oscilloscope to the default configuration, equivalent to the Default button on the front panel.
        """
        self.write('*RST')

    def reboot(self):
        """Restart the scope."""
        self.write('SYSTem:REBoot')

    def run(self):
        """Start taking data, equivalent to pressing the Run button on the front panel."""
        self.write('ACQuire:STATE RUN')

    def stop(self):
        """Stop taking data, equivalent to pressing the Stop button on the front panel."""
        self.write('ACQuire:STATE STOP')

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

    # simple queries
    def get_adc_resolution(self):
        """Returns:
            int: number of bits 8|10
        """
        return int(self.query('ACQuire:RESolution?').replace('Bits', ''))

    def get_ch_coupling(self, ch):
        """Args:
            ch (int): channel number

        Returns:
            str: DC|AC|GND
        """
        return self.query(f'CHANnel{int(ch)}:COUPling?')

    def get_ch_impedance(self, ch):
        """Args:
            ch (int): channel number

        Returns:
            str: 1M|50 (1 MOhm or 50 Ohms)
        """

        response = self.query(f'CHANnel{int(ch)}:IMP?').strip()

        if response == 'ONEMeg':
            return '1M'
        elif response == 'FIFTy':
            return '50'
        else:
            raise RuntimeError(f'Unexpected device response "{response}"')

    def get_ch_offset(self, ch):
        """Args:
                ch (int): channel number

            Returns:
                float: Offset in volts
        """
        return float(self.query(f'CHANnel{int(ch)}:OFFS?').strip())

    def get_ch_probe(self, ch):
        """Args:
                ch (int): channel number

            Returns:
                float: probe attenuation factor
        """
        return float(self.query(f'CHANnel{int(ch)}:PROBe?').strip())

    def get_ch_scale(self, ch):
        """
            Returns the current vertical sensitivity of the specified channel (volts/div).

            Args:
                ch (int): channel number

            Returns:
                float: vertical sensitivity in volts/div
        """
        return float(self.query(f'CHANnel{int(ch)}:SCALe?').strip())

    def get_ch_state(self, ch):
        """Args:
                ch (int): channel number

            Returns:
                bool: True if channel is on. False if channel is off
        """
        state = self.query(f'CHANnel{int(ch)}:SWITch?')

        return state.strip().upper() == 'ON'

    def get_ch_unit(self, ch):
        """Args:
                ch (int): channel number

            Returns:
                str: the unit of the channel V|A
        """
        return self.query(f'CHANnel{int(ch)}:UNIT?')

    def get_id(self):
        """Returns:
                str: id of device
        """
        return self.query('*IDN?')

    def get_measure_mode(self, return_is_simple=False):
        """Get measurement mode simple|advanced

        Args:
            return_is_simple (bool): if True, return bool True if simple mode

        Returns:
            bool if return_is_simple else string simple|advanced
        """

        val = self.query('MEASure:MODE?')
        val = val.lower()
        if  return_is_simple:
            return val == 'simple'
        else:
            return val

    def get_measure_adv_item(self, idx):
        """Get advanced measurement type

        Args:
            idx (int): index of item [1-12]
        """
        assert 0 < idx < 13, 'idx out of range: 1 <= idx <= 12'
        self._check_measure_mode('advanced')
        return self.query(f'MEASure:ADV:P{idx}:TYPE?').lower()

    def get_measure_adv_nitems(self):
        """Gets the total number of advanced measurement items displayed

        Returns:
            int: number of items displayed
        """
        self._check_measure_mode('advanced')
        return int(self.query('MEAS:ADV:LIN?'))

    def get_measure_adv_source(self, idx, source_num=1):
        """Get the source of the measurment item.

        Args:
            idx (int): index of item [1-12]
            source_num (int): source number 1|2
        """
        assert 0 < idx < 13, 'idx out of range: 1 <= idx <= 12'
        self._check_measure_mode('advanced')
        return int(self.query(f'MEAS:ADV:P{idx}:SOURce{source_num}?').replace('C', ''))

    def get_measure_adv_state(self, idx):
        """Get the state of the measurment item.

        Args:
            idx (int): index of item [1-12]

        Returns:
            bool: True if item is ON
        """
        assert 0 < idx < 13, 'idx out of range: 1 <= idx <= 12'
        self._check_measure_mode('advanced')
        state = self.query(f'MEAS:ADV:P{idx}?')
        return state == 'ON'

    def get_measure_adv_style(self):
        """Get the display mode of the advanced measurements. Need M2 for more than 5 measurments. Need M1 for histograms

        Returns:
            int: 1|2 for M1 or M2 modes
        """
        return int(self.query('MEAS:ADV:STYL?')[1])

    def get_measure_adv_value(self, idx):
        """get value of advanced measurement item

        Args:
            idx (int): index of item [1-12]
        """

        # check input
        assert 0 < idx < 13, 'idx out of range: 1 <= idx <= 12'

        # get value
        val = self.query(f'MEAS:ADV:P{idx}:VAL?')

        # try conversion
        try:
            return float(val)
        except ValueError:
            if val == '***':
                return np.nan

    def get_measure_simple_source(self):
        """Get source for the simple measurement, expecting channel

        Returns:
            int: channel number
        """
        self._check_measure_mode('simple')

        val = self.query(f'MEAS:SIMP:SOURce?')

        return int(val[-1])

    def get_measure_simple_value(self, item, ch=None):
        """Get specified measurement value. Items do not need to be displayed  to be read out.

        Args:
            item  (str): ALL|PKPK|MAX|MIN|AMPL|TOP|BASE|LEVELX|CMEAN|MEAN|
                        STDEV|VSTD|RMS|CRMS|MEDIAN|CMEDIAN|OVSN|FPRE|
                        OVSP|RPRE|PER|FREQ|TMAX|TMIN|PWID|NWID|DUTY|
                        NDUTY|WID|NBWID|DELAY|TIMEL|RISE|FALL|RISE20T80
                        |FALL80T20|CCJ|PAREA|NAREA|AREA|ABSAREA|CYCLES|
                        REDGES|FEDGES|EDGES|PPULSES|NPULSES|PACArea|
                        NACArea|ACArea|ABSACArea
            ch (int|None): if None, measure current channel source, if int, check channel"""

        self._check_measure_mode('simple')

        # check item from list
        list_lower = [par.lower() for par in self.MEASUREMENT_ITEMS]
        item = item.lower()
        if item not in list_lower:
            raise RuntimeError(f'Item not in list: {self.MEASUREMENT_ITEMS}')
        idx = list_lower.index(item)
        par = self.MEASUREMENT_ITEMS[idx]

        # check channel
        if ch is not None:
            ch_actual = self.get_measure_simple_source()
            if ch != ch_actual:

                run_state = self.get_run_state()

                # get current value, make sure it changes before reporting something
                if not run_state:
                    old_val = np.around(float(self.get_measure_simple_value(item, None)), 4)

                # switch channels
                self.set_measure_simple_source(ch)
                print(f'Set simple measurment source to C{ch}')

                # wait
                if run_state:
                    time.sleep(0.5)
                else:
                    val = float(self.query(f'MEAS:SIMP:VAL? {par}'))

                    while old_val == np.around(val, 4):
                        time.sleep(0.1)
                        val = float(self.query(f'MEAS:SIMP:VAL? {par}'))

        # get value
        val = self.query(f'MEAS:SIMP:VAL? {par}')
        try:
            return float(val)
        except ValueError:
            return val

    def get_measure_state(self):
        """Get measurement state on/off

        Returns:
            bool: if True, turn measurements are active
        """
        val = self.query('MEAS?')
        return val == 'ON'

    def get_run_state(self):
        """Returns:
                bool: True if run. False if Stop
        """
        return bool(int(self.query('ACQ:STATE?')))

    def get_sequence(self):
        """Returns:
                bool: True if ON, False if OFF
        """
        return self.query('ACQuire:SEQuence?') == 'ON'

    def get_sequence_count(self):
        """
            Returns the current count setting: number of memory segments to acquire.

            The maximum number of segments may be limited by the memory depth of your oscilloscope.

            Returns:
                int: number of counts, is a power of 2
        """
        return int(self.query('ACQuire:SEQuence:COUNt?').strip())

    def get_smpl_rate(self):
        """Returns:
                float: sampling rate for fixed sampling rate mode
        """
        return float(self.query('ACQuire:SRATe?').strip())

    def get_time_delay(self):
        """Returns:
                float: delay between the trigger event and the delay reference point on the screen in seconds
        """
        return float(self.query('TIMebase:DELay?').strip())

    def get_time_scale(self):
        """Returns:
                float: horizontal scale in seconds/div
        """
        return float(self.query('TIMebase:SCALe?').strip())

    def get_trig_mode(self):
        """Returns:
            str: trigger mode (auto|normal|single)
        """
        return self.query('TRIGger:MODE?').lower()

    def get_trig_state(self):
        """Returns:
            str: trigger state (Arm|Ready|Auto|Trig'd|Stop|Roll).
        """
        return self.query('TRIGger:STATus?')

    def get_wave_ch(self):
        """Returns:
            int: channel number corresponding to waveform to be transferred from the oscilloscope
        """
        return int(self.query('WAVeform:SOURce?')[1])

    def get_wave_startpt(self):
        """Returns:
            int: the starting index of the data for waveform transfer.
        """
        return int(self.query('WAVeform:STARt?').strip())

    def get_wave_interval(self):
        """Returns:
            int: the interval between data points for waveform transfer.
        """
        return int(self.query('WAVeform:INTerval?'))

    def get_wave_npts(self):
        """Returns:
            float: the number of waveform points to be transferred
        """
        return float(self.query('WAVeform:POINt?').strip())

    def get_wave_maxpt(self):
        """Returns:
            float: the maximum points of one piece, when it needs to read the waveform data in pieces.
        """
        return float(self.query('WAVeform:MAXPoint?').strip())

    def get_wave_width(self):
        """Returns:
            str: output format for the transfer of waveform data (byte|word).
        """
        return self.query('WAVeform:WIDTh?').lower()

    # simple commands
    def set_adc_resolution(self, bits):
        """Set the number of bits used in data acquisition

        Args:
            bits (int): 8|10
        """
        if bits not in (8, 10):
            raise RuntimeError(f'Input bits must be 8 or 10, not "{bits}"')

        state = self.get_run_state()
        self.run()
        self.write(f'ACQuire:RESolution {bits}B')
        if not state:
            self.stop()

    def set_ch_coupling(self, ch, mode):
        """Selects the coupling mode of the specified input channel.

        Args:
            ch (int): channel number
            mode (str): DC|AC|GND
        """
        mode = mode.upper()
        assert mode in ('DC', 'AC', 'GND'), 'mode must be one of DC, AC, or GND'
        self.write(f'CHANnel{int(ch)}:COUPling {mode}')

    def set_ch_impedance(self, ch, z):
        """Sets the input impedance of the selected channel.
            There are two impedance values available. They are 1M and 50.

        Args:
            ch (int): channel number
            z (str):  1M|50
        """
        z = str(z).upper()

        if z == '1M':
            self.write(f'CHANnel{int(ch)}:IMP ONEMeg')
        elif z == '50':
            self.write(f'CHANnel{int(ch)}:IMP FIFTy')
        else:
            raise RuntimeError('z must be one of "1M" or "50"')

    def set_ch_offset(self, ch, offset):
        """Set vertical offset of the channel.

            The maximum ranges depend on the fixed sensitivity setting.
            The range of legal values varies with the value set by self.set_ch_vscale

        Args:
            ch (int): channel number
            offset (float): offset value in volts
        """
        return self.write(f'CHANnel{int(ch)}:OFFSet {offset:g}')

    def set_ch_probe(self, ch, attenuation=None):
        """Specifies the probe attenuation factor for the selected channel.

            This command does not change the actual input sensitivity of the oscilloscope.
            It changes the reference constants for scaling the  display factors, for making
            automatic measurements, and for setting trigger levels.

        Args:
            ch (int): channel number
            attenuation (float|None): if none, set to default (1X); else should be a float
        """
        if attenuation is None:
            self.write(f'CHANnel{int(ch)}:PROBe DEFault')
        else:
            assert 1e-6 < attenuation < 1e6, 'Attenuation out of bounds: (1e-6, 1e6)'
            self.write(f'CHANnel{int(ch)}:PROBe VALue {attenuation:g}')

    def set_ch_scale(self, ch, scale):
        """Sets the vertical sensitivity in Volts/div.

            If the probe attenuation is changed, the scale value is multiplied by the probe's
            attenuation factor.

        Args:
            ch (int): channel number
            scale (float): vertical scaling
        """
        return self.write(f'CHANnel{int(ch)}:SCALe {scale:g}')

    def set_ch_state(self, ch, on):
        """Turns the display of the specified channel on or off.

        Args:
            ch (int): channel number
            on (bool): if True, turn channel on. If False turn channel off.
        """
        state = 'ON' if on else 'OFF'
        self.write(f'CHANnel{int(ch)}:SWITch {state}')

    def set_ch_unit(self, ch, unit):
        """Changes the unit of input signal of specified channel: voltage (V) or current (A)

        Args:
            ch (int): channel number
            unit (str): V|A for volts or amps
        """
        unit = unit.upper()
        assert unit in ('V', 'A'), 'unit must be one of "V" or "A"'
        self.write(f'CHANnel{int(ch)}:UNIT {unit}')

    def set_measure_mode(self, mode):
        """Set measurement mode simple or advanced

        Args:
            mode (str): simple|advanced
        """

        if mode.lower() in 'simple':
            mode = 'SIMP'
        elif mode.lower() in 'advanced':
            mode = 'ADV'
        else:
            raise RuntimeError('mode must be simple|advanced')

        self.write(f'MEASure:MODE {mode}')

    def set_measure_state(self, state):
        """Set measurement state on/off

        Args:
            state (bool): if True, turn measurements on
        """
        state = 'ON' if state else 'OFF'
        self.write(f'MEASure {state}')

    def set_measure_adv_item(self, idx, item):
        """Set advanced measurement item

        Args:
            idx (int): index of item [1-12]
            item (str):    PKPK|MAX|MIN|AMPL|TOP|BASE|LEVELX|CMEAN|MEAN|
                           STDEV|VSTD|RMS|CRMS|MEDIAN|CMEDIAN|OVSN|FPRE|
                           OVSP|RPRE|PER|FREQ|TMAX|TMIN|PWID|NWID|DUTY|
                           NDUTY|WID|NBWID|DELAY|TIMEL|RISE|FALL|RISE20T80
                           |FALL80T20|CCJ|PAREA|NAREA|AREA|ABSAREA|CYCLES|
                           REDGES|FEDGES|EDGES|PPULSES|NPULSES|PACArea|
                           NACArea|ACArea|ABSACArea
        """

        # check index input
        assert 0 < idx < 13, 'idx out of range: 1 <= idx <= 12'

        # check can display this many items
        if idx > self.get_measure_adv_nitems():
            self.set_measure_adv_nitems(idx)

        # check item from list
        list_lower = [par.lower() for par in self.MEASUREMENT_ITEMS]
        item = item.lower()
        if item not in list_lower:
            raise RuntimeError(f'Item not in list: {self.MEASUREMENT_ITEMS}')
        idxx = list_lower.index(item)
        par = self.MEASUREMENT_ITEMS[idxx]

        # write state
        self.write(f'MEAS:ADV:P{idx}:TYPE {par}')

    def set_measure_adv_nitems(self, nitems):
        """Sets the total number of advanced measurement items displayed

        Args:
            items (int): number of items to display [1-12]
        """

        # check input
        assert 0 < nitems < 13, 'nitems out of range: 1 <= nitems <= 12'

        # check mode can support this many items
        if nitems > self.MEASURE_ADV_MODE1_MAX:
            self.set_measure_adv_style(2)

        # set
        self.write(f'MEAS:ADV:LIN {nitems}')

    def set_measure_adv_state(self, idx, state):
        """Set the state of the measurment item.

        Args:
            idx (int): index of item [1-12]
            state (bool): if true, turn item on
        """
        assert 0 < idx < 13, 'idx out of range: 1 <= idx <= 12'

        # check can display this many items
        if idx > self.get_measure_adv_nitems():
            self.set_measure_adv_nitems(idx)

        state = 'ON' if state else 'OFF'
        self.write(f'MEAS:ADV:P{idx} {state}')

    def set_measure_adv_source(self, idx, ch, source_num=1):
        """Set the source of the measurment item.

        Args:
            idx (int): index of item [1-12]
            ch (int): channel number
            source_num (int): source number 1|2
        """
        assert 0 < idx < 13, 'idx out of range: 1 <= idx <= 12'

        # check can display this many items
        if idx > self.get_measure_adv_nitems():
            self.set_measure_adv_nitems(idx)

        self.write(f'MEAS:ADV:P{idx}:SOURce{source_num} C{ch}')

    def set_measure_adv_style(self, mode=1):
        """Set the display mode of the advanced measurements. Need M2 for more than 5 measurments. Need M1 for histograms

        Args:
            mode (int): 1|2 for M1 or M2 modes
        """
        assert mode in (1,2), 'mode must be one of 1|2'
        self.write(f'MEAS:ADV:STYL M{mode}')

    def set_measure_simple_item(self, item, state=False):
        """Set simple measurement item on/off

        Args:
            item (str):    ALL|PKPK|MAX|MIN|AMPL|TOP|BASE|LEVELX|CMEAN|MEAN|
                           STDEV|VSTD|RMS|CRMS|MEDIAN|CMEDIAN|OVSN|FPRE|
                           OVSP|RPRE|PER|FREQ|TMAX|TMIN|PWID|NWID|DUTY|
                           NDUTY|WID|NBWID|DELAY|TIMEL|RISE|FALL|RISE20T80
                           |FALL80T20|CCJ|PAREA|NAREA|AREA|ABSAREA|CYCLES|
                           REDGES|FEDGES|EDGES|PPULSES|NPULSES|PACArea|
                           NACArea|ACArea|ABSACArea
            state (bool): if True, turn measurement parameter on
        """

        # get state
        state = 'ON' if state else 'OFF'

        # do all
        if item.lower() == 'all':
            for par in self.MEASUREMENT_ITEMS:
                self.write(f'MEASure:SIMPle:ITEM {par},{state}')

        else:

            # check item from list
            list_lower = [par.lower() for par in self.MEASUREMENT_ITEMS]
            item = item.lower()
            if item not in list_lower:
                raise RuntimeError(f'Item not in list: {self.MEASUREMENT_ITEMS}')
            idx = list_lower.index(item)
            par = self.MEASUREMENT_ITEMS[idx]

            # write state
            self.write(f'MEASure:SIMPle:ITEM {par},{state}')

    def set_measure_simple_source(self, ch):
        """Set source for the simple measurement

        Args:
            ch (int): channel number
        """
        self.write(f'MEAS:SIMP:SOUR C{ch}')

    def set_run_state(self, run):
        """Start/Stop taking data, equivalent to pressing the Run/Stop button on the front panel.

        Args:
            run (bool): if True, RUN. If False, STOP
        """
        if run:
            self.run()
        else:
            self.stop()

    def set_sequence(self, state):
        """Enables or disables sequence acquisition mode.

        Args:
            state (bool): If True, sequence on. If False, sequence off.
        """
        if state:
            self.write('ACQuire:SEQuence ON')
        else:
            self.write('ACQuire:SEQuence OFF')

    def set_sequence_count(self, value):
        """Sets the number of memory segments to acquire.

        The maximum number of segments may be limited by the memory depth of your oscilloscope.

        Args:
            value (int): count setting, must be a power of two
        """
        if value % 2 != 0:
            raise RuntimeError(f'Input {value} must be a power of 2')

        self.write(f'ACQuire:SEQuence:COUNt {int(value)}')

    def set_smpl_rate(self, rate):
        """Sets the sampling rate when in the fixed sampling rate mode.

        Args:
            rate (float|str): sample rate in pts/sec or "auto"
        """

        if str(rate) in 'auto':
            self.write('ACQuire:MMANagement AUTO')
        else:
            self.write('ACQuire:MMANagement FSRate')
            self.write(f'ACQuire:SRATe {rate:g}')

    def set_time_delay(self, delay):
        """Specifies the main timebase delay.

            This delay is the time between the trigger event and the delay reference
            point on the screen

        Args:
            delay (float): delay in seconds between the trigger event and the delay reference
            point on the screen
        """
        self.write(f'TIMebase:DELay {float(delay):E}')

    def set_time_scale(self, scale):
        """Sets the horizontal scale per division for the main window.

            Due to the limitation of the expansion strategy, when the time
            base is set from large to small, it will automatically adjust to
            the minimum time base that can be set currently.

        Args:
            scale (float): seconds per division
        """
        self.write(f'TIMebase:SCALe {scale:E}')

    def set_trig_mode(self, mode):
        """Sets the mode of the trigger.

        Args:
            mode (str): single|normal|auto
        """

        mode = mode.lower()

        if mode in 'single': self.write('TRIGger:MODE SINGle')
        elif mode in 'normal': self.write('TRIGger:MODE NORMal')
        elif mode in 'auto': self.write('TRIGger:MODE AUTO')
        else:
            raise RuntimeError("mode must be one of 'single', 'normal', or 'auto'")

    def set_trig_state(self, state):
        """Set trigger state

        Args:
            state (str): RUN|STOP
        """
        if state.upper() in 'RUN':
            self.write('TRIGger:RUN')
        elif state.upper() in 'STOP':
            self.write('TRIGger:STOP')
        else:
            raise RuntimeError('Bad state input, should be one of RUN or STOP')

    def set_wave_ch(self, ch):
        """Specifies the source waveform to be transferred from the oscilloscope

        Args:
            ch (int): channel number
        """
        self.write(f'WAVeform:SOURce C{int(ch)}')

    def set_wave_startpt(self, pt):
        """Args:
            pt (int): index of starting data point for waveform transfer
        """
        self.write(f'WAVeform:STARt {int(pt)}')

    def set_wave_interval(self, interval):
        """Args:
            interval (int): interval between data points for waveform transfer
        """
        self.write(f'WAVeform:INTerval {int(interval)}')

    def set_wave_npts(self, npts):
        """Args:
            npts (int): number of waveform points to be transferred
        """
        self.write(f'WAVeform:POINt {int(npts)}')

    def set_wave_width(self, format):
        """Sets the current output format for the transfer of waveform data.

        Args:
            format (str): byte|word
        """
        format = format.upper()
        if format in 'BYTE':
            self.write('WAVeform:WIDTh BYTE')
        elif format in 'WORD':
            self.write('WAVeform:WIDTh WORD')

    # read waveform commands
    def get_wave_preamble(self, ch=None):
        """Get preamble for waveform data of specified channel (dict, see below for key values)

        Args:
            ch (int|None): channel number. If None, use current set channel

        Returns:
            dict: channel-specific scope settings
                adc_bit:        number of bytes in adc
                bandwidth:      bandwidth limit. OFF, 20M, 200M
                channel:        wave source id
                code_per_div:   the value is different for different vertical gain of different
                                models
                coupling:       vertical coupling. DC, AC, GND
                comm_type:      chosen by remote command comm_format
                comm_order:     chosen by remote command comm_format
                data_bytes:     length in bytes of 1st simple data array. In transmitted
                                waveform, represent the number of transmitted bytes in accordance
                                with the parameter of the :WAVeform:POINt remote command and the
                                used format (see comm_type). Only for analog channels.
                data_first_pt:  indicates the offset relative to the beginning of the trace buffer.
                                Value is the same as the parameter of the :WAVeform:STARt remote
                                command.
                data_interval:  indicates the interval between data points for waveform transfer.
                                Value is the same as the parameter of the :WAVeform:INTerval remote
                                command.
                data_npts:      number of data points in the data array. Only for analog channels.
                                When sequence is on, this value means the points number of single
                                sequence frame.
                descriptor:     descriptor name. It is string, the first 8 chars are always
                                “WAVEDESC”
                fixed_v_gain:   Fixed vertical gain. This is the enumerated vertical scale.
                                This value is not intuitive, and the vertical scale is usually
                                represented by the value of address 156~159
                frame_index:    the specified frame index of sequence set by the parameter
                                <value1> of the command :WAVeform:SEQuence. Default Value is 1
                instrum_name:   string, always “Siglent SDS”.
                probe_atten:    probe attenuation factor
                read_frames:    number of sequence frames transferred this time. Used to calculate
                                the reading times of sequence waveform
                sample_interval:horizontal interval. Sampling interval for time domain waveforms.
                                Horizontal interval = 1/sampling rate
                sum_frames:     number of sequence frames acquired. Used to calculate the reading
                                times of sequence waveform
                t_delay_s:      horizontal offset. Trigger offset for the first sweep of the
                                trigger, seconds between the trigger and the first data point.
                                Unit is s.
                t_per_div:      time_base. This is the enumerated time/div.
                template:       template name. It is string, the first 7 chars are always “WAVEACE”.
                v_offset:       the value of vertical offset with probe attenuation
                v_offset_raw:   the value of vertical offset without probe attenuation
                v_per_div:      the value of vertical scale with probe attenuation.
                v_per_div_raw:  the value of vertical scale without probe attenuation.
                wave_desc_bytes:length in bytes of block WAVEDESC. (346)
        """

        # set channel
        if ch is not None:
            self.set_wave_ch(ch)

        # read preamble
        self.write("WAV:PREamble?", block=False)
        recv_all = self.read_bytes(350)
        recv = recv_all[recv_all.find(b'#')+11:]

        # convert to data
        preamble = {}

        # descriptor name. It is string, the first 8 chars are always “WAVEDESC”
        desc = (struct.unpack('s', recv[i:i+1])[0] for i in range(16))
        desc = (b''.join(desc)).decode()
        preamble['descriptor'] = desc.replace('\x00', '')

        # Template name. It is string, the first 7 chars are always “WAVEACE”.
        desc = (struct.unpack('s', recv[i:i+1])[0] for i in range(16, 32))
        desc = (b''.join(desc)).decode()
        preamble['template'] = desc.replace('\x00', '')

        # COMM_TYPE. Chosen by remote command comm_format. 0 -byte, 1- word. Default value is 0.
        options = ['byte', 'word']
        preamble['comm_type'] = options[struct.unpack('h', recv[32:34])[0]]

        # COMM_ORDER. Chosen by remote command comm_format. 0- LSB, 1- MSB. Default value is 0.
        options = ['LSB', 'MSB']
        preamble['comm_order'] = options[struct.unpack('h', recv[34:36])[0]]

        # wave_desc_length. Length in bytes of block WAVEDESC. (346)
        preamble['wave_desc_bytes'] = struct.unpack('i', recv[36:40])[0]

        # WAVE_ARRAY_1. Length in bytes of 1st simple data array. In
        # transmitted waveform, represent the number of transmitted bytes in
        # accordance with the parameter of the :WAVeform:POINt remote
        # command and the used format (see COMM_TYPE). Only for analog
        # channel.
        preamble['data_bytes'] = struct.unpack('i', recv[60:64])[0]

        # Instrument name. It is string, always “Siglent SDS”.
        desc = (struct.unpack('s', recv[i:i+1])[0] for i in range(76, 92))
        desc = (b''.join(desc)).decode()
        preamble['instrum_name'] = desc.replace('\x00', '')

        # Wave array count. Number of data points in the data array. Only for
        # analog channel. When sequence is on, this value means the points
        # number of single sequence frame.
        preamble['data_npts'] = struct.unpack('i', recv[116:120])[0]

        # First point. Indicates the offset relative to the beginning of the trace
        # buffer. Value is the same as the parameter of
        # the :WAVeform:STARt remote command.
        preamble['data_first_pt'] = struct.unpack('i', recv[132:136])[0]

        # Data interval. Indicates the interval between data points for
        # waveform transfer. Value is the same as the parameter of
        # the :WAVeform:INTerval remote command.
        preamble['data_interval'] = struct.unpack('i', recv[136:140])[0]

        # Read_frames, number of sequence frames transferred this time.
        # Used to calculate the reading times of sequence waveform
        preamble['read_frames'] = struct.unpack('i', recv[144:148])[0]

        # sum_frames, number of sequence frames acquired. Used to
        # calculate the reading times of sequence waveform
        preamble['sum_frames'] = struct.unpack('i', recv[148:152])[0]

        # Vertical gain. The value of vertical scale without probe attenuation.
        preamble['v_per_div_raw'] = struct.unpack('f', recv[156:160])[0]

        # Vertical offset. The value of vertical offset without probe attenuation
        preamble['v_offset_raw'] = struct.unpack('f', recv[160:164])[0]

        # code_per_div. The value is different for different vertical gain of different models
        # see page 562 of manual
        preamble['code_per_div'] = struct.unpack('f', recv[164:168])[0]
        if preamble['code_per_div'] > 2**8:
            preamble['code_per_div'] /= 2**4

        # Adc_bit
        preamble['adc_bit'] = struct.unpack('h', recv[172:174])[0]

        # The specified frame index of sequence set by the parameter
        # <value1> of the command :WAVeform:SEQuence. Default Value is 1
        preamble['frame_index'] = struct.unpack('h', recv[174:176])[0]

        # Horizontal interval. Sampling interval for time domain waveforms.
        # Horizontal interval = 1/sampling rate
        preamble['sample_interval'] = struct.unpack('f', recv[176:180])[0]

        # Horizontal offset. Trigger offset for the first sweep of the trigger,
        # seconds between the trigger and the first data point. Unit is s.
        preamble['t_delay_s'] = struct.unpack('d', recv[180:188])[0]

        # Time_base. This is the enumerated time/div.
        preamble['t_per_div'] = self.TDIV_ENUM[struct.unpack('h', recv[324:326])[0]]

        # Vertical coupling. 0-DC,1-AC,2-GND
        options = ['DC', 'AC', 'GND']
        preamble['coupling'] = options[struct.unpack('h', recv[326:328])[0]]

        # Probe attenuation.
        preamble['probe_atten'] = struct.unpack('f', recv[328:332])[0]

        # Fixed vertical gain. This is the enumerated vertical scale. This value
        # is not intuitive, and the vertical scale is usually represented by the
        # value of address 156~159
        preamble['fixed_v_gain'] = struct.unpack('h', recv[332:334])[0]

        # Bandwidth limit. 0-OFF,1-20M,2-200M
        options = ['OFF', '20M', '200M']
        preamble['bandwidth'] = options[struct.unpack('h', recv[334:336])[0]]

        # Wave source. 0-C1,1-C2,2-C3,3-C4
        # Normal command doesn't work?
        # preamble['channel'] = f"C{struct.unpack('h', recv[344:346])[0]}"
        preamble['channel'] = f"C{self.get_wave_ch()}"

        # adjusted vertical values
        preamble['v_per_div'] = preamble['v_per_div_raw'] * preamble['probe_atten']
        preamble['v_offset'] = preamble['v_offset_raw'] * preamble['probe_atten']

        # save
        self.preambles[preamble['channel']] = preamble

        return preamble

    def read_wave_ch(self, ch, start_pt=0):
        """Fetch the waveform data of a single source channel in volts

        Args:
            ch (int): channel number
            start_pt (int): index of starting point

        Returns:
            pd.DataFrame: voltages of single channel, indexed by timestamp
        """

        # setup input
        self.set_wave_startpt(start_pt)
        self.set_wave_ch(ch)

        # set number of points to read from
        points = self.get_wave_npts()
        one_piece_num = self.get_wave_maxpt()

        if points == 0:
            preamble = self.get_wave_preamble()
            points = preamble['data_npts']
            self.set_wave_npts(points)

        if points > one_piece_num:
            self.set_wave_npts(one_piece_num)

        # number of bits used in data read
        nbits = self.get_adc_resolution()
        if nbits > 8:
            self.set_wave_width('WORD')
        else:
            self.set_wave_width('BYTE')

        # read waveform data?
        read_times = math.ceil(points/one_piece_num)
        recv_all = []
        for i in range(0, read_times):
            start = i*one_piece_num
            self.set_wave_startpt(start)
            self.write("WAV:DATA?", block=False)
            recv_rtn = self.read_raw()
            recv = list(recv_rtn[recv_rtn.find(b'#') + 11:-2])
            recv_all += recv

        # convert bits to float
        if nbits > 8:
            convert_data = []
            for i in range(0, int(len(recv_all) / 2)):
                data_16bit = recv_all[2 * i + 1] * 256 + recv_all[2 * i]
                data = data_16bit >> (16-nbits)
                convert_data.append(data)
        else:
            convert_data = recv_all

        # convert ints to volts
        volt_value = []
        for data in convert_data:

            # 12bit-2047, 8bit-127
            if data > pow(2, nbits-1)-1:
                data = data - pow(2, nbits)
            else:
                pass
            volt_value.append(data)

        volt_value = np.array(volt_value)

        if nbits == 10:
            volt_value = volt_value/4

        # read waveform preamble
        preamble = self.get_wave_preamble()
        code = preamble['code_per_div']
        vdiv = preamble['v_per_div']
        offset = preamble['v_offset']
        tdiv = preamble['t_per_div']
        delay = preamble['t_delay_s']
        interval = preamble['sample_interval']

        # adjust voltage values
        volt_value = volt_value / code * vdiv - offset

        # get times
        idx = np.arange(len(volt_value))
        time_value = -delay - (tdiv * self.HORI_NUM / 2) + idx * interval

        # make data frame for output
        df = pd.DataFrame({f'C{ch}':volt_value, 'time_s':time_value})
        df.set_index('time_s', inplace=True)

        # save
        self.waveforms.drop(columns=[f'C{ch}'], errors='ignore', inplace=True)
        self.waveforms = pd.concat((self.waveforms, df), axis='columns')

        return df

    def read_wave_active(self, start_pt=0):
        """Read the waveforms of all active (displayed) analog input channels

        Args:
            start_pt (int): index of starting point to read

        Returns:
            pd.DataFrame: voltages of all active channels, indexed by timestamp
        """

        # stop run state

        self.stop()

        # iterate over all possible channels
        waves = []
        for i in range(1, 5):

            if self.get_ch_state(i):
                waves.append(self.read_wave_ch(i, start_pt=start_pt))

        # make dataframe
        df = pd.concat(waves, axis='columns')

        # save
        self.waveforms.drop(columns=df.columns, errors='ignore', inplace=True)
        self.waveforms = pd.concat((self.waveforms, df), axis='columns')

        return df

    def draw_wave(self, ch, ax=None, adjust_ylim=True, **plotargs):
        """Draw waveform for single channel, as shown on scope screen

            Must read the waveform first

        Args:
            ch (int): channel number
            ax (plt.Axes|None): object to draw in, if none then make new figure
            adjust_ylim (bool): if True, change ylim to match scope
            plotargs: passed to ax.plot()
        """

        # set axes
        if ax is None:
            plt.figure()
            ax = plt.gca()

        # draw
        try:
            df = self.waveforms[f'C{ch}']
        except KeyError:
            self.read_wave_ch(ch)
            df = self.waveforms[f'C{ch}']
        ax.plot(df.index.values, df.values, label=f'CH{ch}', **plotargs)

        # get preamble
        pre = self.preambles[f'C{ch}']

        # set plot elements
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Voltage (V)')
        if adjust_ylim:
            ax.set_ylim(-4*pre['v_per_div'], 4*pre['v_per_div'])
        ax.legend(fontsize='x-small')

    def draw_wave_all(self, ax=None, **plotargs):
        """Draw all read waveforms, as shown on scope screen

            Must read the waveform first

        Args:
            ax (plt.Axes|None): object to draw in, if none then make new figure
            plotargs: passed to ax.plot()
        """

        if ax is None:
            plt.figure()
            ax = plt.gca()

        for col in self.waveforms:
            self.draw_wave(int(col[1]), ax=ax, adjust_ylim=False, **plotargs)
