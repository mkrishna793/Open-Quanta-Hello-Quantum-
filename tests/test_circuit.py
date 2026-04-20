"""
Tests for open-Quanta Circuit Module.
"""

import pytest
import numpy as np


class TestCircuitCreation:
    """Test circuit initialization."""

    def test_basic_creation(self):
        from openquanta import Circuit

        c = Circuit(2)
        assert c.n_qubits == 2
        assert c.n_bits == 2
        assert c.size == 0
        assert c.gates == []

    def test_creation_with_bits(self):
        from openquanta import Circuit

        c = Circuit(2, n_bits=3)
        assert c.n_qubits == 2
        assert c.n_bits == 3

    def test_creation_with_name(self):
        from openquanta import Circuit

        c = Circuit(2, name="TestCircuit")
        assert c.name == "TestCircuit"

    def test_invalid_qubit_count(self):
        from openquanta import Circuit

        with pytest.raises(ValueError):
            Circuit(0)

        with pytest.raises(ValueError):
            Circuit(-1)

    def test_quantum_circuit_alias(self):
        from openquanta import QuantumCircuit

        c = QuantumCircuit(2)
        assert c.n_qubits == 2


class TestGateApplication:
    """Test applying gates to circuits."""

    def test_apply_single_gate(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)

        assert len(c.gates) == 1
        assert c.gates[0].name == "H"

    def test_apply_multiple_gates(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)

        assert len(c.gates) == 2
        assert c.gates[0].name == "H"
        assert c.gates[1].name == "CNOT"

    def test_apply_gate_object(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        gate = gates.H(0)
        c.apply(gate)

        assert len(c.gates) == 1

    def test_apply_gate_by_name(self):
        from openquanta import Circuit

        c = Circuit(2)
        c.apply("H", 0)

        assert c.gates[0].name == "H"

    def test_chaining(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0).apply(gates.CNOT, 0, 1).measure_all()

        assert len(c.gates) == 4  # H, CNOT, 2 measures

    def test_invalid_qubit_index(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        with pytest.raises(Exception):  # QubitError
            c.apply(gates.H, 5)


class TestConvenienceMethods:
    """Test convenience methods for common gates."""

    def test_h_method(self):
        from openquanta import Circuit

        c = Circuit(2)
        c.h(0)

        assert c.gates[0].name == "H"

    def test_cnot_method(self):
        from openquanta import Circuit

        c = Circuit(2)
        c.cx(0, 1)

        assert c.gates[0].name == "CNOT"

    def test_rotation_methods(self):
        from openquanta import Circuit

        c = Circuit(1)
        c.rx(0, 0.5)
        c.ry(0, 0.3)
        c.rz(0, 0.1)

        assert len(c.gates) == 3
        assert c.gates[0].params == [0.5]

    def test_toffoli_method(self):
        from openquanta import Circuit

        c = Circuit(3)
        c.toffoli(0, 1, 2)

        assert c.gates[0].name == "CCX"


class TestMeasurement:
    """Test measurement functionality."""

    def test_single_measurement(self):
        from openquanta import Circuit

        c = Circuit(2)
        c.measure(0, 0)

        assert len(c.gates) == 1
        assert c.gates[0].name == "Measure"

    def test_measure_all(self):
        from openquanta import Circuit

        c = Circuit(2)
        c.measure_all()

        assert c.num_measurements == 2
        assert len([g for g in c.gates if g.name == "Measure"]) == 2

    def test_measure_range(self):
        from openquanta import Circuit

        c = Circuit(3)
        c.measure_range([0, 1], [0, 1])

        assert c.num_measurements == 2


class TestCircuitProperties:
    """Test circuit properties."""

    def test_size(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)

        assert c.size == 2

    def test_depth(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.H, 1)

        # Two gates on different qubits = depth 1
        assert c.depth == 1

        c.apply(gates.CNOT, 0, 1)
        # Now depth increases
        assert c.depth == 2

    def test_count_gates(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.H, 1)
        c.apply(gates.CNOT, 0, 1)

        assert c.count_gates("H") == 2
        assert c.count_gates("CNOT") == 1
        assert c.count_gates() == 3


class TestCircuitManipulation:
    """Test circuit manipulation methods."""

    def test_copy(self):
        from openquanta import Circuit, gates

        c1 = Circuit(2)
        c1.apply(gates.H, 0)

        c2 = c1.copy()

        assert c2.n_qubits == c1.n_qubits
        assert len(c2.gates) == len(c1.gates)
        assert c2 is not c1

    def test_append(self):
        from openquanta import Circuit, gates

        c1 = Circuit(2)
        c1.apply(gates.H, 0)

        c2 = Circuit(2)
        c2.apply(gates.X, 1)

        c1.append(c2)

        assert len(c1.gates) == 2

    def test_insert(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.X, 1)

        c.insert(1, gates.Y(0))

        assert c.gates[1].name == "Y"

    def test_remove(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.X, 1)

        c.remove(0)

        assert len(c.gates) == 1
        assert c.gates[0].name == "X"


class TestCircuitOperations:
    """Test circuit operations like inverse, power."""

    def test_inverse(self):
        from openquanta import Circuit, gates

        c = Circuit(1)
        c.apply(gates.H, 0)
        c.apply(gates.S, 0)

        inv = c.inverse()

        # Inverse should have gates in reverse order
        assert inv.gates[0].name == "Sdg"
        assert inv.gates[1].name == "H"

    def test_power(self):
        from openquanta import Circuit, gates

        c = Circuit(1)
        c.apply(gates.X, 0)

        c2 = c.power(3)

        assert len(c2.gates) == 3


class TestCircuitOperators:
    """Test circuit operators."""

    def test_addition(self):
        from openquanta import Circuit, gates

        c1 = Circuit(2)
        c1.apply(gates.H, 0)

        c2 = Circuit(2)
        c2.apply(gates.X, 1)

        c3 = c1 + c2

        assert len(c3.gates) == 2

    def test_iadd(self):
        from openquanta import Circuit, gates

        c1 = Circuit(2)
        c1.apply(gates.H, 0)

        c2 = Circuit(2)
        c2.apply(gates.X, 1)

        c1 += c2

        assert len(c1.gates) == 2

    def test_iteration(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)

        gate_names = [g.name for g in c]
        assert gate_names == ["H", "CNOT"]

    def test_indexing(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)

        assert c[0].name == "H"
        assert c[1].name == "CNOT"


class TestCircuitVisualization:
    """Test circuit drawing."""

    def test_draw_text(self):
        from openquanta import Circuit, gates

        c = Circuit(2, name="Test")
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)

        output = c.draw("text")

        assert isinstance(output, str)
        assert "Test" in output or "Qubits" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])