# Contributing to open-Quanta

Thank you for your interest in contributing! This document provides guidelines for contributions.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/open-Quanta.git
   cd open-Quanta
   ```
3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Setup

```bash
# Install in development mode
pip install -e .

# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/
```

## Project Structure

```
openquanta/
├── gates.py         # Add new gates here
├── circuit.py       # Circuit modifications
├── qir_bridge.py    # QIR generation
├── backends/        # Add new backends here
└── modules/         # Add new modules here
```

## Adding a New Gate

1. Add gate function in `gates.py`:
   ```python
   def MyGate(qubit: int) -> Gate:
       """Description of what the gate does."""
       return Gate("MyGate", targets=[qubit])
   ```

2. Add QIR translation in `qir_bridge.py`:
   ```python
   elif name == "MyGate":
       qis.my_gate(builder, qubits[targets[0]])
   ```

3. Add Qiskit translation in `backends/simulator.py`:
   ```python
   elif name == "MyGate":
       qc.my_gate(targets[0])
   ```

4. Add test in `tests/test_gates.py`

## Adding a New Module

1. Create module in `modules/standard.py`:
   ```python
   @module
   def MyModule(n_qubits: int):
       """Description of the module."""
       c = Circuit(n_qubits)
       # Build circuit
       c.measure_all()
       return c
   ```

2. Export in `modules/__init__.py`

3. Add test in `tests/test_modules.py`

## Code Style

- Use clear, descriptive names
- Add docstrings to all public functions
- Keep functions focused and small
- Write tests for new functionality

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_gates.py

# Run with coverage
pytest tests/ --cov=openquanta
```

## Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add my feature"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/my-feature
   ```

4. Open a Pull Request on GitHub

## Questions?

Open an issue on GitHub for questions or discussions.

Thank you for contributing!