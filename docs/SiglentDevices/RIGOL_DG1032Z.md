# Rigol Dg1032z

[Siglentdevices Index](../README.md#siglentdevices-index) /
[Siglentdevices](./index.md#siglentdevices) /
Rigol Dg1032z

> Auto-generated documentation for [SiglentDevices.RIGOL_DG1032Z](../../SiglentDevices/RIGOL_DG1032Z.py) module.

- [Rigol Dg1032z](#rigol-dg1032z)
  - [DG1032Z](#dg1032z)
    - [DG1032Z.get\_ch\_state](#dg1032zget_ch_state)
    - [DG1032Z.get\_mod\_am\_state](#dg1032zget_mod_am_state)
    - [DG1032Z.get\_wave](#dg1032zget_wave)
    - [DG1032Z.set\_ch\_state](#dg1032zset_ch_state)
    - [DG1032Z.set\_mod\_am](#dg1032zset_mod_am)
    - [DG1032Z.set\_mod\_am\_state](#dg1032zset_mod_am_state)
    - [DG1032Z.set\_wave\_arb](#dg1032zset_wave_arb)
    - [DG1032Z.set\_wave\_dc](#dg1032zset_wave_dc)
    - [DG1032Z.set\_wave\_sin](#dg1032zset_wave_sin)
    - [DG1032Z.set\_wave\_square](#dg1032zset_wave_square)
    - [DG1032Z.set\_wave\_triangle](#dg1032zset_wave_triangle)
    - [DG1032Z.wait](#dg1032zwait)
    - [DG1032Z.write](#dg1032zwrite)

## DG1032Z

[Show source in RIGOL_DG1032Z.py:17](../../SiglentDevices/RIGOL_DG1032Z.py#L17)

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

[Show source in RIGOL_DG1032Z.py:49](../../SiglentDevices/RIGOL_DG1032Z.py#L49)

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

[Show source in RIGOL_DG1032Z.py:62](../../SiglentDevices/RIGOL_DG1032Z.py#L62)

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

[Show source in RIGOL_DG1032Z.py:73](../../SiglentDevices/RIGOL_DG1032Z.py#L73)

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

### DG1032Z.set_ch_state

[Show source in RIGOL_DG1032Z.py:117](../../SiglentDevices/RIGOL_DG1032Z.py#L117)

Turn channel on/off

#### Arguments

- `ch` *int* - channel number, 1|2
- `state` *bool* - if true, turn on channel output

#### Signature

```python
def set_ch_state(self, ch=1, state=False):
    ...
```

### DG1032Z.set_mod_am

[Show source in RIGOL_DG1032Z.py:127](../../SiglentDevices/RIGOL_DG1032Z.py#L127)

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

[Show source in RIGOL_DG1032Z.py:148](../../SiglentDevices/RIGOL_DG1032Z.py#L148)

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

### DG1032Z.set_wave_arb

[Show source in RIGOL_DG1032Z.py:163](../../SiglentDevices/RIGOL_DG1032Z.py#L163)

Setup arbitrary waveforms

#### Arguments

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
- `ch` *int* - channel number, 1|2
- `freq` *float* - frequency in Hz. 1 uHz to 60 MHz
- `amp` *float* - Vpp in volts
- `offset` *float* - DC offset in volts
- `phase` *float* - phase in degrees. 0 to 360 deg

#### Signature

```python
def set_wave_arb(self, waveform="", ch=1, freq=1000, amp=1, offset=0, phase=0):
    ...
```

### DG1032Z.set_wave_dc

[Show source in RIGOL_DG1032Z.py:203](../../SiglentDevices/RIGOL_DG1032Z.py#L203)

Set DC output

#### Arguments

- `ch` *int* - channel number, 1|2
- `offset` *float* - DC offset in volts

#### Signature

```python
def set_wave_dc(self, ch=1, offset=0):
    ...
```

### DG1032Z.set_wave_sin

[Show source in RIGOL_DG1032Z.py:213](../../SiglentDevices/RIGOL_DG1032Z.py#L213)

Set AWG to produce a sine wave

#### Arguments

- `ch` *int* - channel number, 1|2
- `freq` *float* - frequency in Hz. 1 uHz to 60 MHz
- `amp` *float* - Vpp in volts
- `offset` *float* - DC offset in volts
- `phase` *float* - phase in degrees. 0 to 360 deg

#### Signature

```python
def set_wave_sin(self, ch=1, freq=1000, amp=5, offset=0, phase=0):
    ...
```

### DG1032Z.set_wave_square

[Show source in RIGOL_DG1032Z.py:225](../../SiglentDevices/RIGOL_DG1032Z.py#L225)

Set AWG to produce a square wave

#### Arguments

- `ch` *int* - channel number, 1|2
- `freq` *float* - frequency in Hz. 1 uHz to 60 MHz
- `amp` *float* - Vpp in volts
- `offset` *float* - DC offset in volts
- `phase` *float* - phase in degrees. 0 to 360 deg

#### Signature

```python
def set_wave_square(self, ch=1, freq=1000, amp=5, offset=0, phase=0):
    ...
```

### DG1032Z.set_wave_triangle

[Show source in RIGOL_DG1032Z.py:237](../../SiglentDevices/RIGOL_DG1032Z.py#L237)

Set AWG to produce a triangle wave

#### Arguments

- `ch` *int* - channel number, 1|2
- `freq` *float* - frequency in Hz. 1 uHz to 60 MHz
- `amp` *float* - Vpp in volts
- `offset` *float* - DC offset in volts
- `phase` *float* - phase in degrees. 0 to 360 deg

#### Signature

```python
def set_wave_triangle(self, ch=1, freq=1000, amp=5, offset=0, phase=0):
    ...
```

### DG1032Z.wait

[Show source in RIGOL_DG1032Z.py:249](../../SiglentDevices/RIGOL_DG1032Z.py#L249)

Wait until operation has completed. Block operation until completed

#### Signature

```python
def wait(self):
    ...
```

### DG1032Z.write

[Show source in RIGOL_DG1032Z.py:253](../../SiglentDevices/RIGOL_DG1032Z.py#L253)

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