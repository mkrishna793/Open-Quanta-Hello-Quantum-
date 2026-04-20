"""
Abstract Backend Class for open-Quanta.

All quantum backends (simulator, hardware) implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any


class BackendError(Exception):
    """Base exception for backend errors."""
    pass


class Backend(ABC):
    """
    Abstract base class for quantum backends.

    All backends (simulators, hardware) must implement this interface.
    This ensures consistent behavior across different execution targets.

    Example:
        class MyBackend(Backend):
            def execute(self, circuit, shots=1000):
                # Implementation here
                return {'0': 500, '1': 500}
    """

    def __init__(self, name: str = ""):
        """
        Initialize backend.

        Args:
            name: Human-readable name for the backend
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    def execute(self, circuit: Any, shots: int = 1000) -> Dict[str, int]:
        """
        Execute a circuit and return measurement results.

        Args:
            circuit: open-Quanta Circuit object
            shots: Number of execution shots

        Returns:
            Dictionary mapping measurement bit strings to counts.
            e.g., {'00': 500, '11': 500}

        Raises:
            BackendError: If execution fails
        """
        pass

    @property
    @abstractmethod
    def available(self) -> bool:
        """Check if backend is available for use."""
        pass

    @property
    @abstractmethod
    def max_qubits(self) -> int:
        """Maximum number of qubits supported."""
        pass

    def validate_circuit(self, circuit: Any) -> None:
        """
        Validate circuit for this backend.

        Args:
            circuit: Circuit to validate

        Raises:
            BackendError: If circuit is invalid for this backend
        """
        if circuit.n_qubits > self.max_qubits:
            raise BackendError(
                f"Circuit has {circuit.n_qubits} qubits, "
                f"but {self.name} only supports {self.max_qubits}"
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "Backend",
    "BackendError",
]