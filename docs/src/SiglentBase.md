# Siglentbase

[Siglentdevices Index](../README.md#siglentdevices-index) /
[Src](./index.md#src) /
Siglentbase

> Auto-generated documentation for [src.SiglentBase](../../src/SiglentBase.py) module.

- [Siglentbase](#siglentbase)
  - [SiglentBase](#siglentbase-1)
    - [SiglentBase.close](#siglentbaseclose)
    - [SiglentBase.flush](#siglentbaseflush)
    - [SiglentBase.query](#siglentbasequery)
    - [SiglentBase.read](#siglentbaseread)
    - [SiglentBase.read\_bytes](#siglentbaseread_bytes)
    - [SiglentBase.read\_raw](#siglentbaseread_raw)
    - [SiglentBase.write](#siglentbasewrite)
    - [SiglentBase.write\_raw](#siglentbasewrite_raw)

## SiglentBase

[Show source in SiglentBase.py:10](../../src/SiglentBase.py#L10)

Control siglent digital device and send messages

#### Attributes

- `ADDRESS` *str* - format to connect to device

#### Signature

```python
class SiglentBase(object):
    def __init__(self, hostname):
        ...
```

### SiglentBase.close

[Show source in SiglentBase.py:38](../../src/SiglentBase.py#L38)

Close remote connection.

#### Signature

```python
def close(self):
    ...
```

### SiglentBase.flush

[Show source in SiglentBase.py:42](../../src/SiglentBase.py#L42)

Flush connection buffer.

#### Signature

```python
def flush(self):
    ...
```

### SiglentBase.query

[Show source in SiglentBase.py:64](../../src/SiglentBase.py#L64)

Push query to device, read back response.

Arguments passed to pyvisa.TCPIPInstrument.query

#### Signature

```python
def query(self, *args, **kwargs):
    ...
```

### SiglentBase.read

[Show source in SiglentBase.py:46](../../src/SiglentBase.py#L46)

Read from stream.

#### Signature

```python
def read(self, *args, **kwargs):
    ...
```

### SiglentBase.read_bytes

[Show source in SiglentBase.py:57](../../src/SiglentBase.py#L57)

Read raw bytes from stream.

Arguments passed to pyvisa.TCPIPInstrument.read_bytes

#### Signature

```python
def read_bytes(self, *args, **kwargs):
    ...
```

### SiglentBase.read_raw

[Show source in SiglentBase.py:50](../../src/SiglentBase.py#L50)

Read raw data from stream.

Arguments passed to pyvisa.TCPIPInstrument.read_raw

#### Signature

```python
def read_raw(self, *args, **kwargs):
    ...
```

### SiglentBase.write

[Show source in SiglentBase.py:71](../../src/SiglentBase.py#L71)

Write string to device.

Arguments passed to pyvisa.TCPIPInstrument.write

#### Signature

```python
def write(self, *args, **kwargs):
    ...
```

### SiglentBase.write_raw

[Show source in SiglentBase.py:78](../../src/SiglentBase.py#L78)

Write raw bytestring to device.

Arguments passed to pyvisa.TCPIPInstrument.write_raw

#### Signature

```python
def write_raw(self, *args, **kwargs):
    ...
```