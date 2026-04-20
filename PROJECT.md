# open-Quanta Project Documentation

## What Is open-Quanta?

open-Quanta is an open-source Python library that makes quantum computing accessible to every Python developer. It provides modular building blocks for creating quantum circuits, testing them on simulators, and running them on any quantum hardware — all with clean, Pythonic syntax.

---

## Core Philosophy

**Write Python. Run Quantum. Stay Modular.**

- No physics PhD required
- No vendor lock-in
- No rewriting code for different hardware
- Build once, compose, share, reuse

---

## The Problem Today

| Issue | Reality |
|-------|---------|
| Too hard | Only ~10,000 people worldwide can use quantum productively |
| Vendor lock-in | IBM users can't run on Google/Quantinuum without rewriting |
| Hard to test | Need hardware access to test anything |
| Hard to share | Algorithms live in papers, not reusable code |
| Fragmented | Each vendor has their own SDK, ecosystem, and learning curve |

---

## The Solution

open-Quanta solves these problems with three key innovations:

### 1. Modular Architecture
Users build with blocks, not from scratch:
```
Gate → Circuit → Module → Algorithm
```
Each level is reusable and composable.

### 2. QIR Standard
Uses Quantum Intermediate Representation (QIR) — an industry standard backed by IBM, Microsoft, Quantinuum, and others. This means code runs on ALL hardware, not just one vendor.

### 3. Pythonic API
Clean, intuitive syntax that any Python developer can learn in minutes, not months.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER LAYER                               │
│                                                              │
│   Beginner:  modules.BellPair().run()                       │
│   Developer: Circuit(2).apply(gates.H, 0).apply(...)        │
│   Creator:   @module def MyAlgo(...): ...                   │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                   open-Quanta CORE                           │
│                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │   Circuit   │  │    Gates    │  │   Modules   │        │
│   │   Builder   │  │  Library    │  │   System    │        │
│   └─────────────┘  └─────────────┘  └─────────────┘        │
│          │                │                │                │
│          └────────────────┼────────────────┘                │
│                           ▼                                 │
│                  ┌─────────────┐                            │
│                  │ QIR Bridge  │                            │
│                  │ (Compiler)  │                            │
│                  └─────────────┘                            │
│                           │                                 │
├───────────────────────────┼─────────────────────────────────┤
│                     QIR OUTPUT                              │
│           (Hardware-Agnostic Intermediate Code)             │
│                           │                                 │
├───────────────────────────┼─────────────────────────────────┤
│                    BACKENDS                                 │
│                           │                                 │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│   │Simulator │ │   IBM    │ │Quantinuum│ │   IonQ   │     │
│   │  (Aer)   │ │ Quantum  │ │ Hardware │ │ Hardware │     │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Circuit Class
The core object that stores a quantum circuit.

**Responsibilities:**
- Track number of qubits
- Store sequence of gates
- Track classical measurement bits
- Provide fluent API for building

**Example:**
```python
c = Circuit(2)
c.apply(gates.H, 0)        # Hadamard on qubit 0
c.apply(gates.CNOT, 0, 1)  # CNOT gate
c.measure_all()            # Measure all qubits
```

---

### 2. Gates Library
Collection of quantum gates as Python objects.

**Basic Gates:**
| Gate | Symbol | Description |
|------|--------|-------------|
| Hadamard | H | Creates superposition |
| Pauli-X | X | Bit flip |
| Pauli-Y | Y | Bit and phase flip |
| Pauli-Z | Z | Phase flip |
| CNOT | CX | Controlled NOT (entanglement) |
| CZ | CZ | Controlled Z |
| Rotation-X | RX | Rotate around X axis |
| Rotation-Y | RY | Rotate around Y axis |
| Rotation-Z | RZ | Rotate around Z axis |
| Measure | M | Measure to classical bit |

---

### 3. Module System
Reusable, shareable quantum algorithms.

**What is a Module?**
- A quantum circuit wrapped in a Python function
- Decorated with `@module`
- Can take parameters
- Can be composed with other modules

**Example:**
```python
@module
def BellPair():
    c = Circuit(2)
    c.apply(gates.H, 0)
    c.apply(gates.CNOT, 0, 1)
    return c

# Usage
bell = BellPair()
result = bell.simulate()
```

---

### 4. QIR Bridge
Translates Circuit objects to QIR code using PyQIR.

**What it does:**
1. Takes Circuit object
2. Iterates through gates
3. Calls PyQIR functions for each gate
4. Returns QIR string

**Input:** Circuit object
**Output:** QIR code (LLVM-based text)

---

### 5. Backends
Execute QIR on different targets.

**Backend Interface:**
```python
class Backend:
    def execute(qir_code, shots=1000) -> dict:
        # Returns {'00': count, '01': count, ...}
```

**Available Backends:**
| Backend | Type | Description |
|---------|------|-------------|
| Simulator | Local | Qiskit Aer, runs on CPU |
| IBM Quantum | Cloud | Real IBM hardware |
| Quantinuum | Cloud | Real Quantinuum hardware |

---

## Data Flow

```
User writes Python code
        │
        ▼
Circuit object created (stores gates)
        │
        ▼
QIR Bridge converts Circuit → QIR
        │
        ▼
Backend receives QIR
        │
        ├── Simulator: QIR → Qiskit → Execute locally
        │
        └── Hardware: QIR → Vendor API → Execute on quantum computer
        │
        ▼
Results returned as Python dict
        │
        ▼
User gets: {'00': 500, '11': 500}
```

---

## Dependencies

open-Quanta uses existing, battle-tested libraries:

| Dependency | Purpose | License |
|------------|---------|---------|
| PyQIR | QIR code generation | MIT (Microsoft) |
| Qiskit | Quantum circuit framework | Apache 2.0 |
| Qiskit Aer | Local simulator | Apache 2.0 |
| Qiskit IBM Runtime | IBM hardware access | Apache 2.0 |
| Python 3.10+ | Runtime | - |

**All dependencies are open source and free.**

---

## Project Structure

```
open-quanta/
├── openquanta/
│   ├── __init__.py           # Package entry point
│   ├── circuit.py            # Circuit class
│   ├── gates.py              # Gate definitions
│   ├── qir_bridge.py         # Circuit → QIR translation
│   ├── backends/
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract Backend class
│   │   ├── simulator.py      # Qiskit Aer backend
│   │   └── ibm.py            # IBM Quantum backend
│   └── modules/
│       ├── __init__.py
│       ├── decorator.py      # @module decorator
│       └── standard.py       # Pre-built modules
├── tests/
│   ├── test_circuit.py
│   ├── test_gates.py
│   ├── test_qir_bridge.py
│   └── test_backends.py
├── examples/
│   ├── basic/
│   │   ├── bell_state.py
│   │   └── superposition.py
│   └── algorithms/
│       └── grover.py
├── docs/
│   └── getting_started.md
├── pyproject.toml
├── README.md
└── PROJECT.md              # This file
```

---

## User Levels

### Level 1: Absolute Beginner
```python
from openquanta import modules

bell = modules.BellPair()
result = bell.simulate()
print(result)
```

### Level 2: Learning Developer
```python
from openquanta import Circuit, gates

c = Circuit(2)
c.apply(gates.H, 0)
c.apply(gates.CNOT, 0, 1)
c.measure_all()
c.draw()  # See the circuit
result = c.simulate()
```

### Level 3: Algorithm Creator
```python
from openquanta import Circuit, gates, module

@module
def GroverSearch(n_qubits, oracle):
    c = Circuit(n_qubits)
    # Build Grover's algorithm
    ...
    return c

# Share with community
```

### Level 4: Hardware Engineer
```python
from openquanta import Circuit, gates

c = Circuit(4)
# ... build circuit

# Choose where to run
result_ibm = c.run(backend="ibm_sherbrooke")
result_quantinuum = c.run(backend="quantinuum_h2")
result_sim = c.simulate()

# Get raw QIR
qir_code = c.to_qir()
```

---

## Key Design Principles

1. **Simplicity First** — The API should feel natural to Python developers
2. **Modular** — Every piece is reusable and composable
3. **Honest** — Never silently fail or hide errors
4. **Portable** — Write once, run anywhere via QIR
5. **Educational** — Users learn quantum as they use it
6. **Community-Driven** — Easy to contribute modules and backends

---

## What open-Quanta Is NOT

- Not a physics simulator (uses existing simulators)
- Not a new quantum language (Python is enough)
- Not vendor-specific (QIR keeps it portable)
- Not a magic translator (user controls the circuit)
- Not for production quantum workloads (yet — hardware is still evolving)

---

## Success Metrics

| Metric | Goal |
|--------|------|
| GitHub stars | 1,000+ in first year |
| Contributors | 50+ community modules |
| pip installs | 10,000+ monthly |
| Tutorial completions | 5,000+ users finish getting started |
| Hardware compatibility | 3+ vendors supported |

---

## Long-Term Vision

**Year 1:** Become the easiest way to learn and prototype quantum circuits
**Year 2:** Standard library of 100+ community modules
**Year 3:** Default choice for quantum education and prototyping
**Year 5:** Standard layer between Python developers and all quantum hardware

---

## Contact & Community

- GitHub: github.com/open-quanta (to be created)
- License: MIT (open source, permissive)
- Python Version: 3.10+

---

*This document is designed for both human developers and AI assistants to understand the project completely.*