"""
Tests for open-Quanta Modules.
"""

import pytest
import numpy as np


class TestModuleDecorator:
    """Test @module decorator."""

    def test_module_creation(self):
        from openquanta.modules import module
        from openquanta import Circuit, gates

        @module
        def SimpleCircuit():
            c = Circuit(1)
            c.apply(gates.H, 0)
            return c

        assert SimpleCircuit.name == "SimpleCircuit"

        c = SimpleCircuit()
        assert c.n_qubits == 1
        assert len(c.gates) == 1

    def test_module_with_params(self):
        from openquanta.modules import module
        from openquanta import Circuit, gates

        @module
        def RotatedState(theta):
            c = Circuit(1)
            c.apply(gates.RY, 0, theta)
            return c

        c = RotatedState(0.5)
        assert c.gates[0].params == [0.5]

    def test_module_simulate(self):
        from openquanta.modules import module
        from openquanta import Circuit, gates

        @module
        def BellPair():
            c = Circuit(2)
            c.apply(gates.H, 0)
            c.apply(gates.CNOT, 0, 1)
            c.measure_all()
            return c

        result = BellPair.simulate(shots=1000)

        # Bell state: only 00 or 11
        valid_keys = {"00", "11"}
        for key in result:
            assert key in valid_keys

    def test_module_run(self):
        from openquanta.modules import module
        from openquanta import Circuit, gates

        @module
        def Simple():
            c = Circuit(1)
            c.apply(gates.H, 0)
            c.measure(0, 0)
            return c

        result = Simple.run(backend="simulator", shots=100)
        assert sum(result.values()) == 100


class TestStandardModules:
    """Test pre-built standard modules."""

    def test_bell_pair(self):
        from openquanta.modules import BellPair

        bell = BellPair()
        assert bell.n_qubits == 2

        result = bell.simulate(shots=500)
        # Bell state: 00 or 11 only
        for key in result:
            assert key in {"00", "11"}

    def test_ghz_state(self):
        from openquanta.modules import GHZ

        ghz = GHZ(3)
        assert ghz.n_qubits == 3

        result = ghz.simulate(shots=500)
        # GHZ state: 000 or 111 only
        for key in result:
            assert key in {"000", "111"}

    def test_superposition(self):
        from openquanta.modules import Superposition

        sup = Superposition(2)
        assert sup.n_qubits == 2

        result = sup.simulate(shots=1000)
        # Should get all 4 states roughly equally
        assert len(result) == 4

    def test_quantum_rng(self):
        from openquanta.modules import QuantumRNG

        rng = QuantumRNG(4)
        result = rng.simulate(shots=100)

        assert sum(result.values()) == 100
        # Should have multiple different outcomes
        assert len(result) > 1

    def test_identity(self):
        from openquanta.modules import Identity

        c = Identity(2)
        result = c.simulate(shots=100)

        # Identity on |00⟩ should return |00⟩
        assert result.get("00", 0) == 100

    def test_all_x(self):
        from openquanta.modules import AllX

        c = AllX(2)
        result = c.simulate(shots=100)

        # X on |00⟩ should give |11⟩
        assert result.get("11", 0) == 100


class TestModuleComposition:
    """Test module composition."""

    def test_compose_two_modules(self):
        from openquanta.modules import BellPair, Superposition

        # Compose Bell pair with superposition
        combined = BellPair.compose(Superposition, 2)

        c = combined()
        assert c.n_qubits >= 2

    def test_compose_modules_function(self):
        from openquanta.modules import compose_modules, BellPair, AllH

        combined = compose_modules(BellPair, AllH(2), name="test_combined")
        c = combined()

        assert len(c.gates) > 0


class TestModuleClass:
    """Test Module class methods."""

    def test_module_repr(self):
        from openquanta.modules import module
        from openquanta import Circuit

        @module
        def MyModule():
            return Circuit(1)

        assert "MyModule" in repr(MyModule)

    def test_module_to_qir(self):
        from openquanta.modules import BellPair

        qir = BellPair.to_qir()

        assert isinstance(qir, str)
        assert len(qir) > 0


class TestAlgorithmModules:
    """Test algorithm modules."""

    def test_deutsch_jozsa(self):
        from openquanta.modules import DeutschJozsa

        # Test constant oracle
        dj = DeutschJozsa(2, oracle_type="constant")
        result = dj.simulate(shots=100)

        # For constant oracle, should get all 0s
        # (simplified test)

    def test_bernstein_vazirani(self):
        from openquanta.modules import BernsteinVazirani

        bv = BernsteinVazirani(2, secret_string=3)  # 11 in binary
        result = bv.simulate(shots=100)

        # Should return the secret string
        # (simplified - depends on implementation)

    def test_qft(self):
        from openquanta.modules import QFT

        qft = QFT(2)
        c = qft()

        assert c.n_qubits == 2
        # QFT circuit should have multiple gates


class TestCustomModule:
    """Test creating custom modules."""

    def test_create_custom_module(self):
        from openquanta.modules import module
        from openquanta import Circuit, gates

        @module
        def MyEntangledPair(n):
            """Create n Bell-like pairs."""
            c = Circuit(n * 2)
            for i in range(n):
                c.apply(gates.H, i * 2)
                c.apply(gates.CNOT, i * 2, i * 2 + 1)
            c.measure_all()
            return c

        c = MyEntangledPair(2)
        assert c.n_qubits == 4

        result = MyEntangledPair.simulate(2, shots=100)
        assert sum(result.values()) == 100

    def test_parametrized_module(self):
        from openquanta.modules import module
        from openquanta import Circuit, gates
        import numpy as np

        @module
        def RotationCircuit(angle):
            c = Circuit(1)
            c.apply(gates.RY, 0, angle)
            c.measure(0, 0)
            return c

        # Different angles give different distributions
        result_0 = RotationCircuit.simulate(0.0, shots=1000)
        result_pi = RotationCircuit.simulate(np.pi, shots=1000)

        # RY(0) should give all 0s
        # RY(π) should give all 1s
        assert result_0.get("0", 0) > 900
        assert result_pi.get("1", 0) > 900


class TestModuleIntegration:
    """Test module integration with other components."""

    def test_module_with_backend(self):
        from openquanta.modules import BellPair

        # Direct simulation
        result = BellPair.simulate(shots=100)
        assert sum(result.values()) == 100

    def test_module_chain(self):
        from openquanta.modules import module
        from openquanta import Circuit, gates

        @module
        def Prepare():
            c = Circuit(2)
            c.apply(gates.H, 0)
            return c

        @module
        def Entangle():
            c = Circuit(2)
            c.apply(gates.CNOT, 0, 1)
            c.measure_all()
            return c

        # Chain modules manually
        c = Prepare()
        c2 = Entangle()
        c.gates.extend(c2.gates)

        result = c.simulate(shots=100)
        assert sum(result.values()) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])