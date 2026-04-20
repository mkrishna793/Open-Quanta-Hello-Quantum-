"""
Backend adapters for running quantum circuits.

Available backends:
- SimulatorBackend: Local Qiskit Aer simulator
- IBMBackend: IBM Quantum hardware (coming soon)
"""

from .base import Backend, BackendError
from .simulator import SimulatorBackend

__all__ = [
    "Backend",
    "BackendError",
    "SimulatorBackend",
]