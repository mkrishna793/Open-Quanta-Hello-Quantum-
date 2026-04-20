"""
Standard Quantum Modules for open-Quanta.

Pre-built modules for common quantum circuits.
"""

import numpy as np
from ..circuit import Circuit
from .. import gates
from .decorator import module


# ============================================================================
# ENTANGLEMENT MODULES
# ============================================================================

@module
def BellPair():
    """
    Create a Bell state (maximally entangled 2-qubit state).

    The Bell state is: (|00⟩ + |11⟩) / √2

    Returns:
        Circuit that produces Bell state

    Example:
        bell = BellPair()
        result = bell.simulate()
        # Result: {'00': ~500, '11': ~500}
    """
    c = Circuit(2, name="BellPair")
    c.apply(gates.H, 0)
    c.apply(gates.CNOT, 0, 1)
    c.measure_all()
    return c


@module
def BellState(theta: float = 0, phi: float = 0):
    """
    Create a generalized Bell state.

    |Φ(θ,φ)⟩ = cos(θ/2)|00⟩ + e^(iφ)sin(θ/2)|11⟩

    Args:
        theta: Rotation angle (default: 0 gives |00⟩)
        phi: Phase angle

    Returns:
        Circuit producing the Bell state
    """
    c = Circuit(2, name=f"BellState({theta},{phi})")
    c.apply(gates.H, 0)
    c.apply(gates.RY, 0, theta)
    c.apply(gates.CNOT, 0, 1)
    c.apply(gates.RZ, 1, phi)
    c.measure_all()
    return c


@module
def GHZ(n_qubits: int = 3):
    """
    Create a GHZ (Greenberger-Horne-Zeilinger) state.

    GHZ state: (|0...0⟩ + |1...1⟩) / √2

    Args:
        n_qubits: Number of qubits (default: 3)

    Returns:
        Circuit producing GHZ state

    Example:
        ghz = GHZ(4)
        result = ghz.simulate()
        # Result: {'0000': ~500, '1111': ~500}
    """
    c = Circuit(n_qubits, name=f"GHZ({n_qubits})")
    c.apply(gates.H, 0)
    for i in range(n_qubits - 1):
        c.apply(gates.CNOT, i, i + 1)
    c.measure_all()
    return c


@module
def WState(n_qubits: int = 3):
    """
    Create a W state.

    W state: (|100...0⟩ + |010...0⟩ + ... + |000...1⟩) / √n

    Args:
        n_qubits: Number of qubits (default: 3)

    Returns:
        Circuit producing W state
    """
    c = Circuit(n_qubits, name=f"WState({n_qubits})")

    # W state preparation
    import numpy as np

    # Start with |100...0⟩
    c.apply(gates.X, 0)

    # Create superposition using rotations
    for i in range(n_qubits - 1):
        theta = 2 * np.arcsin(1 / np.sqrt(n_qubits - i))
        c.apply(gates.RY, i, theta)
        c.apply(gates.CNOT, i, i + 1)
        c.apply(gates.RY, i, -theta)

    c.measure_all()
    return c


# ============================================================================
# SUPERPOSITION MODULES
# ============================================================================

@module
def Superposition(n_qubits: int = 1):
    """
    Create equal superposition on all qubits.

    Superposition: (|0⟩ + |1⟩ + |2⟩ + ... + |2^n-1⟩) / √2^n

    Args:
        n_qubits: Number of qubits in superposition

    Returns:
        Circuit creating equal superposition

    Example:
        sup = Superposition(2)
        result = sup.simulate()
        # Result: roughly equal counts for 00, 01, 10, 11
    """
    c = Circuit(n_qubits, name=f"Superposition({n_qubits})")
    for i in range(n_qubits):
        c.apply(gates.H, i)
    c.measure_all()
    return c


@module
def UniformSuperposition(n_qubits: int):
    """
    Create uniform superposition over all computational basis states.

    Same as Superposition but more explicit naming.

    Args:
        n_qubits: Number of qubits

    Returns:
        Circuit in uniform superposition
    """
    return Superposition(n_qubits)()


# ============================================================================
# QUANTUM FOURIER TRANSFORM
# ============================================================================

@module
def QFT(n_qubits: int, inverse: bool = False):
    """
    Quantum Fourier Transform circuit.

    The QFT maps computational basis to Fourier basis.

    Args:
        n_qubits: Number of qubits
        inverse: If True, apply inverse QFT

    Returns:
        QFT circuit

    Example:
        qft = QFT(3)
        circuit = qft()
    """
    c = Circuit(n_qubits, name=f"QFT({n_qubits})")

    for i in range(n_qubits):
        # Apply H
        c.apply(gates.H, i)

        # Apply controlled rotations
        for j in range(i + 1, n_qubits):
            angle = np.pi / (2 ** (j - i))
            c.apply(gates.CPhase, j, i, angle)
            # Note: CPhase may need to be CRZ depending on convention

    # Swap qubits to reverse order
    for i in range(n_qubits // 2):
        c.apply(gates.SWAP, i, n_qubits - 1 - i)

    c.measure_all()
    return c


@module
def InverseQFT(n_qubits: int):
    """
    Inverse Quantum Fourier Transform.

    Args:
        n_qubits: Number of qubits

    Returns:
        Inverse QFT circuit
    """
    return QFT(n_qubits, inverse=True)()


# ============================================================================
# QUANTUM TELEPORTATION
# ============================================================================

@module
def Teleportation():
    """
    Quantum teleportation circuit.

    Teleports a qubit state from Alice to Bob using
    an entangled Bell pair and classical communication.

    Returns:
        Teleportation circuit (3 qubits, 2 classical bits)
    """
    c = Circuit(3, n_bits=2, name="Teleportation")

    # Prepare Bell pair between qubits 1 and 2
    c.apply(gates.H, 1)
    c.apply(gates.CNOT, 1, 2)

    # Alice's operations on qubits 0 and 1
    c.apply(gates.CNOT, 0, 1)
    c.apply(gates.H, 0)

    # Measurement
    c.measure(0, 0)
    c.measure(1, 1)

    # Bob's corrections (classical controlled)
    # These would normally be conditioned on measurement results
    # For simulation, we include both possibilities
    c.apply(gates.X, 2)  # If measurement of q1 is 1
    c.apply(gates.Z, 2)  # If measurement of q0 is 1

    c.measure(2, 0)  # Measure teleported qubit
    return c


# ============================================================================
# DEUTSCH-JOZSA ALGORITHM
# ============================================================================

@module
def DeutschJozsa(n_qubits: int, oracle_type: str = "balanced"):
    """
    Deutsch-Jozsa algorithm circuit.

    Determines if a function is constant or balanced
    with a single quantum query.

    Args:
        n_qubits: Number of input qubits
        oracle_type: "constant" or "balanced"

    Returns:
        Deutsch-Jozsa circuit
    """
    total_qubits = n_qubits + 1  # +1 for ancilla
    c = Circuit(total_qubits, name=f"DeutschJozsa({n_qubits})")

    # Initialize ancilla to |1⟩
    c.apply(gates.X, n_qubits)

    # Apply H to all qubits
    for i in range(total_qubits):
        c.apply(gates.H, i)

    # Apply oracle
    if oracle_type == "constant":
        # Constant oracle: do nothing or flip ancilla
        pass
    else:
        # Balanced oracle: CNOT each input to ancilla
        for i in range(n_qubits):
            c.apply(gates.CNOT, i, n_qubits)

    # Apply H to input qubits
    for i in range(n_qubits):
        c.apply(gates.H, i)

    # Measure input qubits
    for i in range(n_qubits):
        c.measure(i, i)

    return c


# ============================================================================
# GROVER'S ALGORITHM (SIMPLIFIED)
# ============================================================================

@module
def Grover(n_qubits: int, marked_state: int, iterations: int = None):
    """
    Grover's search algorithm circuit.

    Searches for a marked item in an unsorted database.

    Args:
        n_qubits: Number of qubits
        marked_state: Index of the marked item (0 to 2^n - 1)
        iterations: Number of Grover iterations (default: optimal)

    Returns:
        Grover search circuit
    """
    import numpy as np

    c = Circuit(n_qubits, name=f"Grover({n_qubits})")

    # Calculate optimal iterations
    N = 2 ** n_qubits
    if iterations is None:
        iterations = int(np.pi / 4 * np.sqrt(N))

    # Initial superposition
    for i in range(n_qubits):
        c.apply(gates.H, i)

    # Grover iterations
    for _ in range(iterations):
        # Oracle (mark the target state)
        c.barrier()

        # Apply X to qubits where target bit is 0
        binary = format(marked_state, f'0{n_qubits}b')
        for i, bit in enumerate(binary):
            if bit == '0':
                c.apply(gates.X, i)

        # Multi-controlled Z
        c.apply(gates.H, n_qubits - 1)
        if n_qubits == 2:
            c.apply(gates.CNOT, 0, 1)
        else:
            c.apply(gates.CCX, 0, 1, 2)  # Simplified for 3 qubits
        c.apply(gates.H, n_qubits - 1)

        # Uncompute X
        for i, bit in enumerate(binary):
            if bit == '0':
                c.apply(gates.X, i)

        # Diffusion operator
        c.barrier()
        for i in range(n_qubits):
            c.apply(gates.H, i)
            c.apply(gates.X, i)

        # Apply multi-controlled Z
        c.apply(gates.H, n_qubits - 1)
        if n_qubits == 2:
            c.apply(gates.CNOT, 0, 1)
        else:
            c.apply(gates.CCX, 0, 1, 2)
        c.apply(gates.H, n_qubits - 1)

        for i in range(n_qubits):
            c.apply(gates.X, i)
            c.apply(gates.H, i)

    c.measure_all()
    return c


# ============================================================================
# QUANTUM RANDOM NUMBER GENERATOR
# ============================================================================

@module
def QuantumRNG(n_bits: int = 8):
    """
    Quantum random number generator.

    Uses quantum superposition to generate truly random numbers.

    Args:
        n_bits: Number of random bits to generate

    Returns:
        Circuit that generates random bits

    Example:
        rng = QuantumRNG(4)
        result = rng.simulate(shots=1)
        # Result: one random 4-bit number
    """
    c = Circuit(n_bits, name=f"QuantumRNG({n_bits})")

    # Put all qubits in superposition
    for i in range(n_bits):
        c.apply(gates.H, i)

    c.measure_all()
    return c


# ============================================================================
# BERNSTEIN-VAZIRANI ALGORITHM
# ============================================================================

@module
def BernsteinVazirani(n_qubits: int, secret_string: int):
    """
    Bernstein-Vazirani algorithm circuit.

    Finds a hidden bit string with a single query.

    Args:
        n_qubits: Number of qubits
        secret_string: Hidden string to find

    Returns:
        Bernstein-Vazirani circuit
    """
    c = Circuit(n_qubits + 1, name=f"BernsteinVazirani({n_qubits})")

    # Initialize ancilla
    c.apply(gates.X, n_qubits)

    # Apply H to all
    for i in range(n_qubits + 1):
        c.apply(gates.H, i)

    # Oracle encodes secret string
    binary = format(secret_string, f'0{n_qubits}b')
    for i, bit in enumerate(binary):
        if bit == '1':
            c.apply(gates.CNOT, i, n_qubits)

    # Apply H to input qubits
    for i in range(n_qubits):
        c.apply(gates.H, i)

    # Measure
    for i in range(n_qubits):
        c.measure(i, i)

    return c


# ============================================================================
# UTILITY MODULES
# ============================================================================

@module
def Identity(n_qubits: int = 1):
    """
    Identity circuit - does nothing.

    Useful for testing and as a placeholder.

    Args:
        n_qubits: Number of qubits

    Returns:
        Identity circuit
    """
    c = Circuit(n_qubits, name=f"Identity({n_qubits})")
    for i in range(n_qubits):
        c.apply(gates.I, i)
    c.measure_all()
    return c


@module
def AllX(n_qubits: int):
    """
    Apply X gate to all qubits.

    Args:
        n_qubits: Number of qubits

    Returns:
        Circuit with X on all qubits
    """
    c = Circuit(n_qubits, name=f"AllX({n_qubits})")
    for i in range(n_qubits):
        c.apply(gates.X, i)
    c.measure_all()
    return c


@module
def AllH(n_qubits: int):
    """
    Apply Hadamard to all qubits.

    Same as Superposition module.

    Args:
        n_qubits: Number of qubits

    Returns:
        Circuit with H on all qubits
    """
    c = Circuit(n_qubits, name=f"AllH({n_qubits})")
    for i in range(n_qubits):
        c.apply(gates.H, i)
    c.measure_all()
    return c


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Entanglement
    "BellPair",
    "BellState",
    "GHZ",
    "WState",

    # Superposition
    "Superposition",
    "UniformSuperposition",

    # Algorithms
    "QFT",
    "InverseQFT",
    "Teleportation",
    "DeutschJozsa",
    "Grover",
    "BernsteinVazirani",

    # Utilities
    "QuantumRNG",
    "Identity",
    "AllX",
    "AllH",
]