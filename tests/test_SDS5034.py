# Test basic functionality of SDS5034
# Derek Fujimoto
# Apr 2023

from SiglentDevices import SDS5034
from functools import partial

# connect to device
s = SDS5034('tucan-scope1.triumf.ca')

# testing basic set and queries
def _test_get_set(fn_str, val_list, ch=-1):
    """
        Test by setting a value and getting a value
    """

    # get functions
    fn_get_orig = getattr(s, f'get_{fn_str}')
    fn_set_orig = getattr(s, f'set_{fn_str}')

    if ch > 0:
        fn_get = lambda : fn_get_orig(ch)
        fn_set = lambda val: fn_set_orig(ch, val)
    else:
        fn_get = fn_get_orig
        fn_set = fn_set_orig

    # get initial 
    init = fn_get()

    # set values
    for val in val_list:
        fn_set(val,)
        assert fn_get() == val, f'{fn_str} set or read failed'

    # reset 
    fn_set(init)

def test_adc_resolution():
    _test_get_set('adc_resolution', [8, 10])

def test_ch_coupling():
    _test_get_set('ch_coupling', ('DC', 'AC', 'GND'), ch=1)

def test_ch_impedance():
    _test_get_set('ch_impedance', ('1M', '50'), ch=1)

def test_ch_offset():
    _test_get_set('ch_offset', (1, -0.001, 0.25, 0), ch=1)

# def test_ch_probe():
#     _test_get_set('ch_probe', (3, 0.01, None), ch=1)

def test_ch_scale():
    _test_get_set('ch_scale', (3, 0.01, 1), ch=1)

def test_ch_state():
    _test_get_set('ch_state', (False, True), ch=1)

def test_run_state():
    _test_get_set('run_state', (True, False))

def test_sequence():
    _test_get_set('sequence', (True, False))

def test_sequence_count():
    s.set_sequence(True)
    _test_get_set('sequence_count', (4, 16, 2))
    s.set_sequence(False)

def test_smpl_rate():
    _test_get_set('smpl_rate', (1e3, 1e6, 5e4))
    s.set_smpl_rate('auto')

def test_time_delay():
    _test_get_set('time_delay', (1e-6, 1.34e-6, 5e-6, 0))

def test_time_scale():
    _test_get_set('time_scale', (1e-3, 500e-6, 1e-2))

def test_trig_mode():
    _test_get_set('trig_mode', ('single', 'auto', 'normal'))

def test_wave_ch():
    _test_get_set('wave_ch', (1, 2, 3))

def test_wave_startpt():
    _test_get_set('wave_startpt', (1, 2, 3))

def test_wave_interval():
    _test_get_set('wave_interval', (1, 2, 3))

def test_wave_npts():
    _test_get_set('wave_npts', (6.25e6, 1e6, 1e4))

def test_wave_width():
    _test_get_set('wave_width', ('byte', 'word'))



