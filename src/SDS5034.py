# Communication with the SDS5034X Digital Oscilloscope from Siglent in TEK emulation mode
# Derek Fujimoto
# March 2023

import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import pyvisa, struct, math, gc

"""
    User running this code must have access to the port which the USB is connected to
    see: https://www.tincantools.com/accessing-devices-without-sudo/
    
    For angerona, we found: 
        idVendor           f4ec aka 62700
        idProduct          1008 aka 4104   

    See manual for commands: https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf
"""

HORI_NUM = 10

class SDS5034(object):

    """
        Connect to siglent digital oscilloscope and read waveforms   

        sds: pyvisa resource allowing write/read/query to the device
    """

    # global variables
    ADDRESS = 'TCPIP::{host}::INSTR'

    # see table 2 from https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf
    TDIV_ENUM = (   100e-12,200e-12,500e-12,\
                    1e-6,2e-6,5e-6,10e-6,20e-6,50e-6,100e-6,200e-6,500e-6,\
                    1e-3,2e-3,5e-3,10e-3,20e-3,50e-3,100e-3,200e-3,500e-3,\
                    1e-9,2e-9,5e-9,10e-9,20e-9,50e-9,100e-9,200e-9,500e-9,\
                    1,2,5,10,20,50,100,200,500,1000
                )

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

    # useful read and write passing to pyvisa.resources.TCPIPInstrument class
    def close(self):                        self.sds.close()
    def flush(self):                        self.sds.flush()
    def read(self, *args, **kwargs):        return self.sds.read(*args, **kwargs)
    def read_raw(self, *args, **kwargs):    return self.sds.read_raw(*args, **kwargs)
    def read_bytes(self, *args, **kwargs):  return self.sds.read_bytes(*args, **kwargs)
    def query(self, *args, **kwargs):       return self.sds.query(*args, **kwargs)
    def write(self, *args, **kwargs):       return self.sds.write(*args, **kwargs)
    def write_raw(self, *args, **kwargs):   return self.sds.write_raw(*args, **kwargs)

    # simple basic commands
    def default(self):      self.write('*RST')
    def reboot(self):       self.write('SYSTem:REBoot')
    def run(self):          self.write('ACQuire:STATE RUN')
    def stop(self):         self.write('ACQuire:STATE STOP')

    # simple queries
    def get_adc_resolution(self):   return int(self.query('ACQuire:RESolution?').replace('Bits', ''))
    def get_ch_coupling(self, ch):  return self.query(f'CHANnel{int(ch)}:COUPling?')
    def get_ch_impedance(self, ch): return self.query(f'CHANnel{int(ch)}:IMP?')
    def get_ch_offset(self, ch):    return self.query(f'CHANnel{int(ch)}:OFFS?')
    def get_ch_probe(self, ch):     return self.query(f'CHANnel{int(ch)}:PROBe?')
    def get_ch_state(self, ch):     return self.query(f'CHANnel{int(ch)}:SWITch?')
    def get_ch_unit(self, ch):      return self.query(f'CHANnel{int(ch)}:UNIT?')
    def get_ch_vscale(self, ch):    return self.query(f'CHANnel{int(ch)}:SCALe?')
    def get_id(self):               return self.query('*IDN?')
    def get_sequence(self):         return self.query('ACQuire:SEQuence?')
    def get_sequence_count(self):   return self.query('ACQuire:SEQuence:COUNt?')
    def get_smpl_rate(self):        return self.query('ACQuire:SRATe?')
    def get_time_scale(self):       return self.query('TIMebase:SCALe?')
    def get_trig_mode(self):        return self.query('TRIGger:MODE?')
    def get_trig_state(self):       return self.query('TRIGger:STATus?')
    def get_wave_ch(self):          return self.query('WAVeform:SOURce?')
    def get_wave_startpt(self):     return self.query('WAVeform:STARt?')
    def get_wave_interval(self):    return self.query('WAVeform:INTerval?')
    def get_wave_npts(self):        return float(self.query('WAVeform:POINt?').strip())
    def get_wave_maxpt(self):       return float(self.query('WAVeform:MAXPoint?').strip())
    def get_wave_width(self):       return self.query('WAVeform:WIDTh?')
    
    # simple commands
    def set_ch_coupling(self, ch, mode): 
        """
            ch: int, channel number
            mode: one of DC, AC, GND
        """ 
        mode = mode.upper()
        assert mode in ('DC', 'AC', 'GND'), 'mode must be one of DC, AC, or GND'
        self.write(f'CHANnel{int(ch)}:COUPling {mode}')
    
    def set_ch_impedance(self, ch, z): 
        """
            ch: int, channel number
            impedance: one of '1M' or '50'
        """ 
        z = str(z).upper()

        if z == '1M':
            self.write(f'CHANnel{int(ch)}:IMP ONEMeg')
        elif z == '50':
            self.write(f'CHANnel{int(ch)}:IMP FIFTy')
        else:
            raise RuntimeError('z must be one of "1M" or "50"')

    def set_ch_offset(self, ch, offset):
        return self.write(f'CHANnel{int(ch)}:OFFSet {offset:g}')
    
    def set_ch_probe(self, ch, attenuation=None):
        """
            If attenuation is none, set to default. Else attenuation is float
        """
        if attenuation is None:
            self.write(f'CHANnel{int(ch)}:PROBe DEFault')
        else:
            assert 1e-6 < attenuation < 1e6, 'Attenuation out of bounds: (1e-6, 1e6)'
            self.write(f'CHANnel{int(ch)}:PROBe VALue {attenuation:g}')
    
    def set_ch_state(self, ch, on=True):
        state = 'ON' if on else 'OFF'
        self.write(f'CHANnel{int(ch)}:SWITch {state}')
        
    def set_ch_unit(self, ch, unit):
        """
            unit: str, one of V or A for volts or amps resp.
        """
        unit = unit.upper()
        assert unit in ('V', 'A'), 'unit must be one of "V" or "A"'
        self.write(f'CHANnel{int(ch)}:UNIT {unit}')

    def set_ch_vscale(self, ch, scale):
        """
            set volts/div
        """
        return self.write(f'CHANnel{int(ch)}:SCALe {scale:g}')

    def set_sequence(self, state): 
        if state:
            self.write('ACQuire:SEQuence ON')
        else:
            self.write('ACQuire:SEQuence OFF')

    def set_sequence_count(self, value): 
        self.write(f'ACQuire:SEQuence:COUNt {int(value)}')
        
    def set_smpl_rate(self, rate):
        return self.write(f'ACQuire:SRATe {rate:g}')
    
    def set_time_scale(self, scale):
        """
            scale: seconds per division
        """
        self.write(f'TIMebase:SCALe {scale:g}')

    def set_trig_mode(self, mode):
        """
            mode in "single", 'normal', 'auto'
        """

        mode = mode.lower()

        if mode in 'single': self.write('TRIGger:MODE SINGle')
        elif mode in 'normal': self.write('TRIGger:MODE NORMal')
        elif mode in 'auto': self.write('TRIGger:MODE AUTO')
        else:
            raise RuntimeError("mode must be one of 'single', 'normal', or 'auto'")

    def set_trig_state(self, state):
        """
            state one of RUN or STOP
        """     
        if state.upper() in 'RUN':
            self.write('TRIGger:RUN')
        elif state.upper() in 'STOP':
            self.write('TRIGger:STOP')
        else:
            raise RuntimeError('Bad state input, should be one of RUN or STOP')

    def set_wave_ch(self, ch):          
        self.write(f'WAVeform:SOURce CH{int(ch)}')
    
    def set_wave_startpt(self, pt):
        self.write(f'WAVeform:STARt {int(pt)}')
    
    def set_wave_interval(self, interval):
        self.write(f'WAVeform:INTerval {int(interval)}')

    def set_wave_npts(self, npts):        
        """
            The command sets the number of waveform points to be
        """
        self.write(f'WAVeform:POINt {int(npts)}')

    def set_wave_width(self, format):
        format = format.upper()
        if format in 'BYTE':
            self.write('WAVeform:WIDTh BYTE')
        elif format in 'WORD':
            self.write('WAVeform:WIDTh WORD')


    # read waveform commands
    def get_wave_preamble(self):
        """
            Get preamble for waveform data

            WARNING: you should set waveform source first
                self.write(f"WAV:SOURce C{channel_number}")
        """

        # read data
        self.write("WAV:PREamble?")      # get the preamble
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
        preamble['channel'] = f"C{struct.unpack('h', recv[334:336])[0]}"

        # adjusted vertical values
        preamble['v_per_div'] = preamble['v_per_div_raw'] * preamble['probe_atten']
        preamble['v_offset'] = preamble['v_offset_raw'] * preamble['probe_atten']

        return preamble

    def read_wave_ch(self, ch, start_pt=0):
        """
            Read data from channel
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
        
        self.data_volts = np.array(volt_value)
        return self.data_volts

    def read_wave_time(self, start_pt=0):
        """
            Get timestampts for waveform data
        """

        # read waveform preamble
        self.set_wave_startpt(start_pt)
        preamble = self.get_wave_preamble()

        # get times
        time_value = []
        for idx in range(0, len(volt_value)):
            volt_value[idx] = volt_value[idx] / code * float(vdiv) - float(offset)
            time_data = -float(delay) - (float(tdiv) * HORI_NUM / 2) + idx * interval
            time_value.append(time_data)
        print(len(volt_value))

        # plt.figure(figsize=(7, 5))
        # plt.plot(time_value, volt_value, markersize=2, label=u"Y-T")
        # plt.legend()

