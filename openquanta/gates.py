"""
Quantum Gates Library for open-Quanta.

This module provides:
1. All standard quantum gates (H, X, Y, Z, CNOT, etc.)
2. Rotation gates with parameters (RX, RY, RZ)
3. Multi-qubit gates (CNOT, CZ, SWAP, etc.)
4. Custom gate creation via CustomGate class

Users can create their own gates:
    my_gate = CustomGate("MYGATE", targets=[0, 1], matrix=[[1,0,0,0], ...])
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Callable
import numpy as np


@dataclass
class Gate:
    """
    Base class for all quantum gates.

    Attributes:
        name: Gate name (e.g., "H", "X", "CNOT")
        targets: List of target qubit indices
        params: Optional list of parameters (for rotation gates)
        matrix: Optional unitary matrix (for custom gates)
        control: Optional control qubit index (for controlled gates)
    """
    name: str
    targets: List[int]
    params: List[float] = field(default_factory=list)
    matrix: Optional[np.ndarray] = None
    control: Optional[int] = None

    def __repr__(self):
        if self.params:
            return f"Gate({self.name}, targets={self.targets}, params={self.params})"
        return f"Gate({self.name}, targets={self.targets})"

    def is_parametric(self) -> bool:
        """Check if gate has parameters."""
        return len(self.params) > 0

    def is_custom(self) -> bool:
        """Check if this is a custom gate with matrix."""
        return self.matrix is not None

    def num_qubits(self) -> int:
        """Return number of qubits this gate acts on."""
        return len(self.targets)

    def copy(self) -> 'Gate':
        """Create a copy of this gate."""
        return Gate(
            name=self.name,
            targets=self.targets.copy(),
            params=self.params.copy(),
            matrix=self.matrix.copy() if self.matrix is not None else None,
            control=self.control
        )


# ============================================================================
# SINGLE-QUBIT GATES
# ============================================================================

def I(qubit: int) -> Gate:
    """
    Identity gate - does nothing.
    Matrix: [[1, 0], [0, 1]]
    """
    return Gate("I", targets=[qubit])


def H(qubit: int) -> Gate:
    """
    Hadamard gate - creates superposition.
    Matrix: (1/√2) * [[1, 1], [1, -1]]

    Applies: |0⟩ → (|0⟩ + |1⟩)/√2
             |1⟩ → (|0⟩ - |1⟩)/√2
    """
    return Gate("H", targets=[qubit])


def X(qubit: int) -> Gate:
    """
    Pauli-X gate - bit flip (NOT gate).
    Matrix: [[0, 1], [1, 0]]

    Applies: |0⟩ → |1⟩
             |1⟩ → |0⟩
    """
    return Gate("X", targets=[qubit])


def Y(qubit: int) -> Gate:
    """
    Pauli-Y gate - bit and phase flip.
    Matrix: [[0, -i], [i, 0]]

    Applies: |0⟩ → i|1⟩
             |1⟩ → -i|0⟩
    """
    return Gate("Y", targets=[qubit])


def Z(qubit: int) -> Gate:
    """
    Pauli-Z gate - phase flip.
    Matrix: [[1, 0], [0, -1]]

    Applies: |0⟩ → |0⟩
             |1⟩ → -|1⟩
    """
    return Gate("Z", targets=[qubit])


def S(qubit: int) -> Gate:
    """
    S gate (phase gate) - π/2 phase shift.
    Matrix: [[1, 0], [0, i]]

    Applies: |0⟩ → |0⟩
             |1⟩ → i|1⟩
    """
    return Gate("S", targets=[qubit])


def Sdg(qubit: int) -> Gate:
    """
    S-dagger gate - inverse of S gate, -π/2 phase shift.
    Matrix: [[1, 0], [0, -i]]
    """
    return Gate("Sdg", targets=[qubit])


def T(qubit: int) -> Gate:
    """
    T gate (π/8 gate) - π/4 phase shift.
    Matrix: [[1, 0], [0, e^(iπ/4)]]
    """
    return Gate("T", targets=[qubit])


def Tdg(qubit: int) -> Gate:
    """
    T-dagger gate - inverse of T gate.
    Matrix: [[1, 0], [0, e^(-iπ/4)]]
    """
    return Gate("Tdg", targets=[qubit])


def SX(qubit: int) -> Gate:
    """
    Square root of X gate.
    Matrix: (1/2) * [[1+i, 1-i], [1-i, 1+i]]
    """
    return Gate("SX", targets=[qubit])


def SXdg(qubit: int) -> Gate:
    """
    Square root of X dagger - inverse of SX.
    """
    return Gate("SXdg", targets=[qubit])


# ============================================================================
# ROTATION GATES (PARAMETRIC)
# ============================================================================

def RX(qubit: int, theta: float) -> Gate:
    """
    Rotation around X-axis by angle theta.
    Matrix: [[cos(θ/2), -i*sin(θ/2)], [-i*sin(θ/2), cos(θ/2)]]

    Args:
        qubit: Target qubit index
        theta: Rotation angle in radians
    """
    return Gate("RX", targets=[qubit], params=[theta])


def RY(qubit: int, theta: float) -> Gate:
    """
    Rotation around Y-axis by angle theta.
    Matrix: [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]

    Args:
        qubit: Target qubit index
        theta: Rotation angle in radians
    """
    return Gate("RY", targets=[qubit], params=[theta])


def RZ(qubit: int, theta: float) -> Gate:
    """
    Rotation around Z-axis by angle theta.
    Matrix: [[e^(-iθ/2), 0], [0, e^(iθ/2)]]

    Args:
        qubit: Target qubit index
        theta: Rotation angle in radians
    """
    return Gate("RZ", targets=[qubit], params=[theta])


def Phase(qubit: int, theta: float) -> Gate:
    """
    Phase shift gate.
    Matrix: [[1, 0], [0, e^(iθ)]]

    Args:
        qubit: Target qubit index
        theta: Phase angle in radians
    """
    return Gate("Phase", targets=[qubit], params=[theta])


def U(qubit: int, theta: float, phi: float, lam: float) -> Gate:
    """
    Universal single-qubit rotation gate (U3).
    Matrix: [[cos(θ/2), -e^(iλ)sin(θ/2)],
             [e^(iφ)sin(θ/2), e^(i(φ+λ))cos(θ/2)]]

    Args:
        qubit: Target qubit index
        theta: Rotation angle
        phi: First phase angle
        lam: Second phase angle
    """
    return Gate("U", targets=[qubit], params=[theta, phi, lam])


def U1(qubit: int, lam: float) -> Gate:
    """
    U1 gate - single parameter phase gate.
    Matrix: [[1, 0], [0, e^(iλ)]]
    """
    return Gate("U1", targets=[qubit], params=[lam])


def U2(qubit: int, phi: float, lam: float) -> Gate:
    """
    U2 gate - two parameter gate.
    Matrix: (1/√2) * [[1, -e^(iλ)], [e^(iφ), e^(i(φ+λ))]]
    """
    return Gate("U2", targets=[qubit], params=[phi, lam])


def U3(qubit: int, theta: float, phi: float, lam: float) -> Gate:
    """
    U3 gate - three parameter universal gate (same as U).
    """
    return Gate("U3", targets=[qubit], params=[theta, phi, lam])


# ============================================================================
# TWO-QUBIT GATES
# ============================================================================

def CNOT(control: int, target: int) -> Gate:
    """
    Controlled-NOT (CX) gate - entanglement gate.
    Matrix: [[1,0,0,0], [0,1,0,0], [0,0,0,1], [0,0,1,0]]

    Applies X on target if control is |1⟩.

    Args:
        control: Control qubit index
        target: Target qubit index
    """
    return Gate("CNOT", targets=[control, target])


def CX(control: int, target: int) -> Gate:
    """Alias for CNOT."""
    return CNOT(control, target)


def CY(control: int, target: int) -> Gate:
    """
    Controlled-Y gate.
    Applies Y on target if control is |1⟩.
    """
    return Gate("CY", targets=[control, target])


def CZ(control: int, target: int) -> Gate:
    """
    Controlled-Z gate.
    Matrix: [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,-1]]

    Applies Z on target if control is |1⟩.
    """
    return Gate("CZ", targets=[control, target])


def CH(control: int, target: int) -> Gate:
    """
    Controlled-Hadamard gate.
    Applies H on target if control is |1⟩.
    """
    return Gate("CH", targets=[control, target])


def CS(control: int, target: int) -> Gate:
    """
    Controlled-S gate.
    Applies S on target if control is |1⟩.
    """
    return Gate("CS", targets=[control, target])


def CPhase(control: int, target: int, theta: float) -> Gate:
    """
    Controlled phase gate.
    Matrix: [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,e^(iθ)]]

    Args:
        control: Control qubit index
        target: Target qubit index
        theta: Phase angle in radians
    """
    return Gate("CPhase", targets=[control, target], params=[theta])


def CRX(control: int, target: int, theta: float) -> Gate:
    """
    Controlled RX rotation.

    Args:
        control: Control qubit index
        target: Target qubit index
        theta: Rotation angle in radians
    """
    return Gate("CRX", targets=[control, target], params=[theta])


def CRY(control: int, target: int, theta: float) -> Gate:
    """
    Controlled RY rotation.

    Args:
        control: Control qubit index
        target: Target qubit index
        theta: Rotation angle in radians
    """
    return Gate("CRY", targets=[control, target], params=[theta])


def CRZ(control: int, target: int, theta: float) -> Gate:
    """
    Controlled RZ rotation.

    Args:
        control: Control qubit index
        target: Target qubit index
        theta: Rotation angle in radians
    """
    return Gate("CRZ", targets=[control, target], params=[theta])


def SWAP(qubit1: int, qubit2: int) -> Gate:
    """
    SWAP gate - swaps two qubits.
    Matrix: [[1,0,0,0], [0,0,1,0], [0,1,0,0], [0,0,0,1]]

    Applies: |ab⟩ → |ba⟩
    """
    return Gate("SWAP", targets=[qubit1, qubit2])


def iSWAP(qubit1: int, qubit2: int) -> Gate:
    """
    iSWAP gate - swaps with i phase.
    Matrix: [[1,0,0,0], [0,0,i,0], [0,i,0,0], [0,0,0,1]]
    """
    return Gate("iSWAP", targets=[qubit1, qubit2])


def SQRT_SWAP(qubit1: int, qubit2: int) -> Gate:
    """
    Square root of SWAP gate.
    """
    return Gate("SQRT_SWAP", targets=[qubit1, qubit2])


def DCX(qubit1: int, qubit2: int) -> Gate:
    """
    Double CNOT gate.
    """
    return Gate("DCX", targets=[qubit1, qubit2])


# ============================================================================
# THREE-QUBIT GATES
# ============================================================================

def CCX(control1: int, control2: int, target: int) -> Gate:
    """
    Toffoli gate (CCX) - doubly controlled NOT.
    Applies X on target if both controls are |1⟩.

    Args:
        control1: First control qubit
        control2: Second control qubit
        target: Target qubit
    """
    return Gate("CCX", targets=[control1, control2, target])


def Toffoli(control1: int, control2: int, target: int) -> Gate:
    """Alias for CCX (Toffoli gate)."""
    return CCX(control1, control2, target)


def CCZ(control1: int, control2: int, target: int) -> Gate:
    """
    Doubly controlled Z gate.
    """
    return Gate("CCZ", targets=[control1, control2, target])


def CSWAP(control: int, qubit1: int, qubit2: int) -> Gate:
    """
    Fredkin gate (controlled SWAP).
    Swaps qubit1 and qubit2 if control is |1⟩.
    """
    return Gate("CSWAP", targets=[control, qubit1, qubit2])


def Fredkin(control: int, qubit1: int, qubit2: int) -> Gate:
    """Alias for CSWAP (Fredkin gate)."""
    return CSWAP(control, qubit1, qubit2)


# ============================================================================
# FOUR-QUBIT AND MULTI-QUBIT GATES
# ============================================================================

def CCCX(c1: int, c2: int, c3: int, target: int) -> Gate:
    """
    Triple controlled NOT gate.
    Applies X on target if all three controls are |1⟩.
    """
    return Gate("CCCX", targets=[c1, c2, c3, target])


def MCX(controls: List[int], target: int) -> Gate:
    """
    Multi-controlled X gate.
    Applies X on target if all controls are |1⟩.

    Args:
        controls: List of control qubit indices
        target: Target qubit index
    """
    return Gate("MCX", targets=controls + [target])


def MCZ(controls: List[int], target: int) -> Gate:
    """
    Multi-controlled Z gate.
    """
    return Gate("MCZ", targets=controls + [target])


# ============================================================================
# MEASUREMENT
# ============================================================================

def Measure(qubit: int, bit: int) -> Gate:
    """
    Measurement gate - measures qubit into classical bit.

    Args:
        qubit: Qubit to measure
        bit: Classical bit to store result
    """
    return Gate("Measure", targets=[qubit], params=[bit])


def MeasureAll() -> Gate:
    """
    Marker for measuring all qubits.
    The Circuit.measure_all() method handles this.
    """
    return Gate("MeasureAll", targets=[])


# ============================================================================
# BARRIER AND DELAY
# ============================================================================

def Barrier(qubits: List[int]) -> Gate:
    """
    Barrier gate - prevents optimization across this point.
    Used for circuit organization and visualization.
    """
    return Gate("Barrier", targets=qubits)


def Delay(qubit: int, duration: float) -> Gate:
    """
    Delay gate - idle for specified duration.

    Args:
        qubit: Qubit to delay
        duration: Duration in arbitrary units
    """
    return Gate("Delay", targets=[qubit], params=[duration])


# ============================================================================
# RESET
# ============================================================================

def Reset(qubit: int) -> Gate:
    """
    Reset gate - resets qubit to |0⟩ state.
    """
    return Gate("Reset", targets=[qubit])


# ============================================================================
# CUSTOM GATE CREATION
# ============================================================================

class CustomGate(Gate):
    """
    Custom gate with user-defined unitary matrix.

    Users can create their own gates:

    Example:
        # Create a custom single-qubit gate
        my_gate = CustomGate(
            name="MyGate",
            targets=[0],
            matrix=np.array([[0, 1], [1, 0]])  # Same as X
        )

        # Use in circuit
        circuit.apply(my_gate)

        # Or create a factory function
        def my_custom_gate(qubit: int) -> CustomGate:
            return CustomGate(
                name="MyGate",
                targets=[qubit],
                matrix=np.array([[0, 1], [1, 0]])
            )
    """

    def __init__(
        self,
        name: str,
        targets: List[int],
        matrix: np.ndarray,
        params: Optional[List[float]] = None
    ):
        """
        Create a custom gate.

        Args:
            name: Name for the gate
            targets: Target qubit indices
            matrix: Unitary matrix (must be square and unitary)
            params: Optional parameters

        Raises:
            ValueError: If matrix is not square or not unitary
        """
        # Validate matrix
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError(f"Matrix must be square, got shape {matrix.shape}")

        # Check if unitary (U† U = I)
        if not self._is_unitary(matrix):
            raise ValueError("Matrix must be unitary (U† U = I)")

        super().__init__(
            name=name,
            targets=targets,
            params=params or [],
            matrix=matrix
        )

    @staticmethod
    def _is_unitary(matrix: np.ndarray, tol: float = 1e-10) -> bool:
        """Check if matrix is unitary."""
        n = matrix.shape[0]
        identity = np.eye(n)
        product = matrix.conj().T @ matrix
        return np.allclose(product, identity, atol=tol)


def custom_gate(
    name: str,
    matrix: np.ndarray
) -> Callable:
    """
    Decorator/factory to create reusable custom gate functions.

    Example:
        # Create a factory for your custom gate
        @custom_gate("MyX", np.array([[0, 1], [1, 0]]))
        def my_x(qubit: int):
            return [qubit]

        # Use it
        circuit.apply(my_x, 0)

    Returns:
        Function that creates the gate when called with qubit indices.
    """
    def factory(*qubits: int) -> CustomGate:
        return CustomGate(name=name, targets=list(qubits), matrix=matrix)

    factory.__name__ = name
    factory.__doc__ = f"Custom gate: {name}"
    return factory


# ============================================================================
# CONTROLLED GATE GENERATOR
# ============================================================================

def controlled(base_gate: Gate, control: int) -> Gate:
    """
    Create a controlled version of any gate.

    Args:
        base_gate: The gate to make controlled
        control: Control qubit index

    Returns:
        A new gate that applies base_gate when control is |1⟩

    Example:
        # Create controlled-H
        h_gate = H(1)
        ch_gate = controlled(h_gate, control=0)
        circuit.apply(ch_gate)
    """
    new_targets = [control] + base_gate.targets
    return Gate(
        name=f"C{base_gate.name}",
        targets=new_targets,
        params=base_gate.params.copy(),
        matrix=base_gate.matrix,
        control=control
    )


# ============================================================================
# GATE UTILITIES
# ============================================================================

def is_single_qubit(gate: Gate) -> bool:
    """Check if gate operates on single qubit."""
    return gate.num_qubits() == 1


def is_two_qubit(gate: Gate) -> bool:
    """Check if gate operates on two qubits."""
    return gate.num_qubits() == 2


def is_multi_qubit(gate: Gate) -> bool:
    """Check if gate operates on more than two qubits."""
    return gate.num_qubits() > 2


def is_measurement(gate: Gate) -> bool:
    """Check if gate is a measurement."""
    return gate.name in ("Measure", "MeasureAll")


def is_barrier(gate: Gate) -> bool:
    """Check if gate is a barrier."""
    return gate.name == "Barrier"


# ============================================================================
# COMMON GATE MATRICES (for reference)
# ============================================================================

STANDARD_MATRICES = {
    "I": np.array([[1, 0], [0, 1]], dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    "H": np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),
    "S": np.array([[1, 0], [0, 1j]], dtype=complex),
    "T": np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex),
    "CNOT": np.array([[1,0,0,0], [0,1,0,0], [0,0,0,1], [0,0,1,0]], dtype=complex),
    "SWAP": np.array([[1,0,0,0], [0,0,1,0], [0,1,0,0], [0,0,0,1]], dtype=complex),
    "CZ": np.array([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,-1]], dtype=complex),
}


def get_matrix(gate_name: str) -> Optional[np.ndarray]:
    """
    Get the standard matrix for a named gate.

    Args:
        gate_name: Name of the gate (e.g., "H", "X", "CNOT")

    Returns:
        Unitary matrix or None if not found
    """
    return STANDARD_MATRICES.get(gate_name)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Base
    "Gate",
    "CustomGate",

    # Single-qubit
    "I", "H", "X", "Y", "Z", "S", "Sdg", "T", "Tdg", "SX", "SXdg",

    # Rotation
    "RX", "RY", "RZ", "Phase", "U", "U1", "U2", "U3",

    # Two-qubit
    "CNOT", "CX", "CY", "CZ", "CH", "CS", "CPhase",
    "CRX", "CRY", "CRZ", "SWAP", "iSWAP", "SQRT_SWAP", "DCX",

    # Three-qubit
    "CCX", "Toffoli", "CCZ", "CSWAP", "Fredkin",

    # Multi-qubit
    "CCCX", "MCX", "MCZ",

    # Measurement
    "Measure", "MeasureAll",

    # Utility
    "Barrier", "Delay", "Reset",

    # Custom
    "custom_gate", "controlled",

    # Helpers
    "is_single_qubit", "is_two_qubit", "is_multi_qubit",
    "is_measurement", "is_barrier", "get_matrix",

    # Constants
    "STANDARD_MATRICES",
]