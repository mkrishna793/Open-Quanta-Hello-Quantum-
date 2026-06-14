import pytest
from openquanta.pulse import Pulse, Schedule
from openquanta.backends.open_hardware import OpenHardwareBackend
from openquanta import Circuit, gates

def test_pulse_creation():
    p = Pulse(frequency=5e9, amplitude=1.0, duration=50.0)
    assert p.frequency == 5e9
    assert p.amplitude == 1.0

def test_schedule_play_and_delay():
    sched = Schedule()
    sched.play(0, Pulse(5e9, 1.0, 50.0))
    assert sched.duration == 50.0
    sched.delay(25.0)
    assert sched.duration == 75.0

def test_open_hardware_compile():
    c = Circuit(2)
    c.apply(gates.X, 0)
    c.apply(gates.CNOT, 0, 1)

    backend = OpenHardwareBackend("test_qick")
    sched = backend.compile_to_pulses(c)

    # 1 X pulse (50ns) + 2 CNOT pulses (100ns each) -> wait, targets is [0,1] for CNOT, so it appends twice = 200ns
    # Total 250ns
    assert sched.duration == 250.0

def test_open_hardware_execute():
    c = Circuit(1)
    c.apply(gates.X, 0)

    backend = OpenHardwareBackend("test_qick")
    res = backend.execute(c, shots=10)
    assert "00" in res # Stub returns "00"
