"""
Pure NumPy Local Simulator Backend for open-Quanta.

A completely independent statevector simulator that does not require Qiskit.
"""

from typing import Dict, Optional, Any, List
import numpy as np

from .base import Backend, BackendError
from ..gates import get_matrix


class NumpyBackend(Backend):
    """
    Independent pure-NumPy statevector simulator.

    This simulator applies unitary matrices directly to a statevector.
    It is lightweight and runs entirely in Python + NumPy.
    """

    def __init__(self):
        super().__init__(name="NumpyBackend")

    @property
    def available(self) -> bool:
        """Always available as it only depends on NumPy."""
        return True

    @property
    def max_qubits(self) -> int:
        """Limit to 15 qubits to prevent excessive memory usage."""
        return 15

    def execute(self, circuit: Any, shots: int = 1000) -> Dict[str, int]:
        """
        Execute circuit using numpy statevector simulation.
        """
        self.validate_circuit(circuit)

        n = circuit.n_qubits
        if n == 0:
            return {}

        # Initialize statevector to |0...0>
        # Dimension is 2^n. State is a 1D complex array.
        state = np.zeros(2**n, dtype=complex)
        state[0] = 1.0

        # Apply gates
        for gate in circuit.gates:
            if gate.name in ("Measure", "MeasureAll", "Barrier", "Delay"):
                continue

            state = self._apply_gate(state, gate, n)

        # Measure
        # Determine which qubits are mapped to which classical bits
        measurements = circuit._measurements  # dict: qubit_idx -> bit_idx
        if not measurements:
            return {}

        # Calculate probabilities
        probabilities = np.abs(state) ** 2

        # Normalize probabilities to avoid floating point errors with np.random.choice
        if np.sum(probabilities) > 0:
            probabilities = probabilities / np.sum(probabilities)

        # Sample
        outcomes = np.random.choice(2**n, size=shots, p=probabilities)

        counts = {}
        for outcome in outcomes:
            # Convert integer outcome to bitstring
            # Statevector order: MSB is qubit 0 or LSB is qubit 0?
            # Qiskit uses little-endian (qubit 0 is rightmost bit). We'll follow that for consistency.
            # E.g., outcome 1 means qubit 0 is 1, qubit 1 is 0.
            # In binary string representation, the standard is usually qubit 0 at the end.

            # Binary string representation, padded to n bits
            binary = format(outcome, f'0{n}b')
            # Flip it if we want qubit 0 to be the rightmost

            # Map physical qubits to classical bits
            # Result string length is n_bits
            result_str_list = ['0'] * circuit.n_bits
            for q_idx, c_idx in measurements.items():
                # Extract bit for this qubit.
                # In standard big-endian format outcome:
                # the i-th bit from the left corresponds to qubit i if we use standard tensor order.
                bit_val = binary[q_idx]
                result_str_list[c_idx] = bit_val

            result_str = "".join(result_str_list)

            # Reverse to match standard Qiskit little-endian format (c[0] on the right)
            result_str = result_str[::-1]

            counts[result_str] = counts.get(result_str, 0) + 1

        return counts

    def _apply_gate(self, state: np.ndarray, gate: Any, n_qubits: int) -> np.ndarray:
        """Apply a gate matrix to the statevector."""
        # Get matrix
        if gate.is_custom():
            matrix = gate.matrix
        else:
            matrix = get_matrix(gate.name)
            if matrix is None:
                # We need to construct parametric gates
                matrix = self._get_parametric_matrix(gate)
                if matrix is None:
                    raise BackendError(f"Gate {gate.name} not supported by NumpyBackend")

        targets = gate.targets
        control = getattr(gate, "control", None)

        if control is not None:
            targets = [control] + targets

        # Check matrix dimension matches number of targets
        num_targets = len(targets)
        expected_dim = 2 ** num_targets
        if matrix.shape != (expected_dim, expected_dim):
            raise BackendError(f"Matrix shape {matrix.shape} does not match targets {targets}")

        # Reshape state to tensor (2, 2, ..., 2)
        tensor_state = state.reshape([2] * n_qubits)

        # Apply matrix using tensordot or einsum
        # It's easier to reshape matrix to (2, 2, ..., 2, 2, 2, ..., 2)
        tensor_matrix = matrix.reshape([2] * num_targets + [2] * num_targets)

        # We want to contract the last 'num_targets' indices of the matrix with the 'targets' indices of the state
        axes = (list(range(num_targets, 2 * num_targets)), targets)

        # np.tensordot puts the contracted axes at the end, and the remaining axes of state at the end.
        # We need to carefully put the axes back in the original order.
        new_tensor_state = np.tensordot(tensor_matrix, tensor_state, axes=axes)

        # After tensordot, the axes are: (targets from matrix) + (remaining from state)
        # We need to transpose to get back to original qubit ordering (0, 1, ..., n-1)
        # Let's track the current axes
        current_axes = targets + [i for i in range(n_qubits) if i not in targets]

        # We want the output axes to be [0, 1, ..., n-1]
        # So we need a permutation that maps current_axes to [0, 1, ..., n-1]
        # permutation[i] should be the index in current_axes where value is i
        permutation = [current_axes.index(i) for i in range(n_qubits)]

        new_tensor_state = np.transpose(new_tensor_state, permutation)

        return new_tensor_state.flatten()

    def _get_parametric_matrix(self, gate: Any) -> Optional[np.ndarray]:
        """Generate matrices for parameterized gates."""
        name = gate.name
        params = gate.params

        if name == "RX":
            theta = params[0]
            return np.array([
                [np.cos(theta/2), -1j * np.sin(theta/2)],
                [-1j * np.sin(theta/2), np.cos(theta/2)]
            ])
        elif name == "RY":
            theta = params[0]
            return np.array([
                [np.cos(theta/2), -np.sin(theta/2)],
                [np.sin(theta/2), np.cos(theta/2)]
            ])
        elif name == "RZ":
            theta = params[0]
            return np.array([
                [np.exp(-1j * theta / 2), 0],
                [0, np.exp(1j * theta / 2)]
            ])
        elif name == "Phase":
            theta = params[0]
            return np.array([
                [1, 0],
                [0, np.exp(1j * theta)]
            ])

        return None

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "NumpyBackend",
]
