# Rigol Dg1032z

[Siglentdevices Index](../README.md#siglentdevices-index) /
[Src](./index.md#src) /
Rigol Dg1032z

> Auto-generated documentation for [src.RIGOL_DG1032Z](../../src/RIGOL_DG1032Z.py) module.

- [Rigol Dg1032z](#rigol-dg1032z)
  - [DG1032Z](#dg1032z)
    - [DG1032Z().get_ch_state](#dg1032z()get_ch_state)
    - [DG1032Z().get_wave](#dg1032z()get_wave)
    - [DG1032Z().set_ch_state](#dg1032z()set_ch_state)
    - [DG1032Z().set_wave_sin](#dg1032z()set_wave_sin)
    - [DG1032Z().set_wave_square](#dg1032z()set_wave_square)
    - [DG1032Z().set_wave_triangle](#dg1032z()set_wave_triangle)

## DG1032Z

[Show source in RIGOL_DG1032Z.py:17](../../src/RIGOL_DG1032Z.py#L17)

Control RIGOL function generator

#### Signature

```python
class DG1032Z(SiglentBase):
    def __init__(self, hostname="tucan-awg01.triumf.ca"):
        ...
```

### DG1032Z().get_ch_state

[Show source in RIGOL_DG1032Z.py:45](../../src/RIGOL_DG1032Z.py#L45)

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

### DG1032Z().get_wave

[Show source in RIGOL_DG1032Z.py:58](../../src/RIGOL_DG1032Z.py#L58)

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

### DG1032Z().set_ch_state

[Show source in RIGOL_DG1032Z.py:102](../../src/RIGOL_DG1032Z.py#L102)

Turn channel on/off

#### Arguments

- `ch` *int* - channel number, 1|2
- `state` *bool* - if true, turn on channel output

#### Signature

```python
def set_ch_state(self, ch=1, state=False):
    ...
```

### DG1032Z().set_wave_sin

[Show source in RIGOL_DG1032Z.py:112](../../src/RIGOL_DG1032Z.py#L112)

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

### DG1032Z().set_wave_square

[Show source in RIGOL_DG1032Z.py:124](../../src/RIGOL_DG1032Z.py#L124)

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

### DG1032Z().set_wave_triangle

[Show source in RIGOL_DG1032Z.py:136](../../src/RIGOL_DG1032Z.py#L136)

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