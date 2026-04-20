"""
Tests for open-Quanta Backends.
"""

import pytest
import numpy as np


class TestSimulatorBackend:
    """Test local simulator backend."""

    def test_backend_availability(self):
        from openquanta.backends import SimulatorBackend

        sim = SimulatorBackend()
        assert sim.available

    def test_max_qubits(self):
        from openquanta.backends import SimulatorBackend

        sim = SimulatorBackend()
        assert sim.max_qubits > 0

    def test_simple_simulation(self):
        from openquanta import Circuit, gates
        from openquanta.backends import SimulatorBackend

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)
        c.measure_all()

        sim = SimulatorBackend()
        result = sim.execute(c, shots=1000)

        # Bell state should only give 00 or 11
        assert "00" in result or "11" in result
        assert sum(result.values()) == 1000

    def test_superposition_simulation(self):
        from openquanta import Circuit, gates
        from openquanta.backends import SimulatorBackend

        c = Circuit(1)
        c.apply(gates.H, 0)
        c.measure(0, 0)

        sim = SimulatorBackend()
        result = sim.execute(c, shots=1000)

        # Superposition should give both 0 and 1
        assert "0" in result
        assert "1" in result
        assert sum(result.values()) == 1000

    def test_x_gate_simulation(self):
        from openquanta import Circuit, gates
        from openquanta.backends import SimulatorBackend

        c = Circuit(1)
        c.apply(gates.X, 0)
        c.measure(0, 0)

        sim = SimulatorBackend()
        result = sim.execute(c, shots=100)

        # X gate flips |0⟩ to |1⟩
        assert result.get("1", 0) == 100

    def test_multi_qubit_simulation(self):
        from openquanta import Circuit, gates
        from openquanta.backends import SimulatorBackend

        c = Circuit(3)
        for i in range(3):
            c.apply(gates.H, i)
        c.measure_all()

        sim = SimulatorBackend()
        result = sim.execute(c, shots=1000)

        # Should get roughly equal distribution
        assert len(result) >= 2  # At least some different outcomes
        assert sum(result.values()) == 1000

    def test_rotation_gate_simulation(self):
        from openquanta import Circuit, gates
        from openquanta.backends import SimulatorBackend

        c = Circuit(1)
        c.apply(gates.RY, 0, np.pi / 2)  # Should give 50/50
        c.measure(0, 0)

        sim = SimulatorBackend()
        result = sim.execute(c, shots=1000)

        # RY(π/2) should create superposition
        assert "0" in result
        assert "1" in result


class TestCircuitSimulate:
    """Test circuit.simulate() method."""

    def test_simulate_bell_state(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)
        c.measure_all()

        result = c.simulate(shots=500)

        # Bell state: only 00 or 11
        valid_keys = {"00", "11"}
        for key in result:
            assert key in valid_keys

    def test_simulate_with_different_shots(self):
        from openquanta import Circuit, gates

        c = Circuit(1)
        c.apply(gates.H, 0)
        c.measure(0, 0)

        result1 = c.simulate(shots=100)
        result2 = c.simulate(shots=1000)

        assert sum(result1.values()) == 100
        assert sum(result2.values()) == 1000


class TestCircuitRun:
    """Test circuit.run() method."""

    def test_run_simulator(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)
        c.measure_all()

        result = c.run(backend="simulator", shots=500)

        assert sum(result.values()) == 500

    def test_invalid_backend(self):
        from openquanta import Circuit, gates

        c = Circuit(1)
        c.apply(gates.H, 0)
        c.measure(0, 0)

        with pytest.raises(ValueError):
            c.run(backend="invalid_backend")


class TestStatevector:
    """Test statevector functionality."""

    def test_get_statevector(self):
        from openquanta import Circuit, gates
        from openquanta.backends import SimulatorBackend

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)

        sim = SimulatorBackend()
        sv = sim.get_statevector(c)

        assert len(sv) == 4  # 2 qubits = 4 states
        # Bell state: |00⟩ + |11⟩ normalized
        assert np.isclose(np.abs(sv[0]), 1/np.sqrt(2))
        assert np.isclose(np.abs(sv[3]), 1/np.sqrt(2))


class TestBackendValidation:
    """Test backend validation."""

    def test_circuit_too_many_qubits(self):
        from openquanta import Circuit, gates
        from openquanta.backends import SimulatorBackend

        c = Circuit(100)  # Might exceed simulator limits
        # This should not raise during creation
        # Validation happens during execution

    def test_empty_circuit(self):
        from openquanta import Circuit
        from openquanta.backends import SimulatorBackend

        c = Circuit(2)
        # No gates, no measurements
        # Should still work (just returns nothing useful)

        sim = SimulatorBackend()
        result = sim.execute(c, shots=100)

        # Result depends on Qiskit behavior


if __name__ == "__main__":
    pytest.main([__file__, "-v"])