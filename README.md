# SiglentDevices
API for interfacing with various Siglent devices using SCPI commands

## Usage

### Install and import

To install clone this directory then execute the following: 

```
cd SiglentDevices
pip install --user .
```

Notes: 
* `user` should be typed in verbatim, it is not your username
* don't forget the `.` at the end

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

* [Siglent Device Base Class](docs/SiglentDevices/SiglenBase.md)
* [Digital Oscilloscpe SDS5034](docs/SiglentDevices/SDS5034.md)
* [Programmable DC Power Supply SPD3303](docs/SiglentDevices/SPD3303.md)
* [RIGOL Arbitrary Waveform Generator DG1032Z](docs/SiglentDevices/RIGOL_DG1032Z.md)


## Developer Notes

* Regenerate documentation with [`handsdown`](https://github.com/vemel/handsdown). Replace all `()` with nothing to fix markdown links
