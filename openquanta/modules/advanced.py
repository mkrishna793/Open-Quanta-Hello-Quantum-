"""
Advanced Quantum Modules for open-Quanta.

Provides advanced experimental algorithms such as Quantum Error Correction (QEC)
and Quantum Machine Learning (QML) templates.
"""

from ..circuit import Circuit
from .. import gates
from .decorator import module


# ============================================================================
# QUANTUM ERROR CORRECTION (QEC)
# ============================================================================

@module
def BitFlipCode(error_qubit: int = None):
    """
    3-qubit bit-flip error correction code.

    Demonstrates encoding a single logical qubit into 3 physical qubits
    to protect against a single bit-flip (X) error.

    Args:
        error_qubit: Optional index (0, 1, or 2) to inject a manual bit-flip error.

    Returns:
        Circuit demonstrating the bit-flip code
    """
    # 3 data qubits, 2 ancilla qubits for syndrome measurement
    c = Circuit(5, n_bits=3, name="BitFlipCode")

    # 1. ENCODING
    # Start with some arbitrary state on logical qubit (q0)
    c.apply(gates.H, 0)
    c.apply(gates.RZ, 0, 0.5)

    # Encode q0 into q0, q1, q2
    c.apply(gates.CNOT, 0, 1)
    c.apply(gates.CNOT, 0, 2)
    c.barrier()

    # 2. ERROR INJECTION (Optional)
    if error_qubit is not None and 0 <= error_qubit <= 2:
        c.apply(gates.X, error_qubit)
    c.barrier()

    # 3. SYNDROME MEASUREMENT
    # Measure parity of q0,q1 into ancilla q3
    c.apply(gates.CNOT, 0, 3)
    c.apply(gates.CNOT, 1, 3)

    # Measure parity of q1,q2 into ancilla q4
    c.apply(gates.CNOT, 1, 4)
    c.apply(gates.CNOT, 2, 4)
    c.barrier()

    # Measure ancillas
    c.measure(3, 0)  # Syndrome bit 0
    c.measure(4, 1)  # Syndrome bit 1

    # 4. RECOVERY (Classical feed-forward or quantum controlled)
    # In a real QEC cycle, we'd use classical logic. Here we use quantum controlled gates.
    # Syndrome 11 -> q1 error
    # Syndrome 10 -> q0 error
    # Syndrome 01 -> q2 error
    c.apply(gates.CCX, 3, 4, 1) # Fix q1

    # Fix q0 (if q3=1 and q4=0)
    c.apply(gates.X, 4)
    c.apply(gates.CCX, 3, 4, 0)
    c.apply(gates.X, 4)

    # Fix q2 (if q3=0 and q4=1)
    c.apply(gates.X, 3)
    c.apply(gates.CCX, 3, 4, 2)
    c.apply(gates.X, 3)
    c.barrier()

    # 5. DECODING
    c.apply(gates.CNOT, 0, 2)
    c.apply(gates.CNOT, 0, 1)

    # Final measurement of the logical qubit
    c.measure(0, 2)

    return c


# ============================================================================
# QUANTUM MACHINE LEARNING (QML)
# ============================================================================

@module
def QNNLayer(n_qubits: int, params: list):
    """
    A single layer of a Quantum Neural Network.

    Consists of parameterized RY rotations followed by a hardware-efficient
    entangling structure.

    Args:
        n_qubits: Number of qubits
        params: List of rotation angles (length must equal n_qubits)

    Returns:
        Circuit for the QNN layer
    """
    if len(params) != n_qubits:
        raise ValueError(f"Expected {n_qubits} parameters, got {len(params)}")

    c = Circuit(n_qubits, name=f"QNNLayer({n_qubits})")

    # Parameterized rotations
    for i in range(n_qubits):
        c.apply(gates.RY, i, params[i])

    # Hardware efficient entanglement (linear topology)
    for i in range(n_qubits - 1):
        c.apply(gates.CZ, i, i + 1)

    return c


@module
def QAOA_MaxCut(edges: list, n_qubits: int, gamma: float, beta: float):
    """
    A single step of the Quantum Approximate Optimization Algorithm (QAOA)
    for the MaxCut problem.

    Args:
        edges: List of tuples representing graph edges e.g., [(0,1), (1,2)]
        n_qubits: Number of nodes in the graph
        gamma: Phase separator parameter
        beta: Mixing parameter

    Returns:
        Circuit representing one QAOA layer
    """
    c = Circuit(n_qubits, name="QAOA_Layer")

    # 1. Cost Hamiltonian (Phase Separator)
    for (i, j) in edges:
        # e^{-i gamma Z_i Z_j}
        c.apply(gates.CNOT, i, j)
        c.apply(gates.RZ, j, 2 * gamma)
        c.apply(gates.CNOT, i, j)

    # 2. Mixing Hamiltonian
    for i in range(n_qubits):
        c.apply(gates.RX, i, 2 * beta)

    return c


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "BitFlipCode",
    "QNNLayer",
    "QAOA_MaxCut",
]
