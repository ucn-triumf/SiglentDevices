# Rigol Dg1032z

[Siglentdevices Index](../README.md#siglentdevices-index) /
[Siglentdevices](./index.md#siglentdevices) /
Rigol Dg1032z

> Auto-generated documentation for [SiglentDevices.RIGOL_DG1032Z](../../SiglentDevices/RIGOL_DG1032Z.py) module.

- [Rigol Dg1032z](#rigol-dg1032z)
  - [DG1032Z](#dg1032z)
    - [DG1032Z.get_ch_state](#dg1032zget_ch_state)
    - [DG1032Z.get_mod_am_state](#dg1032zget_mod_am_state)
    - [DG1032Z.get_wave](#dg1032zget_wave)
    - [DG1032Z.set_amp](#dg1032zset_amp)
    - [DG1032Z.set_freq](#dg1032zset_freq)
    - [DG1032Z.set_mod_am](#dg1032zset_mod_am)
    - [DG1032Z.set_mod_am_state](#dg1032zset_mod_am_state)
    - [DG1032Z.set_offset](#dg1032zset_offset)
    - [DG1032Z.set_state](#dg1032zset_state)
    - [DG1032Z.set_wave](#dg1032zset_wave)
    - [DG1032Z.set_wave_custom](#dg1032zset_wave_custom)
    - [DG1032Z.wait](#dg1032zwait)
    - [DG1032Z.write](#dg1032zwrite)

## DG1032Z

[Show source in RIGOL_DG1032Z.py:18](../../SiglentDevices/RIGOL_DG1032Z.py#L18)

Control RIGOL function generator

#### Attributes

- `block_until_finished` *bool* - if true, block set operations until finished

#### Signature

```python
class DG1032Z(SiglentBase):
    def __init__(self, hostname="tucan-awg01.triumf.ca"):
        ...
```

### DG1032Z.get_ch_state

[Show source in RIGOL_DG1032Z.py:68](../../SiglentDevices/RIGOL_DG1032Z.py#L68)

Get channel on/off state

#### Arguments

- `ch` *int* - channel number, 1|2

#### Returns

- `bool` - True if channel is on

#### Signature

```python
def get_ch_state(self, ch=1):
    ...
```

### DG1032Z.get_mod_am_state

[Show source in RIGOL_DG1032Z.py:81](../../SiglentDevices/RIGOL_DG1032Z.py#L81)

Get output modification state

#### Arguments

- `ch` *int* - channel number 1|2

#### Returns

- `bool` - True if modification active, else False

#### Signature

```python
def get_mod_am_state(self, ch=1):
    ...
```

### DG1032Z.get_wave

[Show source in RIGOL_DG1032Z.py:92](../../SiglentDevices/RIGOL_DG1032Z.py#L92)

Read out waveform being applied currently by AWG

#### Arguments

- `ch` *int* - channel number, 1|2

#### Returns

dict of results:
    - `wave` *str* - wave shape, SIN|SQU|TRI
    - `freq` *float* - frequency in Hz. 1 uHz to 60 MHz
    - `amp` *float* - Vpp in volts
    - `offset` *float* - DC offset in volts
    - `phase` *float* - phase in degrees. 0 to 360 deg

#### Signature

```python
def get_wave(self, ch=1):
    ...
```

### DG1032Z.set_amp

[Show source in RIGOL_DG1032Z.py:136](../../SiglentDevices/RIGOL_DG1032Z.py#L136)

Set channel amplitude

#### Arguments

- `ch` *int* - channel number, 1|2
- `amp` *float* - Vpp in volts

#### Signature

```python
def set_amp(self, ch=1, amp=0):
    ...
```

### DG1032Z.set_freq

[Show source in RIGOL_DG1032Z.py:148](../../SiglentDevices/RIGOL_DG1032Z.py#L148)

Set channel frequency in Hz

#### Arguments

- `ch` *int* - channel number, 1|2
- `freq` *float* - frequency in Hz

#### Signature

```python
def set_freq(self, ch=1, freq=1):
    ...
```

### DG1032Z.set_mod_am

[Show source in RIGOL_DG1032Z.py:182](../../SiglentDevices/RIGOL_DG1032Z.py#L182)

Set waveform modification for internal modulation

#### Arguments

- `ch` *int* - channel number 1|2
- `waveform` *str* - SINusoid|SQUare|TRIangle|RAMP|NRAMp|NOISe|USER
- `depth` *int* - percentage of amplitude variation [0, 120]
- `freq` *float* - frequency in Hz

#### Signature

```python
def set_mod_am(self, ch=1, waveform="SIN", depth=100, freq=1):
    ...
```

### DG1032Z.set_mod_am_state

[Show source in RIGOL_DG1032Z.py:203](../../SiglentDevices/RIGOL_DG1032Z.py#L203)

Get output modification state

#### Arguments

- `ch` *int* - channel number 1|2
- `state` *bool* - if True, turn mod on

#### Returns

None

#### Signature

```python
def set_mod_am_state(self, ch=1, state=False):
    ...
```

### DG1032Z.set_offset

[Show source in RIGOL_DG1032Z.py:160](../../SiglentDevices/RIGOL_DG1032Z.py#L160)

Set channel offset in volts

#### Arguments

- `ch` *int* - channel number, 1|2
- `offset` *float* - voltage in volts

#### Signature

```python
def set_offset(self, ch=1, offset=1):
    ...
```

### DG1032Z.set_state

[Show source in RIGOL_DG1032Z.py:172](../../SiglentDevices/RIGOL_DG1032Z.py#L172)

Turn channel on/off

#### Arguments

- `ch` *int* - channel number, 1|2
- `state` *bool* - if true, turn on channel output

#### Signature

```python
def set_state(self, ch=1, state=False):
    ...
```

### DG1032Z.set_wave

[Show source in RIGOL_DG1032Z.py:218](../../SiglentDevices/RIGOL_DG1032Z.py#L218)

Setup arbitrary waveforms

#### Arguments

- `ch` *int* - channel number, 1|2
- `waveform` *str* - one of SINusoid|SQUare|RAMP|PULSe|NOISe|USER|HARMonic|CUSTom|DC|KAISER|
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
- `freq` *float* - frequency in Hz. 1 uHz to 60 MHz
- `amp` *float* - Vpp in volts
- `offset` *float* - DC offset in volts
- `phase` *float* - phase in degrees. 0 to 360 deg

#### Signature

```python
def set_wave(self, ch=1, waveform="", freq=1000, amp=1, offset=0, phase=0):
    ...
```

### DG1032Z.set_wave_custom

[Show source in RIGOL_DG1032Z.py:271](../../SiglentDevices/RIGOL_DG1032Z.py#L271)

Send a custom waveform to the AWG

#### Arguments

- `ch` *int* - channel number, 1|2
- `voltages` *iterable* - list of voltages to set
- `period` *float* - duration of voltage sequence, assuming equally spaced points.

#### Signature

```python
def set_wave_custom(self, ch, voltages, period):
    ...
```

### DG1032Z.wait

[Show source in RIGOL_DG1032Z.py:316](../../SiglentDevices/RIGOL_DG1032Z.py#L316)

Wait until operation has completed. Block operation until completed

#### Signature

```python
def wait(self):
    ...
```

### DG1032Z.write

[Show source in RIGOL_DG1032Z.py:320](../../SiglentDevices/RIGOL_DG1032Z.py#L320)

Write string to device.

#### Arguments

block (bool, None): if true, block output until write is finished.
    if None, use self.block_until_finshed as default condition

remaining arguments passed to SiglentBase.write

#### Signature

```python
def write(self, block=None, *args, **kwargs):
    ...
```