<div align="center">

# Open-Quanta

**Modular Quantum Computing for Every Python Developer**

*Write Python. Run Quantum. Stay Modular.*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![QIR Compatible](https://img.shields.io/badge/QIR-Compatible-green.svg)](https://qir-alliance.org/)

</div>

---

## 🚀 What is open-Quanta? ( This gives developers room to grow from writing a simple "Hello Quantum" script to experimenting with high-level quantum mechanics)

open-Quanta is an **open-source Python library** that makes quantum computing accessible to every Python developer. Build quantum circuits using simple, readable Python code — no physics PhD required.

```python
from openquanta import Circuit, gates

# Create a Bell state (entangled qubits)
c = Circuit(2)
c.apply(gates.H, 0)          # Hadamard gate
c.apply(gates.CNOT, 0, 1)     # CNOT gate
c.measure_all()              # Measure both qubits

# Run on local simulator
result = c.simulate(shots=1000)
print(result)  # {'00': 500, '11': 500}
```

**The result?** Only `00` or `11` — never `01` or `10`. That's quantum entanglement in 5 lines of Python!

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔧 **30+ Gates** | H, X, Y, Z, CNOT, Toffoli, rotations, and more |
| 🧩 **Modular Design** | Build with reusable blocks, not from scratch |
| 🔄 **Portable** | Generate QIR code that runs on any quantum hardware |
| 🧪 **Easy Testing** | Free local simulation with Qiskit Aer |
| 🎯 **Pythonic API** | Clean, intuitive syntax that feels natural |
| ⚡ **Pre-built Modules** | BellPair, GHZ, Grover, QFT, and more |
| 🛠️ **Custom Gates** | Create your own gates with unitary matrices |

---

## 📦 Installation

```bash
pip install openquanta
```

### Requirements

- Python 3.10 or higher
- Qiskit (for simulation)
- PyQIR (for QIR generation)

```bash
pip install qiskit qiskit-aer pyqir numpy
```

---

## 🎯 Quick Start

### Hello Quantum World

Create superposition — the simplest quantum state:

```python
from openquanta import Circuit, gates

c = Circuit(1)               # 1 qubit
c.apply(gates.H, 0)          # Hadamard creates superposition
c.measure(0, 0)              # Measure qubit 0 to bit 0

result = c.simulate()
print(result)  # {'0': ~500, '1': ~500} — 50/50 probability
```

### Bell State (Entanglement)

Create entangled qubits:

```python
from openquanta import Circuit, gates

c = Circuit(2)
c.apply(gates.H, 0)          # Superposition
c.apply(gates.CNOT, 0, 1)     # Entanglement
c.measure_all()

result = c.simulate()
print(result)  # {'00': ~500, '11': ~500} — always same!
```

### Using Pre-built Modules

```python
from openquanta.modules import BellPair, GHZ, QuantumRNG

# Bell state
result = BellPair.simulate()
print(result)  # {'00': ~500, '11': ~500}

# GHZ state (3-qubit entanglement)
result = GHZ(3).simulate()
print(result)  # {'000': ~500, '111': ~500}

# Quantum random number generator
result = QuantumRNG(8).simulate()
print(list(result.keys()))  # Random 8-bit numbers
```

### Custom Gates

Create your own quantum gates:

```python
from openquanta import Circuit, gates
from openquanta.gates import CustomGate
import numpy as np

# Create custom gate with your matrix
my_gate = CustomGate(
    name="MyX",
    targets=[0],
    matrix=np.array([[0, 1], [1, 0]])  # Same as X gate
)

c = Circuit(1)
c.apply(my_gate)
c.measure(0, 0)
result = c.simulate()
print(result)  # {'1': 1000} — flipped from |0⟩ to |1⟩
```

---

## 📚 Available Gates

### Single-Qubit Gates

| Gate | Description | Usage |
|------|-------------|-------|
| `H` | Hadamard (superposition) | `gates.H(0)` |
| `X` | Pauli-X (bit flip) | `gates.X(0)` |
| `Y` | Pauli-Y | `gates.Y(0)` |
| `Z` | Pauli-Z (phase flip) | `gates.Z(0)` |
| `S` | S gate | `gates.S(0)` |
| `T` | T gate | `gates.T(0)` |

### Rotation Gates

| Gate | Description | Usage |
|------|-------------|-------|
| `RX` | Rotation around X | `gates.RX(0, angle)` |
| `RY` | Rotation around Y | `gates.RY(0, angle)` |
| `RZ` | Rotation around Z | `gates.RZ(0, angle)` |

### Two-Qubit Gates

| Gate | Description | Usage |
|------|-------------|-------|
| `CNOT` | Controlled-NOT | `gates.CNOT(0, 1)` |
| `CZ` | Controlled-Z | `gates.CZ(0, 1)` |
| `SWAP` | Swap qubits | `gates.SWAP(0, 1)` |

### Multi-Qubit Gates

| Gate | Description | Usage |
|------|-------------|-------|
| `CCX` | Toffoli gate | `gates.CCX(0, 1, 2)` |
| `MCX` | Multi-controlled X | `gates.MCX([0,1], 2)` |

---

## 📁 Project Structure

```
open-quanta/
├── openquanta/
│   ├── __init__.py          # Main exports
│   ├── gates.py              # Gate library (30+ gates)
│   ├── circuit.py            # Circuit class
│   ├── qir_bridge.py         # QIR generation
│   ├── backends/
│   │   ├── base.py           # Abstract backend
│   │   └── simulator.py      # Qiskit Aer simulator
│   └── modules/
│       ├── decorator.py      # @module decorator
│       └── standard.py       # Pre-built circuits
│
├── tests/                    # Test suite
├── examples/                # Example scripts
│   ├── basic/
│   └── algorithms/
│
├── PROJECT.md                # Detailed documentation
├── BUILD_PLAN.md             # Development roadmap
└── README.md                 # This file
```

---

## 🔧 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER CODE                               │
│                                                             │
│   Circuit(2).apply(gates.H, 0).apply(gates.CNOT, 0, 1)      │
│                                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────── ────────────────┐
│                   open-Quanta CORE                           │
│                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│   │   Circuit   │  │    Gates    │  │   Modules   │          │
│   │   Builder   │  │  Library    │  │   System    │          │
│   └─────────────┘  └─────────────┘  └─────────────┘          │
│          │                                     │             │
│          └────────────────┬────────────────────┘             │
│                           ▼                                  │
│                  ┌─────────────┐                             │
│                  │ QIR Bridge  │                             │
│                  └─────────────┘                             │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
┌─────────────────────┐       ┌─────────────────────┐
│   SIMULATOR         │       │      QIR CODE       │
│   (Qiskit Aer)      │       │   (Industry Std)    │
│                     │       │                     │
│   Returns results   │       │  Runs on hardware   │
│   {'00': 500}       │       │  IBM, Quantinuum    │
└─────────────────────┘       └─────────────────────┘
```

---

## 📖 How It Works

### 1. Gates are Data

```python
# Gates are simple Python objects
h_gate = gates.H(0)
# Gate(name="H", targets=[0], params=[])
```

### 2. Circuits Store Gates

```python
c = Circuit(2)
c.apply(gates.H, 0)      # Adds Gate("H", [0], [])
c.apply(gates.CNOT, 0, 1) # Adds Gate("CNOT", [0, 1], [])
# c.gates = [Gate("H", ...), Gate("CNOT", ...)]
```

### 3. Simulator Converts to Qiskit

```python
# Internally converts our Circuit to Qiskit QuantumCircuit
# Runs simulation using Qiskit Aer
# Returns results as Python dict
result = c.simulate()  # {'00': 500, '11': 500}
```

### 4. QIR Bridge Generates Standard Code

```python
qir_code = c.to_qir()
# Generates LLVM-based QIR that runs on any quantum hardware
```

---

## 🎓 Pre-built Modules

| Module | Description | Usage |
|--------|-------------|-------|
| `BellPair` | Maximally entangled 2-qubit state | `BellPair.simulate()` |
| `GHZ(n)` | GHZ state (n-qubit entanglement) | `GHZ(3).simulate()` |
| `Superposition(n)` | Equal superposition | `Superposition(2).simulate()` |
| `QFT(n)` | Quantum Fourier Transform | `QFT(3).simulate()` |
| `Grover(n, marked)` | Grover's search | `Grover(2, 1).simulate()` |
| `QuantumRNG(n)` | Quantum random numbers | `QuantumRNG(8).simulate()` |

---

## 🧪 Running Tests

```bash
cd open-quanta
pytest tests/
```

---

## 🛣️ Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| ✅ Core | Complete | Gates, Circuit, Simulator, QIR |
| ✅ Modules | Complete | Pre-built quantum circuits |
| ✅ QIR | Complete | Microsoft PyQIR integration |
| 🚧 Hardware | Planned | IBM Quantum backend |
| 🚧 PyPI | Planned | pip install openquanta |

---

## 🤝 Contributing

Contributions are welcome! See [BUILD_PLAN.md](BUILD_PLAN.md) for development roadmap.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

## 📄 License

MIT License - Open source and free to use.

---

## 🙏 Acknowledgments

- **PyQIR** - Microsoft's QIR generation library
- **Qiskit** - IBM's quantum computing framework
- **QIR Alliance** - Industry standard for quantum IR

---

## 📧 Contact

- GitHub: [https://github.com/mkrishna793/open-Quanta](https://github.com/mkrishna793/open-Quanta)
- Issues: [Report a bug](https://github.com/mkrishna793/open-Quanta/issues)

---

<div align="center">

</div>
