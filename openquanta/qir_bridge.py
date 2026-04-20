"""
QIR Bridge - Translates open-Quanta Circuits to QIR code.

This module converts Circuit objects into Quantum Intermediate
Representation (QIR) using PyQIR from Microsoft.

QIR is an industry-standard intermediate representation for quantum
programs, supported by IBM, Microsoft, Quantinuum, and others.
"""

from typing import Optional
import numpy as np

from .circuit import Circuit


class QIRBridgeError(Exception):
    """Raised when QIR generation fails."""
    pass


class QIRBridge:
    """
    Translates open-Quanta Circuit to QIR code.

    This class handles the conversion of our Circuit representation
    into QIR (Quantum Intermediate Representation) code using PyQIR.

    Example:
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import QIRBridge

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)

        bridge = QIRBridge(c)
        qir_code = bridge.compile()
    """

    def __init__(self, circuit: Circuit, name: Optional[str] = None):
        """
        Initialize the QIR bridge.

        Args:
            circuit: The Circuit to convert
            name: Optional name for the QIR module
        """
        self.circuit = circuit
        self.name = name or circuit.name or "circuit"
        self._module = None
        self._builder = None
        self._qubits = None
        self._results = None

    def compile(self) -> str:
        """
        Compile the circuit to QIR code.

        Returns:
            QIR code as a string

        Raises:
            QIRBridgeError: If compilation fails
        """
        try:
            import pyqir
        except ImportError:
            raise QIRBridgeError(
                "PyQIR not installed. Install with: pip install pyqir"
            )

        try:
            # Create PyQIR module
            self._module = pyqir.SimpleModule(
                self.name,
                num_qubits=self.circuit.n_qubits,
                num_results=self.circuit.n_bits
            )
            self._builder = self._module.builder
            self._qubits = self._module.qubits
            self._results = self._module.results
            self._qis = pyqir.qis

            # Apply each gate
            for gate in self.circuit.gates:
                self._apply_gate(gate)

            # Return QIR code
            return self._module.ir()

        except Exception as e:
            raise QIRBridgeError(f"QIR compilation failed: {e}") from e

    def _apply_gate(self, gate) -> None:
        """
        Apply a single gate to the QIR module.

        Args:
            gate: Gate object to apply
        """
        name = gate.name
        targets = gate.targets
        params = gate.params if hasattr(gate, 'params') else []
        qis = self._qis
        b = self._builder
        q = self._qubits
        r = self._results

        # Single-qubit gates
        if name == "I":
            pass  # Identity - do nothing

        elif name == "H":
            qis.h(b, q[targets[0]])

        elif name == "X":
            qis.x(b, q[targets[0]])

        elif name == "Y":
            qis.y(b, q[targets[0]])

        elif name == "Z":
            qis.z(b, q[targets[0]])

        elif name == "S":
            qis.s(b, q[targets[0]])

        elif name == "Sdg":
            qis.s_adj(b, q[targets[0]])

        elif name == "T":
            qis.t(b, q[targets[0]])

        elif name == "Tdg":
            qis.t_adj(b, q[targets[0]])

        # Rotation gates
        elif name == "RX":
            qis.rx(b, params[0], q[targets[0]])

        elif name == "RY":
            qis.ry(b, params[0], q[targets[0]])

        elif name == "RZ":
            qis.rz(b, params[0], q[targets[0]])

        elif name == "Phase":
            qis.rz(b, params[0], q[targets[0]])

        elif name in ("U", "U3"):
            theta, phi, lam = params
            qis.rz(b, lam, q[targets[0]])
            qis.ry(b, theta, q[targets[0]])
            qis.rz(b, phi, q[targets[0]])

        elif name == "U1":
            qis.rz(b, params[0], q[targets[0]])

        elif name == "U2":
            phi, lam = params
            qis.rz(b, lam, q[targets[0]])
            qis.ry(b, np.pi / 2, q[targets[0]])
            qis.rz(b, phi, q[targets[0]])

        # Two-qubit gates
        elif name in ("CNOT", "CX"):
            qis.cx(b, q[targets[0]], q[targets[1]])

        elif name == "CZ":
            qis.cz(b, q[targets[0]], q[targets[1]])

        elif name == "SWAP":
            qis.swap(b, q[targets[0]], q[targets[1]])

        # Three-qubit gates
        elif name in ("CCX", "Toffoli"):
            qis.ccx(b, q[targets[0]], q[targets[1]], q[targets[2]])

        # Measurement
        elif name == "Measure":
            qubit = targets[0]
            bit = params[0] if params else 0
            qis.mz(b, q[qubit], r[bit])

        elif name == "MeasureAll":
            pass  # Handled by individual measurements

        # Barrier
        elif name == "Barrier":
            qis.barrier(b, [q[t] for t in targets])

        # Reset
        elif name == "Reset":
            qis.reset(b, q[targets[0]])

        # Custom gates - need decomposition
        elif gate.is_custom():
            self._apply_custom_gate(gate)

        else:
            raise QIRBridgeError(f"Unsupported gate: {name}")

    def _apply_custom_gate(self, gate) -> None:
        """
        Apply a custom gate with user-defined matrix.

        For custom gates, we decompose into basic gates.

        Args:
            gate: CustomGate object with matrix
        """
        # For single-qubit custom gates, try U3 decomposition
        if len(gate.targets) == 1 and gate.matrix is not None:
            theta, phi, lam = self._extract_u3_params(gate.matrix)
            self._qis.rz(self._builder, lam, self._qubits[gate.targets[0]])
            self._qis.ry(self._builder, theta, self._qubits[gate.targets[0]])
            self._qis.rz(self._builder, phi, self._qubits[gate.targets[0]])
            return

        raise QIRBridgeError(
            f"Cannot compile custom gate '{gate.name}'. "
            "Custom gates require decomposition into basic gates."
        )

    @staticmethod
    def _extract_u3_params(matrix: np.ndarray) -> tuple:
        """
        Extract U3 parameters from a 2x2 unitary matrix.

        Returns:
            Tuple of (theta, phi, lambda) parameters
        """
        a, b = matrix[0]
        c, d = matrix[1]

        theta = 2 * np.arccos(np.clip(np.abs(a), 0, 1))
        phi = np.angle(c) - np.angle(a) if np.abs(a) > 1e-10 else 0
        lam = np.angle(b) - np.angle(a) + np.pi if np.abs(a) > 1e-10 else 0

        return (theta, phi, lam)


def circuit_to_qir(circuit: Circuit, name: Optional[str] = None) -> str:
    """
    Convenience function to convert a Circuit to QIR.

    Args:
        circuit: The Circuit to convert
        name: Optional name for the QIR module

    Returns:
        QIR code as string

    Example:
        from openquanta import Circuit, gates
        from openquanta.qir_bridge import circuit_to_qir

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)

        qir = circuit_to_qir(c)
        print(qir)
    """
    bridge = QIRBridge(circuit, name)
    return bridge.compile()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "QIRBridge",
    "QIRBridgeError",
    "circuit_to_qir",
]