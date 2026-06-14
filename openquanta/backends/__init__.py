"""
Backend adapters for running quantum circuits.

Available backends:
- SimulatorBackend: Local Qiskit Aer simulator
- IBMBackend: IBM Quantum hardware (coming soon)
"""

from .base import Backend, BackendError
from .simulator import SimulatorBackend
from .numpy_sim import NumpyBackend
from .open_hardware import OpenHardwareBackend
from .rust_sim import RustBackend

__all__ = [
    "Backend",
    "BackendError",
    "SimulatorBackend",
    "NumpyBackend",
    "OpenHardwareBackend",
    "RustBackend",
]