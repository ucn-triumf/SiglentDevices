Module SDS5034
==============

See [here](https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf) for additional SCPI commands and documentation.

Classes
-------

`SDS5034(hostname='tucan-scope1.triumf.ca')`
:   Connect to siglent digital oscilloscope and read waveforms   

    Instance variables

        preambles: dict of preamble values, saved as measured
        sds: pyvisa resource allowing write/read/query to the device
        waveforms: pd.DataFrame of waveform data in volts (includes all channels)

    hostname: ip address or DNC lookup of device

### Class variables

`ADDRESS`
:   Address format to connect to device

`HORI_NUM`
:   Number of horizontal divisions

`TDIV_ENUM`
:   time division values from table 2 of https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf

### Methods

`close(self)`
:   Close remote connection

`default(self)`
:   Resets the oscilloscope to the default configuration, equivalent to the Default button on the front panel

`draw_wave(self, ch, ax=None, adjust_ylim=True, **plotargs)`
:   Draw all read waveforms, as shown on scope screen
    
    ch:         int, channel id
    ax:         plt.Axes object for drawing, if none then make new
    adjust_ylim:if True, change ylim to match scope
    plotargs:   passed to ax.plot()

`draw_wave_all(self, ax=None, **plotargs)`
:   Draw all channels
    
    ax:         plt.Axes object for drawing, if none then make new
    plotargs:   passed to ax.plot()

`flush(self)`
:   Flush connection buffer

`get_adc_resolution(self)`
:   Get the number of bits used in data acquisition

`get_ch_coupling(self, ch)`
:   Returns the coupling mode of the specified channel.

`get_ch_impedance(self, ch)`
:   Returns the current impedance setting of the selected channel in Ohms.

`get_ch_offset(self, ch)`
:   Returns the offset value of the specified channel (volts).

`get_ch_probe(self, ch)`
:   Returns the current probe attenuation factor for the selected channel.

`get_ch_scale(self, ch)`
:   Returns the current vertical sensitivity of the specified channel (volts/div).

`get_ch_state(self, ch)`
:   Returns current status of the selected channel (ON/OFF). Return True if on.

`get_ch_unit(self, ch)`
:   Returns the current unit of the concerned channel.

`get_id(self)`
:   Returns identification string of device.

`get_run_state(self)`
:   Get RUN/STOP state. Return True if running.

`get_sequence(self)`
:   Returns whether the current sequence acquisition switch is on or not (True if ON).

`get_sequence_count(self)`
:   Returns the current count setting: number of memory segments to acquire. 
    The maximum number of segments may be limited by the memory depth of your oscilloscope.

`get_smpl_rate(self)`
:   Returns the current sampling rate when in the fixed sampling rate mode.

`get_time_delay(self)`
:   This delay is the time between the trigger event and the delay reference point on the screen (seconds).

`get_time_scale(self)`
:   Returns the current horizontal scale setting in seconds per division for the main window.

`get_trig_mode(self)`
:   Returns the current mode of trigger (auto|normal|single).

`get_trig_state(self)`
:   Reurns the current state of the trigger (Arm|Ready|Auto|Trig'd|Stop|Roll}).

`get_wave_ch(self)`
:   Returns the source waveform to be transferred from the oscilloscope.

`get_wave_interval(self)`
:   Returns the interval between data points for waveform transfer.

`get_wave_maxpt(self)`
:   Returns the maximum points of one piece, when it needs to read the waveform data in pieces.

`get_wave_npts(self)`
:   Returns the number of waveform points to be transferred.

`get_wave_preamble(self, ch=None)`
:   Get preamble for waveform data of specified channel (dict, see below for key values)
    
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

`get_wave_startpt(self)`
:   Returns the starting data point for waveform transfer.

`get_wave_width(self)`
:   Returns the current output format for the transfer of waveform data (byte|word).

`query(self, *args, **kwargs)`
:   Push query to device, read back response

`read(self, *args, **kwargs)`
:   Read from stream

`read_bytes(self, *args, **kwargs)`
:   Read raw bytes from stream

`read_raw(self, *args, **kwargs)`
:   Read raw data from stream

`read_wave_active(self, start_pt=0)`
:   Read the waveforms of all active (displayed) analog input channels
    
    start_pt:   int, starting point to read from (default: 0)

`read_wave_ch(self, ch, start_pt=0)`
:   Returns the waveform data of a single source channel in volts
    
    ch:         int, channel id number
    start_pt:   int, starting point to read from (default: 0)

`reboot(self)`
:   Restart the scope

`run(self)`
:   Start taking data, equivalent to pressing the Run button on the front panel

`set_adc_resolution(self, bits)`
:   Set the number of bits used in data acquisition

`set_ch_coupling(self, ch, mode)`
:   Selects the coupling mode of the specified input channel.
    
    ch:     int, channel number
    mode:   string, one of DC, AC, GND

`set_ch_impedance(self, ch, z)`
:   Sets the input impedance of the selected channel. 
    There are two impedance values available. They are 1 MOhm and 50.
    
    ch:         int, channel number
    impedance:  string, one of '1M' or '50'

`set_ch_offset(self, ch, offset)`
:   Allows adjustment of the vertical offset of the
    specified input channel. The maximum ranges depend on the
    fixed sensitivity setting.
    
    The range of legal values varies with the value set by self.set_ch_vscale 
    
    ch:     int, channel number
    offset: float, offset value in volts

`set_ch_probe(self, ch, attenuation=None)`
:   Specifies the probe attenuation factor for the selected channel. 
    This command does not change the actual input sensitivity of the oscilloscope. 
    It changes the reference constants for scaling the  display factors, for making 
    automatic measurements, and for setting trigger levels.
    
    ch:          int, channel number
    attenuation: if none, set to default (1X); else should be a float

`set_ch_scale(self, ch, scale)`
:   Sets the vertical sensitivity in Volts/div. If the
    probe attenuation is changed, the scale value is multiplied by
    the probe's attenuation factor.
    
    ch:     int, channel number
    scale:  float, vertical scaling

`set_ch_state(self, ch, on=True)`
:   Turns the display of the specified channel on or off.
    
    ch: int, channel number
    on: if True, turn channel on

`set_ch_unit(self, ch, unit)`
:   Changes the unit of input signal of specified
    channel: voltage (V) or current (A) 
    
    ch:     int, channel number
    unit:   str, one of V or A for volts or amps

`set_run_state(self, run=True)`
:   Start/Stop taking data, equivalent to pressing the Run/Stop button on the front panel

`set_sequence(self, state)`
:   Enables or disables sequence acquisition mode.
    
    state:  bool, if true, sequence on

`set_sequence_count(self, value)`
:   Sets the number of memory segments to
    acquire. The maximum number of segments may be limited
    by the memory depth of your oscilloscope. Must be a power of 2. 
    
    value: int, count setting

`set_smpl_rate(self, rate)`
:   Sets the sampling rate when in the fixed sampling rate mode.
    
    rate: float, rate in pts/sec or "auto"

`set_time_delay(self, delay)`
:   Specifies the main timebase delay. This delay
    is the time between the trigger event and the delay reference
    point on the screen
    
    delay: float, delay in seconds

`set_time_scale(self, scale)`
:   Sets the horizontal scale per division for the main window.
    Due to the limitation of the expansion strategy, when the time
    base is set from large to small, it will automatically adjust to
    the minimum time base that can be set currently.
    
    scale: seconds per division

`set_trig_mode(self, mode)`
:   Sets the mode of the trigger.
    
    mode: str, single|normal|auto

`set_trig_state(self, state)`
:   Set trigger state (RUN|STOP)
    
    state: str (RUN|STOP)

`set_wave_ch(self, ch)`
:   Specifies the source waveform to be transferred from the oscilloscope 
    
    ch: int, channel number

`set_wave_interval(self, interval)`
:   Sets the interval between data points for waveform transfer.
    
    interval: int

`set_wave_npts(self, npts)`
:   Sets the number of waveform points to be transferred
    
    npts: int, number of points

`set_wave_startpt(self, pt)`
:   Specifies the starting data point for waveform transfer 
    
    pt: int, starting index

`set_wave_width(self, format)`
:   Sets the current output format for the transfer of waveform data.
    
    format: str, byte|word

`stop(self)`
:   Stop taking data, equivalent to pressing the Stop button on the front panel

`write(self, *args, **kwargs)`
:   Write string to device

`write_raw(self, *args, **kwargs)`
:   Write raw bytestring to device
