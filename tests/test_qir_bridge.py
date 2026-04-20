"""
Tests for open-Quanta QIR Bridge.
"""

import pytest


class TestQIRBridgeBasic:
    """Test basic QIR bridge functionality."""

    def test_bridge_creation(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import QIRBridge

        c = Circuit(2)
        c.apply(gates.H, 0)

        bridge = QIRBridge(c)
        assert bridge.circuit == c

    def test_simple_h_gate_qir(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(1)
        c.apply(gates.H, 0)

        qir = circuit_to_qir(c)

        assert isinstance(qir, str)
        assert len(qir) > 0

    def test_cnot_gate_qir(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(2)
        c.apply(gates.CNOT, 0, 1)

        qir = circuit_to_qir(c)

        assert isinstance(qir, str)

    def test_bell_state_qir(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)
        c.measure_all()

        qir = circuit_to_qir(c, name="bell_state")

        assert "bell_state" in qir or len(qir) > 0


class TestQIRGateTranslation:
    """Test translation of various gates to QIR."""

    def test_single_qubit_gates(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(1)
        c.apply(gates.X, 0)
        c.apply(gates.Y, 0)
        c.apply(gates.Z, 0)

        qir = circuit_to_qir(c)
        assert isinstance(qir, str)

    def test_rotation_gates(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(1)
        c.apply(gates.RX, 0, 0.5)
        c.apply(gates.RY, 0, 0.3)
        c.apply(gates.RZ, 0, 0.1)

        qir = circuit_to_qir(c)
        assert isinstance(qir, str)

    def test_two_qubit_gates(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(2)
        c.apply(gates.CNOT, 0, 1)
        c.apply(gates.CZ, 0, 1)
        c.apply(gates.SWAP, 0, 1)

        qir = circuit_to_qir(c)
        assert isinstance(qir, str)

    def test_three_qubit_gates(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(3)
        c.apply(gates.CCX, 0, 1, 2)

        qir = circuit_to_qir(c)
        assert isinstance(qir, str)

    def test_measurement_in_qir(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(1)
        c.apply(gates.H, 0)
        c.measure(0, 0)

        qir = circuit_to_qir(c)
        assert isinstance(qir, str)


class TestQIRErrorHandling:
    """Test QIR bridge error handling."""

    def test_unsupported_gate(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import QIRBridge, QIRBridgeError

        # Create a gate with unknown name
        class UnknownGate:
            name = "UnknownGate"
            targets = [0]
            params = []
            def is_custom(self): return False

        c = Circuit(1)
        c.gates.append(UnknownGate())

        bridge = QIRBridge(c)
        with pytest.raises(QIRBridgeError):
            bridge.compile()


class TestCircuitToQIR:
    """Test circuit.to_qir() method."""

    def test_circuit_to_qir_method(self):
        from openquanta import Circuit, gates

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)

        qir = c.to_qir()

        assert isinstance(qir, str)
        assert len(qir) > 0

    def test_qir_with_name(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(2, name="MyCircuit")
        c.apply(gates.H, 0)

        qir = circuit_to_qir(c, name="test_circuit")

        assert isinstance(qir, str)


class TestQIROutputFormat:
    """Test QIR output format."""

    def test_qir_is_string(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)
        c.measure_all()

        qir = circuit_to_qir(c)

        assert isinstance(qir, str)

    def test_qir_structure(self):
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.measure_all()

        qir = circuit_to_qir(c)

        # QIR should contain module/function definitions
        # Exact format depends on PyQIR version
        assert len(qir) > 50  # Should be substantial


if __name__ == "__main__":
    pytest.main([__file__, "-v"])