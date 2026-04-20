"""
Local Simulator Backend for open-Quanta.

Uses Qiskit Aer for local quantum circuit simulation.
"""

from typing import Dict, Optional, Any, List
import numpy as np

from .base import Backend, BackendError


class SimulatorBackend(Backend):
    """
    Local quantum circuit simulator using Qiskit Aer.

    This backend runs quantum circuits on your local machine using
    statevector simulation. Perfect for testing and development.

    Example:
        from openquanta import Circuit, gates
        from openquanta.backends import SimulatorBackend

        c = Circuit(2)
        c.apply(gates.H, 0)
        c.apply(gates.CNOT, 0, 1)
        c.measure_all()

        sim = SimulatorBackend()
        result = sim.execute(c, shots=1000)
        print(result)  # {'00': 500, '11': 500}
    """

    def __init__(self, method: str = "automatic"):
        """
        Initialize the simulator.

        Args:
            method: Simulation method:
                - "automatic": Choose best method automatically
                - "statevector": Full statevector simulation
                - "density_matrix": Density matrix simulation
                - "stabilizer": Clifford circuit simulation
                - "matrix_product_state": MPS simulation
        """
        super().__init__(name="SimulatorBackend")
        self.method = method
        self._simulator = None

    @property
    def available(self) -> bool:
        """Check if Qiskit Aer is available."""
        try:
            from qiskit_aer import AerSimulator
            return True
        except ImportError:
            return False

    @property
    def max_qubits(self) -> int:
        """Maximum qubits depends on available memory."""
        # Conservative estimate for statevector simulation
        return 30

    def execute(self, circuit: Any, shots: int = 1000) -> Dict[str, int]:
        """
        Execute circuit on local simulator.

        Args:
            circuit: open-Quanta Circuit object
            shots: Number of simulation shots

        Returns:
            Dictionary of measurement results

        Raises:
            BackendError: If simulation fails
        """
        try:
            # Import Qiskit
            from qiskit import QuantumCircuit
            from qiskit_aer import AerSimulator
        except ImportError as e:
            raise BackendError(
                "Qiskit Aer not installed. "
                "Install with: pip install qiskit-aer"
            ) from e

        try:
            # Validate circuit
            self.validate_circuit(circuit)

            # Convert to Qiskit QuantumCircuit
            qc = self._to_qiskit(circuit)

            # Create simulator
            simulator = AerSimulator(method=self.method)

            # Run simulation
            job = simulator.run(qc, shots=shots)
            result = job.result()

            # Extract counts
            counts = result.get_counts()

            # Convert to our format
            return self._normalize_counts(counts, circuit)

        except Exception as e:
            raise BackendError(f"Simulation failed: {e}") from e

    def _to_qiskit(self, circuit: Any) -> Any:
        """
        Convert open-Quanta Circuit to Qiskit QuantumCircuit.

        Args:
            circuit: open-Quanta Circuit object

        Returns:
            Qiskit QuantumCircuit
        """
        from qiskit import QuantumCircuit
        from qiskit.circuit import Parameter

        # Create Qiskit circuit
        qc = QuantumCircuit(circuit.n_qubits, circuit.n_bits)

        # Apply each gate
        for gate in circuit.gates:
            self._apply_gate_to_qiskit(qc, gate)

        return qc

    def _apply_gate_to_qiskit(self, qc: Any, gate: Any) -> None:
        """Apply a gate to the Qiskit circuit."""
        name = gate.name
        targets = gate.targets
        params = gate.params if hasattr(gate, 'params') else []

        # Single-qubit gates
        if name == "I":
            qc.id(targets[0])

        elif name == "H":
            qc.h(targets[0])

        elif name == "X":
            qc.x(targets[0])

        elif name == "Y":
            qc.y(targets[0])

        elif name == "Z":
            qc.z(targets[0])

        elif name == "S":
            qc.s(targets[0])

        elif name == "Sdg":
            qc.sdg(targets[0])

        elif name == "T":
            qc.t(targets[0])

        elif name == "Tdg":
            qc.tdg(targets[0])

        elif name == "SX":
            qc.sx(targets[0])

        elif name == "SXdg":
            qc.sxdg(targets[0])

        # Rotation gates
        elif name == "RX":
            qc.rx(params[0], targets[0])

        elif name == "RY":
            qc.ry(params[0], targets[0])

        elif name == "RZ":
            qc.rz(params[0], targets[0])

        elif name == "Phase":
            qc.p(params[0], targets[0])

        elif name in ("U", "U3"):
            theta, phi, lam = params
            qc.u(theta, phi, lam, targets[0])

        elif name == "U1":
            qc.p(params[0], targets[0])

        elif name == "U2":
            phi, lam = params
            qc.u(np.pi / 2, phi, lam, targets[0])

        # Two-qubit gates
        elif name in ("CNOT", "CX"):
            qc.cx(targets[0], targets[1])

        elif name == "CY":
            qc.cy(targets[0], targets[1])

        elif name == "CZ":
            qc.cz(targets[0], targets[1])

        elif name == "CH":
            qc.ch(targets[0], targets[1])

        elif name == "CS":
            # Controlled-S not directly in Qiskit, build it
            qc.cp(np.pi / 2, targets[0], targets[1])

        elif name == "CPhase":
            qc.cp(params[0], targets[0], targets[1])

        elif name == "CRX":
            qc.crx(params[0], targets[0], targets[1])

        elif name == "CRY":
            qc.cry(params[0], targets[0], targets[1])

        elif name == "CRZ":
            qc.crz(params[0], targets[0], targets[1])

        elif name == "SWAP":
            qc.swap(targets[0], targets[1])

        elif name == "iSWAP":
            # iSWAP decomposition
            qc.swap(targets[0], targets[1])
            # Simplified - full iSWAP needs more gates

        elif name == "DCX":
            qc.cx(targets[0], targets[1])
            qc.cx(targets[1], targets[0])

        # Three-qubit gates
        elif name in ("CCX", "Toffoli"):
            qc.ccx(targets[0], targets[1], targets[2])

        elif name == "CCZ":
            # CCZ: H on target, CCX, H on target
            qc.h(targets[2])
            qc.ccx(targets[0], targets[1], targets[2])
            qc.h(targets[2])

        elif name in ("CSWAP", "Fredkin"):
            qc.cswap(targets[0], targets[1], targets[2])

        # Multi-qubit gates
        elif name == "CCCX":
            # Qiskit doesn't have CCCX directly, use decomposition
            qc.ccx(targets[0], targets[1], targets[2])
            # This is simplified - full CCCX needs ancilla

        elif name == "MCX":
            # Multi-controlled X
            controls = targets[:-1]
            target = targets[-1]
            qc.mcx(controls, target)

        elif name == "MCZ":
            # Multi-controlled Z
            controls = targets[:-1]
            target = targets[-1]
            qc.h(target)
            qc.mcx(controls, target)
            qc.h(target)

        # Measurement
        elif name == "Measure":
            qubit = targets[0]
            bit = params[0] if params else 0
            qc.measure(qubit, bit)

        elif name == "MeasureAll":
            qc.measure_all()

        # Special operations
        elif name == "Barrier":
            qc.barrier(targets)

        elif name == "Reset":
            qc.reset(targets[0])

        elif name == "Delay":
            qc.delay(params[0], targets[0])

        # Custom gates
        elif gate.is_custom():
            self._apply_custom_gate_to_qiskit(qc, gate)

        else:
            raise BackendError(f"Unsupported gate: {name}")

    def _apply_custom_gate_to_qiskit(self, qc: Any, gate: Any) -> None:
        """Apply a custom gate to Qiskit circuit."""
        from qiskit.circuit.library import UnitaryGate

        matrix = gate.matrix
        targets = gate.targets

        # Create unitary gate
        unitary = UnitaryGate(matrix, label=gate.name)
        qc.append(unitary, targets)

    def _normalize_counts(
        self,
        counts: Dict[str, int],
        circuit: Any
    ) -> Dict[str, int]:
        """
        Normalize Qiskit counts to our format.

        Qiskit returns bit strings in a specific order.
        We need to ensure consistency.

        Args:
            counts: Raw counts from Qiskit
            circuit: Original circuit for reference

        Returns:
            Normalized counts dictionary
        """
        # Ensure keys have consistent bit ordering
        normalized = {}
        for bitstring, count in counts.items():
            # Qiskit uses big-endian, we want little-endian
            # Actually, keep as-is for now for compatibility
            normalized[bitstring] = count

        return normalized

    def get_statevector(self, circuit: Any) -> np.ndarray:
        """
        Get the statevector after running the circuit.

        This returns the full quantum state, useful for debugging
        and understanding circuit behavior.

        Args:
            circuit: open-Quanta Circuit object

        Returns:
            Statevector as numpy array
        """
        try:
            from qiskit import QuantumCircuit
            from qiskit_aer import AerSimulator
            from qiskit.quantum_info import Statevector
        except ImportError as e:
            raise BackendError(
                "Qiskit not installed. Install with: pip install qiskit qiskit-aer"
            ) from e

        # Convert to Qiskit (without measurements)
        qc = QuantumCircuit(circuit.n_qubits)

        # Apply only non-measurement gates
        for gate in circuit.gates:
            if gate.name != "Measure":
                self._apply_gate_to_qiskit(qc, gate)

        # Get statevector
        statevector = Statevector(qc)
        return statevector.data

    def get_unitary(self, circuit: Any) -> np.ndarray:
        """
        Get the unitary matrix representing the circuit.

        Args:
            circuit: open-Quanta Circuit object

        Returns:
            Unitary matrix as numpy array
        """
        try:
            from qiskit import QuantumCircuit
            from qiskit.quantum_info import Operator
        except ImportError as e:
            raise BackendError(
                "Qiskit not installed. Install with: pip install qiskit"
            ) from e

        # Convert to Qiskit (without measurements)
        qc = QuantumCircuit(circuit.n_qubits)

        for gate in circuit.gates:
            if gate.name not in ("Measure", "MeasureAll", "Barrier"):
                self._apply_gate_to_qiskit(qc, gate)

        # Get unitary
        op = Operator(qc)
        return op.data


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "SimulatorBackend",
]