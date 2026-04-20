"""
Quantum Circuit Class for open-Quanta.

This module provides the Circuit class for building and manipulating
quantum circuits with a clean, fluent Python API.

Example:
    from openquanta import Circuit, gates

    c = Circuit(2)
    c.apply(gates.H, 0)
    c.apply(gates.CNOT, 0, 1)
    c.measure_all()
    result = c.simulate()
"""

from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
import copy


class CircuitError(Exception):
    """Base exception for Circuit errors."""
    pass


class QubitError(CircuitError):
    """Raised when qubit index is invalid."""
    pass


class GateError(CircuitError):
    """Raised when gate operation fails."""
    pass


class Circuit:
    """
    Quantum circuit representation and manipulation.

    The Circuit class stores a sequence of quantum gates and measurements,
    providing methods to build, modify, and execute quantum circuits.

    Attributes:
        n_qubits (int): Number of qubits in the circuit
        n_bits (int): Number of classical bits for measurement
        gates (List[Gate]): Sequence of gates in the circuit
        name (str): Optional name for the circuit

    Example:
        # Create a Bell state
        c = Circuit(2, name="BellState")
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)
        c.measure_all()
    """

    def __init__(self, n_qubits: int, n_bits: Optional[int] = None, name: str = ""):
        """
        Initialize a quantum circuit.

        Args:
            n_qubits: Number of qubits in the circuit
            n_bits: Number of classical bits (default: same as n_qubits)
            name: Optional name for the circuit

        Raises:
            ValueError: If n_qubits < 1
        """
        if n_qubits < 1:
            raise ValueError(f"Circuit must have at least 1 qubit, got {n_qubits}")

        self.n_qubits = n_qubits
        self.n_bits = n_bits if n_bits is not None else n_qubits
        self.name = name
        self.gates: List[Any] = []
        self._measurements: Dict[int, int] = {}  # qubit -> bit mapping

    # ========================================================================
    # GATE APPLICATION METHODS
    # ========================================================================

    def apply(
        self,
        gate: Union[Callable, Any],
        *args,
        **kwargs
    ) -> 'Circuit':
        """
        Apply a gate to the circuit.

        Supports multiple calling conventions:
        1. Pass gate object directly: c.apply(gates.H(0))
        2. Pass gate function with args: c.apply(gates.H, 0)
        3. Pass gate name as string: c.apply("H", 0)

        Args:
            gate: Gate object, gate function, or gate name string
            *args: Arguments for the gate (qubit indices, parameters)
            **kwargs: Keyword arguments for the gate

        Returns:
            self (for method chaining)

        Raises:
            GateError: If gate application fails
            QubitError: If qubit index is out of range

        Example:
            c = Circuit(2)
            c.apply(gates.H, 0)           # Function style
            c.apply(gates.CNOT, 0, 1)     # Two-qubit gate
            c.apply(gates.RX, 0, 0.5)     # Parametric gate
            c.apply(gates.H(0))           # Direct gate object
        """
        try:
            gate_obj = self._resolve_gate(gate, *args, **kwargs)
            self._validate_gate(gate_obj)
            self.gates.append(gate_obj)
            return self
        except Exception as e:
            raise GateError(f"Failed to apply gate: {e}") from e

    def _resolve_gate(
        self,
        gate: Union[Callable, Any],
        *args,
        **kwargs
    ) -> Any:
        """Resolve gate input to a Gate object."""
        # Import here to avoid circular dependency
        from .gates import Gate

        # Case 1: Already a Gate object
        if isinstance(gate, Gate):
            return gate

        # Case 2: Callable (gate function like gates.H)
        if callable(gate):
            result = gate(*args, **kwargs)
            if isinstance(result, Gate):
                return result
            raise GateError(f"Gate function {gate} did not return a Gate object")

        # Case 3: String gate name
        if isinstance(gate, str):
            return self._gate_from_name(gate, *args, **kwargs)

        raise GateError(f"Unknown gate type: {type(gate)}")

    def _gate_from_name(self, name: str, *args, **kwargs) -> Any:
        """Create a gate from its name string."""
        from . import gates

        gate_func = getattr(gates, name, None)
        if gate_func is None:
            raise GateError(f"Unknown gate name: {name}")

        return gate_func(*args, **kwargs)

    def _validate_gate(self, gate: Any) -> None:
        """Validate that gate's qubits are within circuit bounds."""
        for qubit in gate.targets:
            if qubit < 0 or qubit >= self.n_qubits:
                raise QubitError(
                    f"Qubit index {qubit} out of range [0, {self.n_qubits - 1}]"
                )

    # ========================================================================
    # CONVENIENCE METHODS FOR COMMON GATES
    # ========================================================================

    def h(self, qubit: int) -> 'Circuit':
        """Apply Hadamard gate."""
        return self.apply("H", qubit)

    def x(self, qubit: int) -> 'Circuit':
        """Apply X (NOT) gate."""
        return self.apply("X", qubit)

    def y(self, qubit: int) -> 'Circuit':
        """Apply Y gate."""
        return self.apply("Y", qubit)

    def z(self, qubit: int) -> 'Circuit':
        """Apply Z gate."""
        return self.apply("Z", qubit)

    def s(self, qubit: int) -> 'Circuit':
        """Apply S gate."""
        return self.apply("S", qubit)

    def t(self, qubit: int) -> 'Circuit':
        """Apply T gate."""
        return self.apply("T", qubit)

    def cx(self, control: int, target: int) -> 'Circuit':
        """Apply CNOT (CX) gate."""
        return self.apply("CNOT", control, target)

    def cnot(self, control: int, target: int) -> 'Circuit':
        """Apply CNOT gate (alias for cx)."""
        return self.cx(control, target)

    def cz(self, control: int, target: int) -> 'Circuit':
        """Apply CZ gate."""
        return self.apply("CZ", control, target)

    def swap(self, qubit1: int, qubit2: int) -> 'Circuit':
        """Apply SWAP gate."""
        return self.apply("SWAP", qubit1, qubit2)

    def ccx(self, control1: int, control2: int, target: int) -> 'Circuit':
        """Apply Toffoli (CCX) gate."""
        return self.apply("CCX", control1, control2, target)

    def toffoli(self, control1: int, control2: int, target: int) -> 'Circuit':
        """Apply Toffoli gate (alias for ccx)."""
        return self.ccx(control1, control2, target)

    def rx(self, qubit: int, theta: float) -> 'Circuit':
        """Apply RX rotation gate."""
        return self.apply("RX", qubit, theta)

    def ry(self, qubit: int, theta: float) -> 'Circuit':
        """Apply RY rotation gate."""
        return self.apply("RY", qubit, theta)

    def rz(self, qubit: int, theta: float) -> 'Circuit':
        """Apply RZ rotation gate."""
        return self.apply("RZ", qubit, theta)

    # ========================================================================
    # MEASUREMENT METHODS
    # ========================================================================

    def measure(self, qubit: int, bit: Optional[int] = None) -> 'Circuit':
        """
        Measure a single qubit into a classical bit.

        Args:
            qubit: Qubit index to measure
            bit: Classical bit index (default: same as qubit)

        Returns:
            self (for chaining)

        Raises:
            QubitError: If qubit index is invalid
        """
        if qubit < 0 or qubit >= self.n_qubits:
            raise QubitError(f"Qubit {qubit} out of range")

        bit = bit if bit is not None else qubit
        self._measurements[qubit] = bit
        self.n_bits = max(self.n_bits, bit + 1)

        from .gates import Measure
        self.gates.append(Measure(qubit, bit))
        return self

    def measure_all(self) -> 'Circuit':
        """
        Measure all qubits.

        Measures each qubit i to classical bit i.

        Returns:
            self (for chaining)
        """
        for i in range(self.n_qubits):
            self.measure(i, i)
        return self

    def measure_range(
        self,
        qubits: List[int],
        bits: Optional[List[int]] = None
    ) -> 'Circuit':
        """
        Measure multiple qubits.

        Args:
            qubits: List of qubit indices to measure
            bits: List of classical bit indices (default: same as qubits)

        Returns:
            self (for chaining)
        """
        bits = bits or qubits
        if len(qubits) != len(bits):
            raise ValueError("qubits and bits must have same length")

        for q, b in zip(qubits, bits):
            self.measure(q, b)
        return self

    # ========================================================================
    # BARRIER AND STRUCTURE
    # ========================================================================

    def barrier(self, qubits: Optional[List[int]] = None) -> 'Circuit':
        """
        Add a barrier to the circuit.

        Barriers prevent optimization across them and are useful
        for visualization.

        Args:
            qubits: Specific qubits for barrier (default: all)

        Returns:
            self (for chaining)
        """
        from .gates import Barrier
        qubits = qubits or list(range(self.n_qubits))
        self.gates.append(Barrier(qubits))
        return self

    def reset(self, qubit: int) -> 'Circuit':
        """
        Reset a qubit to |0⟩ state.

        Args:
            qubit: Qubit to reset

        Returns:
            self (for chaining)
        """
        return self.apply("Reset", qubit)

    def reset_all(self) -> 'Circuit':
        """Reset all qubits to |0⟩."""
        for i in range(self.n_qubits):
            self.reset(i)
        return self

    # ========================================================================
    # CIRCUIT MANIPULATION
    # ========================================================================

    def copy(self, name: Optional[str] = None) -> 'Circuit':
        """
        Create a deep copy of the circuit.

        Args:
            name: Name for the copied circuit

        Returns:
            New Circuit object
        """
        new_circuit = Circuit(self.n_qubits, self.n_bits, name or self.name)
        new_circuit.gates = [g.copy() if hasattr(g, 'copy') else copy.deepcopy(g)
                             for g in self.gates]
        new_circuit._measurements = self._measurements.copy()
        return new_circuit

    def append(self, other: 'Circuit') -> 'Circuit':
        """
        Append another circuit to this one.

        Args:
            other: Circuit to append

        Returns:
            self (for chaining)

        Raises:
            ValueError: If circuits have incompatible qubit counts
        """
        if other.n_qubits > self.n_qubits:
            raise ValueError(
                f"Cannot append circuit with {other.n_qubits} qubits "
                f"to circuit with {self.n_qubits} qubits"
            )

        self.gates.extend(other.gates.copy())
        self._measurements.update(other._measurements)
        self.n_bits = max(self.n_bits, other.n_bits)
        return self

    def compose(self, other: 'Circuit', qubits: Optional[List[int]] = None) -> 'Circuit':
        """
        Compose with another circuit on specific qubits.

        Args:
            other: Circuit to compose
            qubits: Qubits to compose onto (default: first n qubits)

        Returns:
            New composed circuit
        """
        qubits = qubits or list(range(other.n_qubits))

        if len(qubits) != other.n_qubits:
            raise ValueError(
                f"Need {other.n_qubits} qubit mappings, got {len(qubits)}"
            )

        new_circuit = self.copy()

        # Map gates from other circuit to specified qubits
        for gate in other.gates:
            new_gate = gate.copy()
            new_gate.targets = [qubits[t] for t in gate.targets]
            new_circuit.gates.append(new_gate)

        return new_circuit

    def insert(self, index: int, gate: Any) -> 'Circuit':
        """
        Insert a gate at a specific position.

        Args:
            index: Position to insert
            gate: Gate to insert

        Returns:
            self (for chaining)
        """
        gate_obj = self._resolve_gate(gate)
        self._validate_gate(gate_obj)
        self.gates.insert(index, gate_obj)
        return self

    def remove(self, index: int) -> 'Circuit':
        """
        Remove gate at index.

        Args:
            index: Index of gate to remove

        Returns:
            self (for chaining)
        """
        if 0 <= index < len(self.gates):
            self.gates.pop(index)
        return self

    def pop(self, index: int = -1) -> Any:
        """
        Remove and return gate at index.

        Args:
            index: Index of gate (default: last)

        Returns:
            The removed gate
        """
        return self.gates.pop(index)

    # ========================================================================
    # CIRCUIT PROPERTIES
    # ========================================================================

    @property
    def depth(self) -> int:
        """
        Calculate circuit depth.

        Depth is the number of gate layers, where gates in
        the same layer act on different qubits.

        Returns:
            Circuit depth
        """
        if not self.gates:
            return 0

        qubit_depths = [0] * self.n_qubits

        for gate in self.gates:
            max_depth = max(qubit_depths[q] for q in gate.targets if q < self.n_qubits)
            for q in gate.targets:
                if q < self.n_qubits:
                    qubit_depths[q] = max_depth + 1

        return max(qubit_depths)

    @property
    def size(self) -> int:
        """Number of gates in the circuit."""
        return len(self.gates)

    @property
    def num_measurements(self) -> int:
        """Number of measurement operations."""
        return len(self._measurements)

    def count_gates(self, gate_name: Optional[str] = None) -> int:
        """
        Count gates by name.

        Args:
            gate_name: Specific gate name (default: count all)

        Returns:
            Number of matching gates
        """
        if gate_name:
            return sum(1 for g in self.gates if g.name == gate_name)
        return len(self.gates)

    def get_gate(self, index: int) -> Any:
        """Get gate at index."""
        return self.gates[index]

    def get_gates_by_name(self, name: str) -> List[Any]:
        """Get all gates with a specific name."""
        return [g for g in self.gates if g.name == name]

    # ========================================================================
    # EXECUTION METHODS
    # ========================================================================

    def simulate(
        self,
        shots: int = 1000,
        backend: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Simulate the circuit locally.

        Args:
            shots: Number of simulation shots
            backend: Optional backend name (default: "simulator")

        Returns:
            Dictionary mapping measurement outcomes to counts
            e.g., {'00': 500, '11': 500}
        """
        from .backends import SimulatorBackend

        sim = SimulatorBackend()
        return sim.execute(self, shots=shots)

    def run(
        self,
        backend: str = "simulator",
        shots: int = 1000,
        **kwargs
    ) -> Dict[str, int]:
        """
        Run the circuit on a specified backend.

        Args:
            backend: Backend name ("simulator", "ibm", etc.)
            shots: Number of shots
            **kwargs: Additional backend-specific options

        Returns:
            Dictionary of measurement results

        Raises:
            ValueError: If backend is not available
        """
        backend = backend.lower()

        if backend == "simulator":
            return self.simulate(shots=shots)

        # Try to import and use hardware backends
        if backend.startswith("ibm"):
            try:
                from .backends import IBMBackend
                ibm = IBMBackend(**kwargs)
                return ibm.execute(self, shots=shots)
            except ImportError:
                raise ValueError(
                    "IBM backend not available. "
                    "Install with: pip install qiskit-ibm-runtime"
                )

        raise ValueError(f"Unknown backend: {backend}")

    def to_qir(self) -> str:
        """
        Convert circuit to QIR (Quantum Intermediate Representation).

        Returns:
            QIR code as string
        """
        from .qir_bridge import circuit_to_qir
        return circuit_to_qir(self)

    # ========================================================================
    # VISUALIZATION
    # ========================================================================

    def draw(self, output: str = "text") -> str:
        """
        Draw the circuit.

        Args:
            output: Output format ("text", "matplotlib", "latex")

        Returns:
            Circuit diagram as string (for text output)
        """
        if output == "text":
            return self._draw_text()

        # For other outputs, convert to Qiskit and use their drawing
        try:
            from .backends.simulator import SimulatorBackend
            qc = SimulatorBackend()._to_qiskit(self)
            return qc.draw(output=output)
        except ImportError:
            return self._draw_text()

    def _draw_text(self) -> str:
        """Generate ASCII art circuit diagram."""
        lines = []
        lines.append(f"Circuit: {self.name or 'unnamed'}")
        lines.append(f"Qubits: {self.n_qubits}, Gates: {self.size}, Depth: {self.depth}")
        lines.append("")

        # Create grid using ASCII characters only
        wire_width = max(3, self.size * 4)
        wires = [f"q{i}: " + "-" * wire_width for i in range(self.n_qubits)]
        c_wires = [f"c{i}: " + " " * wire_width for i in range(self.n_bits)]

        # Add gates
        col = 0
        for gate in self.gates:
            gate_str = self._gate_symbol(gate)
            for q in gate.targets:
                if q < len(wires):
                    pos = 4 + col * 4
                    wire = list(wires[q])
                    for i, c in enumerate(gate_str):
                        if pos + i < len(wire):
                            wire[pos + i] = c
                    wires[q] = "".join(wire)
            col += 1

        lines.extend(wires)
        if self._measurements:
            lines.append("")
            lines.extend(c_wires)

        return "\n".join(lines)

    def _gate_symbol(self, gate: Any) -> str:
        """Get symbol for gate in ASCII diagram."""
        symbols = {
            "H": "[H]",
            "X": "[X]",
            "Y": "[Y]",
            "Z": "[Z]",
            "S": "[S]",
            "T": "[T]",
            "CNOT": "─X─",
            "CZ": "─Z─",
            "SWAP": "─x─",
            "Measure": "─M─",
            "Barrier": "───",
        }
        return symbols.get(gate.name, f"[{gate.name[:2]}]")

    # ========================================================================
    # SPECIAL METHODS
    # ========================================================================

    def __len__(self) -> int:
        """Return number of gates."""
        return self.size

    def __getitem__(self, index: int) -> Any:
        """Get gate at index."""
        return self.gates[index]

    def __iter__(self):
        """Iterate over gates."""
        return iter(self.gates)

    def __repr__(self) -> str:
        return (
            f"Circuit(n_qubits={self.n_qubits}, "
            f"n_bits={self.n_bits}, gates={self.size})"
        )

    def __str__(self) -> str:
        return self.draw()

    def __add__(self, other: 'Circuit') -> 'Circuit':
        """Concatenate two circuits."""
        new = self.copy()
        new.append(other)
        return new

    def __iadd__(self, other: 'Circuit') -> 'Circuit':
        """Append circuit in-place."""
        self.append(other)
        return self

    # ========================================================================
    # ADVANCED METHODS
    # ========================================================================

    def inverse(self) -> 'Circuit':
        """
        Create the inverse (adjoint) of the circuit.

        Returns:
            New circuit with gates in reverse order, inverted
        """
        inv_circuit = Circuit(self.n_qubits, self.n_bits, f"{self.name}_inv")

        # Reverse gates and invert each
        for gate in reversed(self.gates):
            inv_gate = self._invert_gate(gate)
            inv_circuit.gates.append(inv_gate)

        return inv_circuit

    def _invert_gate(self, gate: Any) -> Any:
        """Invert a single gate."""
        gate = gate.copy()

        # Self-inverse gates
        if gate.name in ("H", "X", "Y", "Z", "CNOT", "CZ", "SWAP"):
            return gate

        # Conjugate gates
        if gate.name == "S":
            gate.name = "Sdg"
            return gate
        if gate.name == "T":
            gate.name = "Tdg"
            return gate

        # Inverse of rotation: negate angle
        if gate.name in ("RX", "RY", "RZ", "Phase"):
            gate.params = [-p for p in gate.params]
            return gate

        # Default: return as-is with note
        return gate

    def power(self, n: int) -> 'Circuit':
        """
        Repeat circuit n times.

        Args:
            n: Number of repetitions

        Returns:
            New circuit with n copies
        """
        if n < 0:
            raise ValueError(f"Power must be non-negative, got {n}")

        result = Circuit(self.n_qubits, self.n_bits, f"{self.name}^{n}")
        for _ in range(n):
            result.append(self)
        return result

    def control(self, control_qubits: Union[int, List[int]]) -> 'Circuit':
        """
        Create controlled version of the circuit.

        Args:
            control_qubits: Control qubit(s) to add

        Returns:
            New controlled circuit
        """
        if isinstance(control_qubits, int):
            control_qubits = [control_qubits]

        new_n_qubits = self.n_qubits + len(control_qubits)
        new_circuit = Circuit(new_n_qubits, self.n_bits, f"C-{self.name}")

        # Add control prefix to each gate
        offset = len(control_qubits)
        for gate in self.gates:
            new_gate = gate.copy()
            new_gate.targets = [t + offset for t in gate.targets]
            new_gate.control = control_qubits[0]  # Primary control
            new_gate.name = f"C{gate.name}"
            new_circuit.gates.append(new_gate)

        return new_circuit


# ============================================================================
# CIRCUIT FACTORY FUNCTIONS
# ============================================================================

def QuantumCircuit(n_qubits: int, n_bits: Optional[int] = None, name: str = "") -> Circuit:
    """
    Factory function for creating quantum circuits.
    Alias for Circuit constructor for Qiskit familiarity.

    Args:
        n_qubits: Number of qubits
        n_bits: Number of classical bits
        name: Circuit name

    Returns:
        New Circuit instance
    """
    return Circuit(n_qubits, n_bits, name)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "Circuit",
    "CircuitError",
    "QubitError",
    "GateError",
    "QuantumCircuit",
]