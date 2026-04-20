# open-Quanta Build Plan

## Build Philosophy

**Build modular. Build one at a time. Test before moving forward.**

Each phase:
1. Builds ONE component
2. Tests it independently
3. Verifies it works
4. Then connects to previous components
5. Tests the connection
6. Only then move to next phase

If any error occurs, we know exactly which component caused it.

---

## Phase 0: Setup (Day 1)

### Goal
Create project structure and install dependencies.

### Tasks
- [ ] Create folder structure
- [ ] Initialize git repository
- [ ] Create pyproject.toml with dependencies
- [ ] Create virtual environment
- [ ] Install all dependencies
- [ ] Verify imports work

### Files to Create
```
open-quanta/
├── pyproject.toml
├── .gitignore
├── README.md
├── openquanta/
│   └── __init__.py (empty, just package marker)
└── tests/
    └── __init__.py (empty)
```

### Verification
```python
# Run this in Python
import pyqir
import qiskit
from qiskit_aer import AerSimulator

print("All dependencies installed correctly")
```

### Success Criteria
- `pip install -e .` works
- All imports succeed
- No errors

---

## Phase 1: Gate Definitions (Day 2)

### Goal
Create quantum gate objects that can be used to build circuits.

### Tasks
- [ ] Define base Gate class
- [ ] Implement single-qubit gates (H, X, Y, Z)
- [ ] Implement rotation gates (RX, RY, RZ)
- [ ] Implement two-qubit gates (CNOT, CZ)
- [ ] Implement measurement gate
- [ ] Write unit tests for each gate
- [ ] All tests pass

### Files to Create
```
openquanta/
├── __init__.py
└── gates.py

tests/
└── test_gates.py
```

### Code Structure
```python
# gates.py

class Gate:
    """Base class for all quantum gates."""
    def __init__(self, name: str, targets: list, params: list = None):
        self.name = name
        self.targets = targets
        self.params = params or []

# Single-qubit gates
H = lambda q: Gate("H", [q])
X = lambda q: Gate("X", [q])
Y = lambda q: Gate("Y", [q])
Z = lambda q: Gate("Z", [q])

# Rotation gates
RX = lambda q, theta: Gate("RX", [q], [theta])
RY = lambda q, theta: Gate("RY", [q], [theta])
RZ = lambda q, theta: Gate("RZ", [q], [theta])

# Two-qubit gates
CNOT = lambda c, t: Gate("CNOT", [c, t])
CZ = lambda c, t: Gate("CZ", [c, t])

# Measurement
Measure = lambda q, c: Gate("Measure", [q], [c])
```

### Verification
```python
# test_gates.py

from openquanta import gates

def test_single_qubit_gates():
    h = gates.H(0)
    assert h.name == "H"
    assert h.targets == [0]
    assert h.params == []

def test_rotation_gates():
    rx = gates.RX(0, 0.5)
    assert rx.name == "RX"
    assert rx.params == [0.5]

def test_two_qubit_gates():
    cnot = gates.CNOT(0, 1)
    assert cnot.name == "CNOT"
    assert cnot.targets == [0, 1]
```

### Success Criteria
- All gates create correctly
- All tests pass
- Gate objects store name, targets, params correctly

---

## Phase 2: Circuit Class (Day 3)

### Goal
Create Circuit class that stores qubits and gate sequence.

### Tasks
- [ ] Define Circuit class
- [ ] Implement `__init__` with qubit count
- [ ] Implement `apply(gate, *qubits)` method
- [ ] Implement `measure_all()` method
- [ ] Implement `measure(qubit, classical_bit)` method
- [ ] Implement `copy()` method
- [ ] Write unit tests
- [ ] All tests pass

### Files to Create/Modify
```
openquanta/
├── __init__.py
├── gates.py
└── circuit.py          # NEW

tests/
├── test_gates.py
└── test_circuit.py     # NEW
```

### Code Structure
```python
# circuit.py

from .gates import Gate, Measure

class Circuit:
    def __init__(self, n_qubits: int):
        self.n_qubits = n_qubits
        self.n_bits = 0
        self.gates = []
        self.measurements = {}

    def apply(self, gate, *args):
        """Apply a gate to the circuit."""
        if callable(gate):
            # gate is a function like gates.H
            gate_obj = gate(*args)
        else:
            gate_obj = gate
        self.gates.append(gate_obj)
        return self  # Allow chaining

    def measure(self, qubit: int, bit: int):
        """Measure a qubit to a classical bit."""
        self.measurements[qubit] = bit
        self.n_bits = max(self.n_bits, bit + 1)
        self.gates.append(Measure(qubit, bit))
        return self

    def measure_all(self):
        """Measure all qubits."""
        for i in range(self.n_qubits):
            self.measure(i, i)
        return self

    def copy(self):
        """Create a copy of the circuit."""
        c = Circuit(self.n_qubits)
        c.n_bits = self.n_bits
        c.gates = self.gates.copy()
        c.measurements = self.measurements.copy()
        return c
```

### Verification
```python
# test_circuit.py

from openquanta import Circuit, gates

def test_circuit_creation():
    c = Circuit(2)
    assert c.n_qubits == 2
    assert c.gates == []

def test_apply_single_gate():
    c = Circuit(2)
    c.apply(gates.H, 0)
    assert len(c.gates) == 1
    assert c.gates[0].name == "H"

def test_apply_multiple_gates():
    c = Circuit(2)
    c.apply(gates.H, 0)
    c.apply(gates.CNOT, 0, 1)
    assert len(c.gates) == 2

def test_measure_all():
    c = Circuit(2)
    c.apply(gates.H, 0)
    c.measure_all()
    assert len(c.measurements) == 2

def test_chaining():
    c = Circuit(2).apply(gates.H, 0).apply(gates.CNOT, 0, 1).measure_all()
    assert len(c.gates) == 3
```

### Success Criteria
- Circuit stores qubits correctly
- Gates append in order
- Measure works correctly
- Chaining works
- All tests pass

---

## Phase 3: QIR Bridge — Basic (Day 4-5)

### Goal
Convert Circuit objects to QIR code using PyQIR.

### Tasks
- [ ] Create QIR bridge module
- [ ] Implement conversion for H gate
- [ ] Implement conversion for X, Y, Z gates
- [ ] Implement conversion for CNOT, CZ
- [ ] Implement conversion for RX, RY, RZ
- [ ] Implement conversion for Measure
- [ ] Handle qubit allocation
- [ ] Handle classical bit allocation
- [ ] Write unit tests
- [ ] All tests pass

### Files to Create/Modify
```
openquanta/
├── __init__.py
├── gates.py
├── circuit.py
└── qir_bridge.py      # NEW

tests/
├── test_gates.py
├── test_circuit.py
└── test_qir_bridge.py # NEW
```

### Code Structure
```python
# qir_bridge.py

import pyqir
from .circuit import Circuit

class QIRBridge:
    def __init__(self, circuit: Circuit):
        self.circuit = circuit

    def compile(self) -> str:
        """Convert circuit to QIR code."""
        # Create PyQIR module
        module = pyqir.SimpleModule(
            "circuit",
            self.circuit.n_qubits,
            self.circuit.n_bits
        )

        # Apply each gate
        for gate in self.circuit.gates:
            self._apply_gate(module, gate)

        return module.ir()

    def _apply_gate(self, module, gate):
        """Apply a single gate to the module."""
        qubits = module.qubits
        results = module.results

        if gate.name == "H":
            pyqir.h(qubits[gate.targets[0]])

        elif gate.name == "X":
            pyqir.x(qubits[gate.targets[0]])

        elif gate.name == "Y":
            pyqir.y(qubits[gate.targets[0]])

        elif gate.name == "Z":
            pyqir.z(qubits[gate.targets[0]])

        elif gate.name == "CNOT":
            pyqir.cx(qubits[gate.targets[0]], qubits[gate.targets[1]])

        elif gate.name == "CZ":
            pyqir.cz(qubits[gate.targets[0]], qubits[gate.targets[1]])

        elif gate.name == "RX":
            pyqir.rx(gate.params[0], qubits[gate.targets[0]])

        elif gate.name == "RY":
            pyqir.ry(gate.params[0], qubits[gate.targets[0]])

        elif gate.name == "RZ":
            pyqir.rz(gate.params[0], qubits[gate.targets[0]])

        elif gate.name == "Measure":
            pyqir.mz(qubits[gate.targets[0]], results[gate.params[0]])


def circuit_to_qir(circuit: Circuit) -> str:
    """Convenience function to convert circuit to QIR."""
    return QIRBridge(circuit).compile()
```

### Verification
```python
# test_qir_bridge.py

from openquanta import Circuit, gates
from openquanta.qir_bridge import circuit_to_qir

def test_h_gate_to_qir():
    c = Circuit(1).apply(gates.H, 0)
    qir = circuit_to_qir(c)
    assert "h" in qir.lower()

def test_cnot_to_qir():
    c = Circuit(2).apply(gates.CNOT, 0, 1)
    qir = circuit_to_qir(c)
    assert "cx" in qir.lower() or "cnot" in qir.lower()

def test_bell_state_qir():
    c = Circuit(2)
    c.apply(gates.H, 0)
    c.apply(gates.CNOT, 0, 1)
    c.measure_all()

    qir = circuit_to_qir(c)
    assert "h" in qir.lower()
    assert "cx" in qir.lower() or "cnot" in qir.lower()
    assert "mz" in qir.lower() or "measure" in qir.lower()
```

### Success Criteria
- Each gate converts to correct QIR
- Bell state generates valid QIR
- Output is QIR-compatible string
- All tests pass

---

## Phase 4: Simulator Backend (Day 6-7)

### Goal
Execute circuits on local simulator and return results.

### Tasks
- [ ] Create backend base class
- [ ] Create simulator backend using Qiskit Aer
- [ ] Handle QIR → Qiskit conversion (or direct circuit execution)
- [ ] Implement `run(shots)` method
- [ ] Return results as dictionary
- [ ] Write unit tests
- [ ] All tests pass

### Files to Create/Modify
```
openquanta/
├── __init__.py
├── gates.py
├── circuit.py
├── qir_bridge.py
└── backends/
    ├── __init__.py
    ├── base.py          # NEW
    └── simulator.py     # NEW

tests/
├── test_gates.py
├── test_circuit.py
├── test_qir_bridge.py
└── test_backends.py     # NEW
```

### Code Structure
```python
# backends/base.py

from abc import ABC, abstractmethod
from typing import Dict

class Backend(ABC):
    """Abstract base class for all backends."""

    @abstractmethod
    def execute(self, circuit, shots: int = 1000) -> Dict[str, int]:
        """Execute a circuit and return measurement counts."""
        pass
```

```python
# backends/simulator.py

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from .base import Backend

class SimulatorBackend(Backend):
    """Local simulator backend using Qiskit Aer."""

    def __init__(self):
        self.simulator = AerSimulator()

    def execute(self, circuit, shots: int = 1000) -> Dict[str, int]:
        """Execute circuit on local simulator."""
        # Convert our Circuit to Qiskit QuantumCircuit
        qc = self._to_qiskit(circuit)

        # Run simulation
        job = self.simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts()

        return dict(counts)

    def _to_qiskit(self, circuit) -> QuantumCircuit:
        """Convert open-Quanta Circuit to Qiskit QuantumCircuit."""
        qc = QuantumCircuit(circuit.n_qubits, circuit.n_bits)

        for gate in circuit.gates:
            if gate.name == "H":
                qc.h(gate.targets[0])
            elif gate.name == "X":
                qc.x(gate.targets[0])
            elif gate.name == "Y":
                qc.y(gate.targets[0])
            elif gate.name == "Z":
                qc.z(gate.targets[0])
            elif gate.name == "CNOT":
                qc.cx(gate.targets[0], gate.targets[1])
            elif gate.name == "CZ":
                qc.cz(gate.targets[0], gate.targets[1])
            elif gate.name == "RX":
                qc.rx(gate.params[0], gate.targets[0])
            elif gate.name == "RY":
                qc.ry(gate.params[0], gate.targets[0])
            elif gate.name == "RZ":
                qc.rz(gate.params[0], gate.targets[0])
            elif gate.name == "Measure":
                qc.measure(gate.targets[0], gate.params[0])

        return qc
```

### Verification
```python
# test_backends.py

from openquanta import Circuit, gates
from openquanta.backends import SimulatorBackend

def test_bell_state_simulation():
    c = Circuit(2)
    c.apply(gates.H, 0)
    c.apply(gates.CNOT, 0, 1)
    c.measure_all()

    backend = SimulatorBackend()
    result = backend.execute(c, shots=1000)

    # Bell state should give 00 or 11 only
    assert "00" in result or "11" in result
    assert sum(result.values()) == 1000

def test_superposition():
    c = Circuit(1)
    c.apply(gates.H, 0)
    c.measure(0, 0)

    backend = SimulatorBackend()
    result = backend.execute(c, shots=1000)

    # Superposition should give both 0 and 1
    assert "0" in result
    assert "1" in result
```

### Success Criteria
- Bell state gives correct results (00 and 11 only)
- Superposition gives both outcomes
- Results are dictionary format
- All tests pass

---

## Phase 5: Circuit Convenience Methods (Day 8)

### Goal
Add `simulate()` and `run()` methods directly on Circuit class.

### Tasks
- [ ] Add `simulate(shots)` method to Circuit
- [ ] Add `run(backend, shots)` method to Circuit
- [ ] Add `to_qir()` method to Circuit
- [ ] Update `__init__.py` exports
- [ ] Write integration tests
- [ ] All tests pass

### Files to Modify
```
openquanta/
├── __init__.py         # UPDATE
├── circuit.py          # UPDATE
├── gates.py
├── qir_bridge.py
└── backends/
    ├── __init__.py
    ├── base.py
    └── simulator.py
```

### Code Changes
```python
# circuit.py (add methods)

from .backends import SimulatorBackend
from .qir_bridge import circuit_to_qir

class Circuit:
    # ... existing code ...

    def simulate(self, shots: int = 1000) -> Dict[str, int]:
        """Simulate circuit locally."""
        backend = SimulatorBackend()
        return backend.execute(self, shots)

    def run(self, backend_name: str = "simulator", shots: int = 1000) -> Dict[str, int]:
        """Run circuit on specified backend."""
        # For now, only simulator
        if backend_name == "simulator":
            return self.simulate(shots)
        else:
            raise ValueError(f"Unknown backend: {backend_name}")

    def to_qir(self) -> str:
        """Convert circuit to QIR code."""
        return circuit_to_qir(self)
```

### Verification
```python
# tests/integration_test.py

from openquanta import Circuit, gates

def test_bell_state_e2e():
    """End-to-end test: create circuit and simulate."""
    c = Circuit(2)
    c.apply(gates.H, 0)
    c.apply(gates.CNOT, 0, 1)
    c.measure_all()

    # Test simulate method
    result = c.simulate(shots=1000)
    assert sum(result.values()) == 1000

    # Test to_qir method
    qir = c.to_qir()
    assert len(qir) > 0

def test_simple_user_workflow():
    """Test the simplest user workflow."""
    from openquanta import Circuit, gates

    c = Circuit(2)
    c.apply(gates.H, 0)
    c.apply(gates.CNOT, 0, 1)
    c.measure_all()

    result = c.simulate()
    print(result)  # Should show {'00': ~500, '11': ~500}
```

### Success Criteria
- `circuit.simulate()` works
- `circuit.to_qir()` works
- End-to-end test passes
- User workflow is simple

---

## Phase 6: Module System (Day 9-10)

### Goal
Create `@module` decorator for reusable quantum algorithms.

### Tasks
- [ ] Create module decorator
- [ ] Create Module class
- [ ] Implement module composition (combining modules)
- [ ] Create standard modules (BellPair, etc.)
- [ ] Write tests for module system
- [ ] All tests pass

### Files to Create
```
openquanta/
├── modules/
│   ├── __init__.py
│   ├── decorator.py     # NEW
│   └── standard.py      # NEW
```

### Code Structure
```python
# modules/decorator.py

from functools import wraps

class Module:
    """A reusable quantum module."""

    def __init__(self, func, name=None):
        self.func = func
        self.name = name or func.__name__
        self.__doc__ = func.__doc__

    def __call__(self, *args, **kwargs):
        """Build and return the circuit."""
        return self.func(*args, **kwargs)

    def compose(self, other_module, *args, **kwargs):
        """Combine this module with another."""
        # Get circuits from both
        c1 = self()
        c2 = other_module(*args, **kwargs) if callable(other_module) else other_module

        # Create combined circuit
        combined = c1.copy()
        # Add gates from c2 to combined
        combined.gates.extend(c2.gates)
        combined.n_qubits = max(c1.n_qubits, c2.n_qubits)
        combined.n_bits = max(c1.n_bits, c2.n_bits)

        return combined


def module(func):
    """Decorator to create a Module."""
    return Module(func)
```

```python
# modules/standard.py

from ..circuit import Circuit
from ..gates import H, CNOT
from .decorator import module

@module
def BellPair():
    """Create a Bell state (maximally entangled pair)."""
    c = Circuit(2)
    c.apply(H, 0)
    c.apply(CNOT, 0, 1)
    c.measure_all()
    return c

@module
def Superposition(n_qubits=1):
    """Create equal superposition on all qubits."""
    c = Circuit(n_qubits)
    for i in range(n_qubits):
        c.apply(H, i)
    c.measure_all()
    return c

@module
def GHZ(n_qubits=3):
    """Create a GHZ state (Greenberger-Horne-Zeilinger)."""
    c = Circuit(n_qubits)
    c.apply(H, 0)
    for i in range(n_qubits - 1):
        c.apply(CNOT, i, i + 1)
    c.measure_all()
    return c
```

### Verification
```python
# tests/test_modules.py

from openquanta.modules import BellPair, Superposition, GHZ

def test_bell_pair():
    bell = BellPair()
    result = bell.simulate(shots=1000)

    # Should only get 00 or 11
    assert "00" in result or "11" in result
    assert sum(result.values()) == 1000

def test_superposition():
    sup = Superposition(2)
    result = sup.simulate(shots=1000)

    # Should get all possible outcomes
    assert len(result) == 4  # 00, 01, 10, 11
    assert sum(result.values()) == 1000

def test_ghz():
    ghz = GHZ(3)
    result = ghz.simulate(shots=1000)

    # GHZ should give 000 or 111
    assert "000" in result or "111" in result
```

### Success Criteria
- Module decorator works
- Standard modules create correct circuits
- Modules simulate correctly
- All tests pass

---

## Phase 7: Examples & Documentation (Day 11)

### Goal
Create examples and documentation for users.

### Tasks
- [ ] Create getting started guide
- [ ] Create basic examples
- [ ] Create algorithm examples
- [ ] Add docstrings to all public functions
- [ ] All examples run without error

### Files to Create
```
examples/
├── basic/
│   ├── 01_hello_quantum.py
│   ├── 02_bell_state.py
│   └── 03_superposition.py
├── algorithms/
│   ├── grover_search.py
│   └── deutsch_jozsa.py
└── README.md

docs/
└── getting_started.md
```

### Example Code
```python
# examples/basic/01_hello_quantum.py
"""
Hello Quantum World!
The simplest quantum program.
"""

from openquanta import Circuit, gates

# Create a circuit with 1 qubit
c = Circuit(1)

# Apply Hadamard gate (creates superposition)
c.apply(gates.H, 0)

# Measure the qubit
c.measure(0, 0)

# Simulate
result = c.simulate(shots=1000)

print("Hello Quantum World!")
print(f"Results: {result}")
print("You should see roughly 50% 0s and 50% 1s")
```

### Success Criteria
- All examples run
- Documentation is clear
- New users can follow getting started

---

## Phase 8: IBM Backend (Day 12-13)

### Goal
Add IBM Quantum hardware backend.

### Tasks
- [ ] Create IBM backend class
- [ ] Handle IBM API credentials
- [ ] Implement job submission
- [ ] Handle job status and results
- [ ] Write tests (may need mock)
- [ ] Document setup process

### Files to Create
```
openquanta/
└── backends/
    └── ibm.py         # NEW
```

### Code Structure
```python
# backends/ibm.py

from qiskit_ibm_runtime import QiskitRuntimeService
from .base import Backend

class IBMBackend(Backend):
    """IBM Quantum hardware backend."""

    def __init__(self, token: str, backend_name: str = "ibm_sherbrooke"):
        self.service = QiskitRuntimeService(channel="ibm_quantum", token=token)
        self.backend_name = backend_name
        self.backend = self.service.backend(backend_name)

    def execute(self, circuit, shots: int = 1000):
        # Convert to Qiskit (reuse simulator backend's method)
        from .simulator import SimulatorBackend
        qc = SimulatorBackend()._to_qiskit(circuit)

        # Run on IBM
        from qiskit_ibm_runtime import SamplerV2
        sampler = SamplerV2(self.backend)
        job = sampler.run([qc], shots=shots)
        result = job.result()
        return dict(result[0].data.meas.get_counts())
```

### Success Criteria
- IBM backend connects
- Jobs submit successfully
- Results return correctly

---

## Phase 9: Polish & Release Prep (Day 14)

### Goal
Prepare for first release.

### Tasks
- [ ] Add comprehensive error handling
- [ ] Add input validation
- [ ] Complete README
- [ ] Add LICENSE file
- [ ] Add CHANGELOG
- [ ] Create GitHub repository
- [ ] Publish to PyPI (optional)

### Files to Finalize
```
├── README.md
├── LICENSE
├── CHANGELOG.md
├── pyproject.toml
└── .github/
    └── workflows/
        └── test.yml
```

### Success Criteria
- `pip install openquanta` works
- README explains project
- All tests pass on CI

---

## Build Order Summary

```
Phase 0: Setup                    → Foundation
    │
    ▼
Phase 1: Gates                    → Build blocks
    │
    ▼
Phase 2: Circuit                  → Store blocks
    │
    ▼
Phase 3: QIR Bridge               → Translate blocks
    │
    ▼
Phase 4: Simulator Backend        → Run blocks
    │
    ▼
Phase 5: Circuit Methods          → Easy API
    │
    ▼
Phase 6: Module System            → Reusable blocks
    │
    ▼
Phase 7: Examples & Docs          → User onboarding
    │
    ▼
Phase 8: IBM Backend              → Real hardware
    │
    ▼
Phase 9: Polish & Release         → Production ready
```

---

## Error Isolation Strategy

Each phase is **self-contained**:

1. **Phase 1 fails** → Gates don't create → Fix gate code only
2. **Phase 2 fails** → Circuit doesn't store → Fix circuit code only
3. **Phase 3 fails** → QIR not generated → Fix bridge code only
4. **Phase 4 fails** → Simulation errors → Fix backend code only
5. **Phase 5 fails** → Methods don't work → Fix integration only
6. **Phase 6 fails** → Modules don't compose → Fix module code only

We always know **where** to look.

---

## Testing Strategy

| Phase | Test Type | What We Test |
|-------|-----------|--------------|
| 1 | Unit | Gate creation |
| 2 | Unit | Circuit storage |
| 3 | Unit | QIR output |
| 4 | Integration | Simulation results |
| 5 | Integration | End-to-end workflow |
| 6 | Unit | Module composition |
| 7 | Manual | Examples run |
| 8 | Integration | Hardware execution |
| 9 | CI/CD | All tests pass |

---

## Dependencies Timeline

```
Phase 0: Install all dependencies
Phase 1: Uses gates only (no deps)
Phase 2: Uses Circuit + gates (no new deps)
Phase 3: Uses PyQIR (new dep)
Phase 4: Uses Qiskit Aer (new dep)
Phase 5: No new deps
Phase 6: No new deps
Phase 7: No new deps
Phase 8: Uses Qiskit IBM Runtime (new dep)
Phase 9: No new deps
```

---

## Ready to Start?

Once you approve this plan, we begin with **Phase 0: Setup**.

Each phase will be completed, tested, and verified before moving to the next.