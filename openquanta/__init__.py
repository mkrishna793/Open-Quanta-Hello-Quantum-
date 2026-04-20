"""
open-Quanta: Modular quantum computing for every Python developer.

Write Python. Run Quantum. Stay Modular.

Quick Start:
    from openquanta import Circuit, gates

    # Create a Bell state
    c = Circuit(2)
    c.apply(gates.H, 0)
    c.apply(gates.CNOT, 0, 1)
    c.measure_all()

    # Simulate
    result = c.simulate()
    print(result)  # {'00': 500, '11': 500}

Or use pre-built modules:
    from openquanta.modules import BellPair

    bell = BellPair()
    result = bell.simulate()

Custom gates:
    from openquanta.gates import CustomGate
    import numpy as np

    my_gate = CustomGate("MyX", [0], np.array([[0, 1], [1, 0]]))
    circuit.apply(my_gate)
"""

__version__ = "0.1.0"
__author__ = "open-Quanta Team"

# Core components
from .circuit import (
    Circuit,
    CircuitError,
    QubitError,
    GateError,
    QuantumCircuit,
)

from .gates import (
    # Base
    Gate,
    CustomGate,

    # Single-qubit
    I, H, X, Y, Z, S, Sdg, T, Tdg, SX, SXdg,

    # Rotation
    RX, RY, RZ, Phase, U, U1, U2, U3,

    # Two-qubit
    CNOT, CX, CY, CZ, CH, CS, CPhase,
    CRX, CRY, CRZ, SWAP, iSWAP, SQRT_SWAP, DCX,

    # Three-qubit
    CCX, Toffoli, CCZ, CSWAP, Fredkin,

    # Multi-qubit
    CCCX, MCX, MCZ,

    # Measurement
    Measure, MeasureAll,

    # Utility
    Barrier, Delay, Reset,

    # Custom gate support
    custom_gate, controlled,

    # Helpers
    is_single_qubit, is_two_qubit, is_multi_qubit,
    is_measurement, is_barrier, get_matrix,
    STANDARD_MATRICES,
)

from .qir_bridge import (
    QIRBridge,
    QIRBridgeError,
    circuit_to_qir,
)

from .backends import (
    Backend,
    BackendError,
    SimulatorBackend,
)

from .modules import (
    # Decorator
    module,
    Module,
    ModuleError,
    compose_modules,

    # Standard modules
    BellPair,
    BellState,
    GHZ,
    WState,
    Superposition,
    QFT,
    InverseQFT,
    Teleportation,
    DeutschJozsa,
    Grover,
    BernsteinVazirani,
    QuantumRNG,
    Identity,
    AllX,
    AllH,
)


__all__ = [
    # Version
    "__version__",
    "__author__",

    # Circuit
    "Circuit",
    "CircuitError",
    "QubitError",
    "GateError",
    "QuantumCircuit",

    # Gates
    "Gate",
    "CustomGate",
    "I", "H", "X", "Y", "Z", "S", "Sdg", "T", "Tdg", "SX", "SXdg",
    "RX", "RY", "RZ", "Phase", "U", "U1", "U2", "U3",
    "CNOT", "CX", "CY", "CZ", "CH", "CS", "CPhase",
    "CRX", "CRY", "CRZ", "SWAP", "iSWAP", "SQRT_SWAP", "DCX",
    "CCX", "Toffoli", "CCZ", "CSWAP", "Fredkin",
    "CCCX", "MCX", "MCZ",
    "Measure", "MeasureAll",
    "Barrier", "Delay", "Reset",
    "custom_gate", "controlled",
    "STANDARD_MATRICES",

    # Helpers
    "is_single_qubit", "is_two_qubit", "is_multi_qubit",
    "is_measurement", "is_barrier", "get_matrix",

    # QIR
    "QIRBridge",
    "QIRBridgeError",
    "circuit_to_qir",

    # Backends
    "Backend",
    "BackendError",
    "SimulatorBackend",

    # Modules
    "module",
    "Module",
    "ModuleError",
    "compose_modules",
    "BellPair",
    "BellState",
    "GHZ",
    "WState",
    "Superposition",
    "QFT",
    "InverseQFT",
    "Teleportation",
    "DeutschJozsa",
    "Grover",
    "BernsteinVazirani",
    "QuantumRNG",
    "Identity",
    "AllX",
    "AllH",
]