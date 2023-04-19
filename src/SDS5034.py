# Communication with the SDS5034X Digital Oscilloscope from Siglent in TEK emulation mode
# Derek Fujimoto
# March 2023

import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import pyvisa, struct, math

"""
    User running this code must have access to the port which the USB is connected to
    see: https://www.tincantools.com/accessing-devices-without-sudo/
    
    For angerona, we found: 
        idVendor           f4ec aka 62700
        idProduct          1008 aka 4104   

    See manual for commands: https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf
"""

class SDS5034(object):

    """
        Connect to siglent digital oscilloscope and read waveforms   

        Instance variables

            preambles: dict of preamble values, saved as measured
            sds: pyvisa resource allowing write/read/query to the device
            waveforms: pd.DataFrame of waveform data in volts (includes all channels)
    """

    # global variables
    ADDRESS = 'TCPIP::{host}::INSTR'
    """Address format to connect to device"""

    HORI_NUM = 10
    """Number of horizontal divisions"""

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
    """time division values from table 2 of https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf"""

    def __init__(self, hostname='tucan-scope1.triumf.ca'):
        """
            hostname: ip address or DNC lookup of device
        """

        # connect to device
        rm = pyvisa.ResourceManager()
        self.sds = rm.open_resource(self.ADDRESS.format(host=hostname))

        # setup connection 
        self.sds.read_termination = '\n'
        self.sds.write_termination = '\n'

        # set chunk size for communication 
        self.sds.chunk_size = 20*1024*1024

        # set data storage
        self.preambles = {}
        self.waveforms = pd.DataFrame()

    # useful read and write passing to pyvisa.resources.TCPIPInstrument class
    def close(self):                        
        """
            Close remote connection
        """
        self.sds.close()

    def flush(self):
        """
            Flush connection buffer
        """
        self.sds.flush()

    def read(self, *args, **kwargs):        
        """
            Read from stream
        """
        return self.sds.read(*args, **kwargs)
    
    def read_raw(self, *args, **kwargs):    
        """
            Read raw data from stream
        """
        return self.sds.read_raw(*args, **kwargs)
    
    def read_bytes(self, *args, **kwargs):  
        """
            Read raw bytes from stream
        """
        return self.sds.read_bytes(*args, **kwargs)
    
    def query(self, *args, **kwargs):       
        """
            Push query to device, read back response
        """
        return self.sds.query(*args, **kwargs)
    
    def write(self, *args, **kwargs):       
        """
            Write string to device
        """
        return self.sds.write(*args, **kwargs)
    
    def write_raw(self, *args, **kwargs):   
        """
            Write raw bytestring to device
        """
        return self.sds.write_raw(*args, **kwargs)

    # simple basic commands
    def default(self):      
        """
            Resets the oscilloscope to the default configuration, equivalent to the Default button on the front panel
        """
        self.write('*RST')

    def reboot(self):       
        """
            Restart the scope
        """
        self.write('SYSTem:REBoot')
    
    def run(self):          
        """
            Start taking data, equivalent to pressing the Run button on the front panel
        """
        self.write('ACQuire:STATE RUN')
    
    def stop(self):         
        """
            Stop taking data, equivalent to pressing the Stop button on the front panel
        """
        self.write('ACQuire:STATE STOP')

    # simple queries
    
    def get_adc_resolution(self):   
        """
            Get the number of bits used in data acquisition
        """
        return int(self.query('ACQuire:RESolution?').replace('Bits', ''))
    
    def get_ch_coupling(self, ch):  
        """
            Returns the coupling mode of the specified channel.
        """
        return self.query(f'CHANnel{int(ch)}:COUPling?')
    
    def get_ch_impedance(self, ch): 
        """
            Returns the current impedance setting of the selected channel in Ohms.
        """

        response = self.query(f'CHANnel{int(ch)}:IMP?').strip()

        if response == 'ONEMeg': 
            return '1M'
        elif response == 'FIFTy': 
            return '50'
        else: 
            raise RuntimeError(f'Unexpected device response "{response}"')
    
    def get_ch_offset(self, ch):    
        """
            Returns the offset value of the specified channel (volts).
        """
        return float(self.query(f'CHANnel{int(ch)}:OFFS?').strip())
    
    def get_ch_probe(self, ch):     
        """
            Returns the current probe attenuation factor for the selected channel.
        """
        return float(self.query(f'CHANnel{int(ch)}:PROBe?').strip())
    
    def get_ch_scale(self, ch):    
        """
            Returns the current vertical sensitivity of the specified channel (volts/div).
        """
        return float(self.query(f'CHANnel{int(ch)}:SCALe?').strip())
    
    def get_ch_state(self, ch):     
        """
            Returns current status of the selected channel (ON/OFF). Return True if on. 
        """
        state = self.query(f'CHANnel{int(ch)}:SWITch?')

        return state.strip().upper() == 'ON'
    
    def get_ch_unit(self, ch):      
        """
            Returns the current unit of the concerned channel.
        """
        return self.query(f'CHANnel{int(ch)}:UNIT?')
    
    def get_id(self):               
        """
            Returns identification string of device.
        """
        return self.query('*IDN?')
    
    def get_run_state(self):
        """
            Get RUN/STOP state. Return True if running. 
        """
        return bool(int(self.query('ACQ:STATE?')))
        
    def get_sequence(self):         
        """
            Returns whether the current sequence acquisition switch is on or not (True if ON).
        """
        return self.query('ACQuire:SEQuence?') == 'ON'
    
    def get_sequence_count(self):   
        """
            Returns the current count setting: number of memory segments to acquire. 
            The maximum number of segments may be limited by the memory depth of your oscilloscope.
        """
        return int(self.query('ACQuire:SEQuence:COUNt?').strip())
    
    def get_smpl_rate(self):        
        """
            Returns the current sampling rate when in the fixed sampling rate mode.
        """
        return float(self.query('ACQuire:SRATe?').strip())

    def get_time_delay(self):
        """
            This delay is the time between the trigger event and the delay reference point on the screen (seconds).
        """
        return float(self.query('TIMebase:DELay?').strip())

    def get_time_scale(self):       
        """
            Returns the current horizontal scale setting in seconds per division for the main window.
        """
        return float(self.query('TIMebase:SCALe?').strip())
    
    def get_trig_mode(self):        
        """
            Returns the current mode of trigger (auto|normal|single).
        """
        return self.query('TRIGger:MODE?').lower()
    
    def get_trig_state(self):       
        """
            Reurns the current state of the trigger (Arm|Ready|Auto|Trig'd|Stop|Roll}).
        """
        return self.query('TRIGger:STATus?')
    
    def get_wave_ch(self):          
        """
            Returns the source waveform to be transferred from the oscilloscope.
        """
        return int(self.query('WAVeform:SOURce?')[1])
    
    def get_wave_startpt(self):     
        """
            Returns the starting data point for waveform transfer.
        """
        return int(self.query('WAVeform:STARt?').strip())
    
    def get_wave_interval(self):    
        """
            Returns the interval between data points for waveform transfer.
        """
        return int(self.query('WAVeform:INTerval?'))
    
    def get_wave_npts(self):        
        """
            Returns the number of waveform points to be transferred.
        """
        return float(self.query('WAVeform:POINt?').strip())
    
    def get_wave_maxpt(self):       
        """
            Returns the maximum points of one piece, when it needs to read the waveform data in pieces.
        """
        return float(self.query('WAVeform:MAXPoint?').strip())
    
    def get_wave_width(self):       
        """
            Returns the current output format for the transfer of waveform data (byte|word).
        """
        return self.query('WAVeform:WIDTh?').lower()
    
    # simple commands
    def set_adc_resolution(self, bits):   
        """
            Set the number of bits used in data acquisition
        """
        if bits not in (8, 10):
            raise RuntimeError(f'Input bits must be 8 or 10, not "{bits}"')
        self.write(f'ACQuire:RESolution {bits}Bits')
    
    def set_ch_coupling(self, ch, mode): 
        """
            Selects the coupling mode of the specified input channel.

            ch:     int, channel number
            mode:   string, one of DC, AC, GND
        """ 
        mode = mode.upper()
        assert mode in ('DC', 'AC', 'GND'), 'mode must be one of DC, AC, or GND'
        self.write(f'CHANnel{int(ch)}:COUPling {mode}')
    
    def set_ch_impedance(self, ch, z): 
        """
            Sets the input impedance of the selected channel. 
            There are two impedance values available. They are 1 MOhm and 50.

            ch:         int, channel number
            impedance:  string, one of '1M' or '50'
        """ 
        z = str(z).upper()

        if z == '1M':
            self.write(f'CHANnel{int(ch)}:IMP ONEMeg')
        elif z == '50':
            self.write(f'CHANnel{int(ch)}:IMP FIFTy')
        else:
            raise RuntimeError('z must be one of "1M" or "50"')

    def set_ch_offset(self, ch, offset):
        """
            Allows adjustment of the vertical offset of the
            specified input channel. The maximum ranges depend on the
            fixed sensitivity setting.

            The range of legal values varies with the value set by self.set_ch_vscale 

            ch:     int, channel number
            offset: float, offset value in volts
        """
        return self.write(f'CHANnel{int(ch)}:OFFSet {offset:g}')
    
    def set_ch_probe(self, ch, attenuation=None):
        """
            Specifies the probe attenuation factor for the selected channel. 
            This command does not change the actual input sensitivity of the oscilloscope. 
            It changes the reference constants for scaling the  display factors, for making 
            automatic measurements, and for setting trigger levels.
            
            ch:          int, channel number
            attenuation: if none, set to default (1X); else should be a float
        """
        if attenuation is None:
            self.write(f'CHANnel{int(ch)}:PROBe DEFault')
        else:
            assert 1e-6 < attenuation < 1e6, 'Attenuation out of bounds: (1e-6, 1e6)'
            self.write(f'CHANnel{int(ch)}:PROBe VALue {attenuation:g}')
    
    def set_ch_scale(self, ch, scale):
        """
            Sets the vertical sensitivity in Volts/div. If the
            probe attenuation is changed, the scale value is multiplied by
            the probe's attenuation factor.
            
            ch:     int, channel number
            scale:  float, vertical scaling
        """
        return self.write(f'CHANnel{int(ch)}:SCALe {scale:g}')

    def set_ch_state(self, ch, on=True):
        """
            Turns the display of the specified channel on or off.

            ch: int, channel number
            on: if True, turn channel on
        """
        state = 'ON' if on else 'OFF'
        self.write(f'CHANnel{int(ch)}:SWITch {state}')
        
    def set_ch_unit(self, ch, unit):
        """
            Changes the unit of input signal of specified
            channel: voltage (V) or current (A) 

            ch:     int, channel number
            unit:   str, one of V or A for volts or amps
        """
        unit = unit.upper()
        assert unit in ('V', 'A'), 'unit must be one of "V" or "A"'
        self.write(f'CHANnel{int(ch)}:UNIT {unit}')

    def set_run_state(self, run=True):
        """
            Start/Stop taking data, equivalent to pressing the Run/Stop button on the front panel
        """
        if run: 
            self.run()
        else:
            self.stop()

    def set_sequence(self, state): 
        """
            Enables or disables sequence acquisition mode.

            state:  bool, if true, sequence on
        """
        if state:
            self.write('ACQuire:SEQuence ON')
        else:
            self.write('ACQuire:SEQuence OFF')

    def set_sequence_count(self, value): 
        """
            Sets the number of memory segments to
            acquire. The maximum number of segments may be limited
            by the memory depth of your oscilloscope. Must be a power of 2. 

            value: int, count setting
        """
        if value % 2 != 0: 
            raise RuntimeError(f'Input {value} must be a power of 2')
        
        self.write(f'ACQuire:SEQuence:COUNt {int(value)}')
        
    def set_smpl_rate(self, rate):
        """
            Sets the sampling rate when in the fixed sampling rate mode.

            rate: float, rate in pts/sec or "auto"
        """

        if str(rate) in 'auto':
            self.write('ACQuire:MMANagement AUTO')
        else:
            self.write('ACQuire:MMANagement FSRate')
            self.write(f'ACQuire:SRATe {rate:g}')
    
    def set_time_delay(self, delay):
        """
            Specifies the main timebase delay. This delay
            is the time between the trigger event and the delay reference
            point on the screen

            delay: float, delay in seconds
        """
        self.write(f'TIMebase:DELay {float(delay):E}')

    def set_time_scale(self, scale):
        """
            Sets the horizontal scale per division for the main window.
            Due to the limitation of the expansion strategy, when the time
            base is set from large to small, it will automatically adjust to
            the minimum time base that can be set currently.

            scale: seconds per division
        """
        self.write(f'TIMebase:SCALe {scale:E}')

    def set_trig_mode(self, mode):
        """
            Sets the mode of the trigger.

            mode: str, single|normal|auto
        """

        mode = mode.lower()

        if mode in 'single': self.write('TRIGger:MODE SINGle')
        elif mode in 'normal': self.write('TRIGger:MODE NORMal')
        elif mode in 'auto': self.write('TRIGger:MODE AUTO')
        else:
            raise RuntimeError("mode must be one of 'single', 'normal', or 'auto'")

    def set_trig_state(self, state):
        """
            Set trigger state (RUN|STOP)

            state: str (RUN|STOP)
        """     
        if state.upper() in 'RUN':
            self.write('TRIGger:RUN')
        elif state.upper() in 'STOP':
            self.write('TRIGger:STOP')
        else:
            raise RuntimeError('Bad state input, should be one of RUN or STOP')

    def set_wave_ch(self, ch):
        """
            Specifies the source waveform to be transferred from the oscilloscope 

            ch: int, channel number
        """
        self.write(f'WAVeform:SOURce C{int(ch)}')
    
    def set_wave_startpt(self, pt):
        """
            Specifies the starting data point for waveform transfer 

            pt: int, starting index
        """
        self.write(f'WAVeform:STARt {int(pt)}')
    
    def set_wave_interval(self, interval):
        """
            Sets the interval between data points for waveform transfer.

            interval: int
        """
        self.write(f'WAVeform:INTerval {int(interval)}')

    def set_wave_npts(self, npts):        
        """
            Sets the number of waveform points to be transferred

            npts: int, number of points
        """
        self.write(f'WAVeform:POINt {int(npts)}')

    def set_wave_width(self, format):
        """
            Sets the current output format for the transfer of waveform data.

            format: str, byte|word
        """
        format = format.upper()
        if format in 'BYTE':
            self.write('WAVeform:WIDTh BYTE')
        elif format in 'WORD':
            self.write('WAVeform:WIDTh WORD')

    # read waveform commands
    def get_wave_preamble(self, ch=None):
        """
            Get preamble for waveform data of specified channel (dict, see below for key values)

            ch: int, channel for which to read preamble. If none, use current set channel

            keys: 
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
        self.write("WAV:PREamble?")
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
        """
            Returns the waveform data of a single source channel in volts

            ch:         int, channel id number
            start_pt:   int, starting point to read from (default: 0)
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

        # read waveform data? 
        read_times = math.ceil(points/one_piece_num)
        recv_all = []
        for i in range(0, read_times):
            start = i*one_piece_num
            self.set_wave_startpt(start)
            self.write("WAV:DATA?")
            recv_rtn = self.read_raw()
            recv = list(recv_rtn[recv_rtn.find(b'#') + 11:-2])
            recv_all += recv

        # convert bits to float
        if nbits > 8:
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
            if data > pow(2,nbits-1)-1:
                data = data - pow(2,nbits)
            else:
                pass
            volt_value.append(data)
        
        volt_value = np.array(volt_value)
        
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
        """
            Read the waveforms of all active (displayed) analog input channels

            start_pt:   int, starting point to read from (default: 0)
        """

        # stop run state
        
        self.stop()

        # iterate over all possible channels
        waves = []
        for i in range(1, 5):

            if self.get_ch_state(i).strip() == 'ON':
                waves.append(self.read_wave_ch(i, start_pt=start_pt))

        # make dataframe
        df = pd.concat(waves, axis='columns')

        # save
        self.waveforms.drop(columns=df.columns, errors='ignore', inplace=True)
        self.waveforms = pd.concat((self.waveforms, df), axis='columns')

        return df
                
    def draw_wave(self, ch, ax=None, adjust_ylim=True, **plotargs):
        """
            Draw all read waveforms, as shown on scope screen

            ch:         int, channel id
            ax:         plt.Axes object for drawing, if none then make new
            adjust_ylim:if True, change ylim to match scope
            plotargs:   passed to ax.plot()
        """

        # set axes
        if ax is None: 
            plt.figure()
            ax = plt.gca()

        # draw
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
        """
            Draw all channels

            ax:         plt.Axes object for drawing, if none then make new
            plotargs:   passed to ax.plot()
        """

        if ax is None:
            plt.figure()
            ax = plt.gca()

        for col in self.waveforms:
            self.draw_wave(int(col[1]), ax=ax, adjust_ylim=False, **plotargs)