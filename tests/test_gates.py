"""
Tests for open-Quanta Gates Module.
"""

import pytest
import numpy as np


class TestGateBasics:
    """Test basic gate functionality."""

    def test_gate_creation(self):
        """Test that gates can be created."""
        from openquanta.gates import Gate

        gate = Gate("H", targets=[0])
        assert gate.name == "H"
        assert gate.targets == [0]
        assert gate.params == []

    def test_gate_with_params(self):
        """Test parametric gates."""
        from openquanta.gates import Gate

        gate = Gate("RX", targets=[0], params=[0.5])
        assert gate.name == "RX"
        assert gate.params == [0.5]
        assert gate.is_parametric()

    def test_gate_copy(self):
        """Test gate copying."""
        from openquanta.gates import Gate

        gate = Gate("CNOT", targets=[0, 1])
        copy = gate.copy()

        assert copy.name == gate.name
        assert copy.targets == gate.targets
        assert copy is not gate


class TestSingleQubitGates:
    """Test single-qubit gate functions."""

    def test_h_gate(self):
        from openquanta.gates import H

        gate = H(0)
        assert gate.name == "H"
        assert gate.targets == [0]
        assert not gate.is_parametric()

    def test_x_gate(self):
        from openquanta.gates import X

        gate = X(0)
        assert gate.name == "X"

    def test_y_gate(self):
        from openquanta.gates import Y

        gate = Y(0)
        assert gate.name == "Y"

    def test_z_gate(self):
        from openquanta.gates import Z

        gate = Z(0)
        assert gate.name == "Z"

    def test_s_gate(self):
        from openquanta.gates import S, Sdg

        gate = S(0)
        assert gate.name == "S"

        gate = Sdg(0)
        assert gate.name == "Sdg"

    def test_t_gate(self):
        from openquanta.gates import T, Tdg

        gate = T(0)
        assert gate.name == "T"

        gate = Tdg(0)
        assert gate.name == "Tdg"


class TestRotationGates:
    """Test rotation gates with parameters."""

    def test_rx_gate(self):
        from openquanta.gates import RX

        gate = RX(0, 0.5)
        assert gate.name == "RX"
        assert gate.params == [0.5]
        assert gate.is_parametric()

    def test_ry_gate(self):
        from openquanta.gates import RY

        gate = RY(0, np.pi / 4)
        assert gate.params == [np.pi / 4]

    def test_rz_gate(self):
        from openquanta.gates import RZ

        gate = RZ(0, 1.0)
        assert gate.name == "RZ"

    def test_u3_gate(self):
        from openquanta.gates import U3

        gate = U3(0, 0.5, 0.3, 0.1)
        assert gate.params == [0.5, 0.3, 0.1]


class TestTwoQubitGates:
    """Test two-qubit gates."""

    def test_cnot_gate(self):
        from openquanta.gates import CNOT

        gate = CNOT(0, 1)
        assert gate.name == "CNOT"
        assert gate.targets == [0, 1]
        assert gate.num_qubits() == 2

    def test_cx_alias(self):
        from openquanta.gates import CX

        gate = CX(0, 1)
        assert gate.name == "CNOT"

    def test_cz_gate(self):
        from openquanta.gates import CZ

        gate = CZ(0, 1)
        assert gate.name == "CZ"

    def test_swap_gate(self):
        from openquanta.gates import SWAP

        gate = SWAP(0, 1)
        assert gate.name == "SWAP"


class TestMultiQubitGates:
    """Test multi-qubit gates."""

    def test_ccx_gate(self):
        from openquanta.gates import CCX

        gate = CCX(0, 1, 2)
        assert gate.name == "CCX"
        assert gate.targets == [0, 1, 2]
        assert gate.num_qubits() == 3

    def test_toffoli_alias(self):
        from openquanta.gates import Toffoli

        gate = Toffoli(0, 1, 2)
        assert gate.name == "CCX"

    def test_mcx_gate(self):
        from openquanta.gates import MCX

        gate = MCX([0, 1, 2], 3)
        assert gate.name == "MCX"
        assert gate.num_qubits() == 4


class TestMeasurement:
    """Test measurement gates."""

    def test_measure_gate(self):
        from openquanta.gates import Measure

        gate = Measure(0, 0)
        assert gate.name == "Measure"
        assert gate.targets == [0]
        assert gate.params == [0]

    def test_measure_all(self):
        from openquanta.gates import MeasureAll

        gate = MeasureAll()
        assert gate.name == "MeasureAll"


class TestCustomGate:
    """Test custom gate creation."""

    def test_custom_gate_creation(self):
        from openquanta.gates import CustomGate

        # X gate as custom
        matrix = np.array([[0, 1], [1, 0]], dtype=complex)
        gate = CustomGate("MyX", [0], matrix)

        assert gate.name == "MyX"
        assert gate.is_custom()
        assert np.allclose(gate.matrix, matrix)

    def test_custom_gate_validation(self):
        from openquanta.gates import CustomGate

        # Non-unitary matrix should fail
        bad_matrix = np.array([[1, 2], [3, 4]], dtype=complex)

        with pytest.raises(ValueError):
            CustomGate("BadGate", [0], bad_matrix)

    def test_custom_gate_factory(self):
        from openquanta.gates import custom_gate

        # Create factory function
        @custom_gate("MyH", np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2))
        def my_h(qubit):
            return [qubit]

        gate = my_h(0)
        assert gate.name == "MyH"
        assert gate.targets == [0]


class TestControlledGate:
    """Test controlled gate generation."""

    def test_controlled_h(self):
        from openquanta.gates import H, controlled

        h = H(1)
        ch = controlled(h, control=0)

        assert ch.name == "CH"
        assert 0 in ch.targets


class TestStandardMatrices:
    """Test standard gate matrices."""

    def test_get_matrix(self):
        from openquanta.gates import get_matrix, STANDARD_MATRICES
        import numpy as np

        h_matrix = get_matrix("H")
        assert h_matrix is not None
        assert h_matrix.shape == (2, 2)

        # Verify H is unitary
        identity = h_matrix.conj().T @ h_matrix
        assert np.allclose(identity, np.eye(2))

    def test_cnot_matrix(self):
        from openquanta.gates import get_matrix
        import numpy as np

        cnot = get_matrix("CNOT")
        assert cnot.shape == (4, 4)
        assert np.allclose(cnot @ cnot, np.eye(4))  # CNOT is self-inverse


class TestGateHelpers:
    """Test gate helper functions."""

    def test_is_single_qubit(self):
        from openquanta.gates import H, is_single_qubit

        gate = H(0)
        assert is_single_qubit(gate)

    def test_is_two_qubit(self):
        from openquanta.gates import CNOT, is_two_qubit

        gate = CNOT(0, 1)
        assert is_two_qubit(gate)

    def test_is_measurement(self):
        from openquanta.gates import Measure, is_measurement

        gate = Measure(0, 0)
        assert is_measurement(gate)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])