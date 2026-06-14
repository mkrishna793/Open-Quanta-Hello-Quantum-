"""
Rust Statevector Simulator Backend for open-Quanta.

A hyper-fast simulator written in Rust via PyO3, replacing standard Python looping.
"""

from typing import Dict, Any
from .base import Backend, BackendError
from ..gates import get_matrix


class RustBackend(Backend):
    """
    Lightning fast statevector simulator implemented in Rust.
    """

    def __init__(self):
        super().__init__(name="RustBackend")
        try:
            import openquanta_rust_sim
            self._available = True
        except ImportError:
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    @property
    def max_qubits(self) -> int:
        return 30

    def execute(self, circuit: Any, shots: int = 1000) -> Dict[str, int]:
        if not self.available:
            raise BackendError("openquanta_rust_sim is not installed/compiled.")

        self.validate_circuit(circuit)

        n = circuit.n_qubits
        if n == 0:
            return {}

        import openquanta_rust_sim
        import numpy as np

        sim = openquanta_rust_sim.RustStatevectorSim(n)

        # Apply gates
        for gate in circuit.gates:
            if gate.name in ("Measure", "MeasureAll", "Barrier", "Delay"):
                continue

            targets = gate.targets
            control = getattr(gate, "control", None)

            if gate.name in ("CNOT", "CX") and len(targets) == 2 and control is None:
                # Basic CNOT
                sim.apply_cnot(targets[0], targets[1])
            elif control is not None and gate.name in ("X", "CNOT", "CX"):
                # Explicit controlled X
                sim.apply_cnot(control, targets[0])
            elif len(targets) == 1 and control is None:
                # Single qubit gate
                if gate.is_custom():
                    matrix = gate.matrix
                else:
                    matrix = get_matrix(gate.name)
                    if matrix is None:
                        # Parametric
                        if gate.name == "RX":
                            theta = gate.params[0]
                            matrix = np.array([[np.cos(theta/2), -1j*np.sin(theta/2)], [-1j*np.sin(theta/2), np.cos(theta/2)]])
                        elif gate.name == "RY":
                            theta = gate.params[0]
                            matrix = np.array([[np.cos(theta/2), -np.sin(theta/2)], [np.sin(theta/2), np.cos(theta/2)]])
                        elif gate.name == "RZ":
                            theta = gate.params[0]
                            matrix = np.array([[np.exp(-1j*theta/2), 0], [0, np.exp(1j*theta/2)]])
                        elif gate.name == "Phase":
                            theta = gate.params[0]
                            matrix = np.array([[1, 0], [0, np.exp(1j*theta)]])
                        else:
                            raise BackendError(f"Gate {gate.name} not implemented in Rust simulator yet.")

                # Flatten the 2x2 matrix to list of (real, imag) tuples
                flat_mat = [(float(matrix[i,j].real), float(matrix[i,j].imag)) for i in range(2) for j in range(2)]
                sim.apply_single_qubit_gate(targets[0], flat_mat)
            else:
                raise BackendError(f"Multi-qubit gate {gate.name} (not CNOT) is not yet supported natively in Rust backend.")

        # Prepare measurement map
        measurements = circuit._measurements
        if not measurements:
            return {}

        # The Rust backend handles sampling and little-endian ordering internally
        return sim.measure_and_sample(shots, measurements)

__all__ = [
    "RustBackend",
]
