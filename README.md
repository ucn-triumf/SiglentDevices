# SiglentDevices
API for interfacing with various Siglent devices using SCPI commands

## Usage

### Install and import

To "install" clone this directory onto your PYTHONPATH. 

Dependencies: 

* `matplotlib`
* `pyvisa`
* `numpy`

Import as

```python
import SiglentDevices
```

Run functionality tests with `pytest`

### Example Digital Oscilloscpe SDS5034

```python
from SiglentDevices import SDS5034
import matplotlib.pyplot as plt

# connect to device
sds = SDS5034('tucan-scope1.triumf.ca')

# switch scope into run state
sds.run()

# switch scope into stop state (no longer takes data)
sds.stop()

# read waveform ch1
volts = sds.read_wave_ch(1)
```
---

## Device List

* [Digital Oscilloscpe SDS5034](doc/SDS5034_doc.md)