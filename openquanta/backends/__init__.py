"""
Backend adapters for running quantum circuits.

Available backends:
- SimulatorBackend: Local Qiskit Aer simulator
- IBMBackend: IBM Quantum hardware (coming soon)
"""

from .base import Backend, BackendError
from .simulator import SimulatorBackend
from .numpy_sim import NumpyBackend

__all__ = [
    "Backend",
    "BackendError",
    "SimulatorBackend",
    "NumpyBackend",
]