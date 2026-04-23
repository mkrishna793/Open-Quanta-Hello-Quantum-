"""
Module System for open-Quanta.

Provides the @module decorator for creating reusable quantum circuits.
"""

from typing import Callable, Optional
from functools import wraps


class ModuleError(Exception):
    """Raised when module operations fail."""
    pass


class Module:
    """
    A reusable quantum module.

    Modules are quantum circuits wrapped in a function,
    making them reusable and composable.

    Example:
        @module
        def BellPair():
            c = Circuit(2)
            c.apply(gates.H, 0)
            c.apply(gates.CNOT, 0, 1)
            c.measure_all()
            return c

        # Use it
        bell = BellPair()
        result = bell.simulate()
    """

    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Initialize a module.

        Args:
            func: Function that builds the circuit
            name: Module name (default: function name)
            description: Module description (default: function docstring)
        """
        self.func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__ or ""

    def __call__(self, *args, **kwargs):
        """
        Build and return the circuit.

        Returns:
            Circuit object
        """
        return self.func(*args, **kwargs)

    def simulate(self, *args, shots: int = 1000, **kwargs) -> dict:
        """
        Build circuit and simulate directly.

        Returns:
            Simulation results
        """
        circuit = self(*args, **kwargs)
        return circuit.simulate(shots=shots)

    def run(
        self,
        *args,
        backend: str = "simulator",
        shots: int = 1000,
        **kwargs
    ) -> dict:
        """
        Build circuit and run on backend.

        Returns:
            Execution results
        """
        circuit = self(*args, **kwargs)
        return circuit.run(backend=backend, shots=shots)

    def to_qir(self, *args, **kwargs) -> str:
        """
        Build circuit and convert to QIR.

        Returns:
            QIR code string
        """
        circuit = self(*args, **kwargs)
        return circuit.to_qir()

    def compose(
        self,
        other: 'Module',
        *args,
        **kwargs
    ) -> 'Module':
        """
        Compose this module with another.

        Args:
            other: Another Module to compose with
            *args: Arguments for other module
            **kwargs: Keyword arguments for other module

        Returns:
            New composed Module
        """
        @module
        def composed():
            c1 = self()
            c2 = other(*args, **kwargs) if callable(other) else other

            # Append c2 to c1
            result = c1.copy()
            for gate in c2.gates:
                result.gates.append(gate)
            result.n_bits = max(result.n_bits, c2.n_bits)
            return result

        composed.name = f"{self.name}_+_{other.name if hasattr(other, 'name') else 'other'}"
        return composed

    def __repr__(self) -> str:
        return f"Module({self.name})"


def module(func: Callable) -> Module:
    """
    Decorator to create a Module from a function.

    Args:
        func: Function that returns a Circuit

    Returns:
        Module object

    Example:
        @module
        def Superposition(n_qubits=1):
            '''Create superposition on n qubits.'''
            c = Circuit(n_qubits)
            for i in range(n_qubits):
                c.apply(gates.H, i)
            c.measure_all()
            return c

        # Use it
        sup = Superposition(3)
        result = sup.simulate()
    """
    return Module(func)


def module_with_params(**param_defaults):
    """
    Create a module with explicit parameter defaults.

    Args:
        **param_defaults: Default values for parameters

    Returns:
        Decorator that creates a Module

    Example:
        @module_with_params(n_qubits=2, name="bell")
        def MyCircuit(n_qubits, name):
            c = Circuit(n_qubits, name=name)
            c.apply(gates.H, 0)
            c.apply(gates.CNOT, 0, 1)
            return c

        # Use with defaults
        c1 = MyCircuit()

        # Or override
        c2 = MyCircuit(n_qubits=3)
    """
    def decorator(func: Callable) -> Module:
        @wraps(func)
        def wrapper(**kwargs):
            # Merge defaults with provided kwargs
            final_kwargs = {**param_defaults, **kwargs}
            return func(**final_kwargs)

        return Module(wrapper, name=func.__name__)
    return decorator


def compose_modules(*modules: Module, name: Optional[str] = None) -> Module:
    """
    Compose multiple modules into one.

    Args:
        *modules: Modules to compose
        name: Name for the composed module

    Returns:
        New composed Module

    Example:
        bell = BellPair()
        sup = Superposition(2)

        combined = compose_modules(bell, sup, name="bell_and_superposition")
        result = combined.simulate()
    """
    @module
    def composed():
        from ..circuit import Circuit

        # Get circuits from all modules
        circuits = [m() for m in modules]

        # Find total qubits needed
        total_qubits = max(c.n_qubits for c in circuits)

        # Create result circuit
        result = Circuit(total_qubits)

        # Append all gates
        for c in circuits:
            for gate in c.gates:
                result.gates.append(gate)
            result.n_bits = max(result.n_bits, c.n_bits)

        return result

    if name:
        composed.name = name
    else:
        composed.name = "_+_".join(m.name for m in modules)

    return composed


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "Module",
    "ModuleError",
    "module",
    "module_with_params",
    "compose_modules",
]