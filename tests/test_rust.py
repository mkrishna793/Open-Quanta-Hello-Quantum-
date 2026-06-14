import pytest
from openquanta import Circuit, gates
from openquanta.backends.rust_sim import RustBackend

def test_rust_simulator():
    backend = RustBackend()
    if not backend.available:
        pytest.skip("Rust simulator not compiled")

    c = Circuit(2)
    c.apply(gates.H, 0)
    c.apply(gates.CNOT, 0, 1)
    c.measure_all()

    res = backend.execute(c, shots=100)
    assert "00" in res or "11" in res
    assert "01" not in res
    assert "10" not in res

def test_rust_single_gates():
    backend = RustBackend()
    if not backend.available:
        pytest.skip("Rust simulator not compiled")

    c = Circuit(1)
    c.apply(gates.X, 0)
    c.measure(0, 0)
    res = backend.execute(c, shots=10)
    assert "1" in res
