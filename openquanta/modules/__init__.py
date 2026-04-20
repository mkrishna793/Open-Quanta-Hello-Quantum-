"""
Pre-built quantum modules for common circuits.

Available modules:
- Entanglement: BellPair, BellState, GHZ, WState
- Superposition: Superposition, UniformSuperposition
- Algorithms: QFT, Teleportation, DeutschJozsa, Grover, BernsteinVazirani
- Utilities: QuantumRNG, Identity, AllX, AllH
"""

from .decorator import (
    Module,
    ModuleError,
    module,
    module_with_params,
    compose_modules,
)
from .standard import (
    BellPair,
    BellState,
    GHZ,
    WState,
    Superposition,
    UniformSuperposition,
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
    # Decorator
    "module",
    "Module",
    "ModuleError",
    "module_with_params",
    "compose_modules",

    # Standard modules
    "BellPair",
    "BellState",
    "GHZ",
    "WState",
    "Superposition",
    "UniformSuperposition",
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