"""
Hello Quantum World!
The simplest quantum program.

This example demonstrates:
- Creating a quantum circuit
- Applying a Hadamard gate (creates superposition)
- Measuring the qubit
- Simulating the circuit
"""

from openquanta import Circuit, gates

# Create a circuit with 1 qubit
c = Circuit(1, name="Hello Quantum")

# Apply Hadamard gate
# This creates a superposition: |0⟩ → (|0⟩ + |1⟩)/√2
c.apply(gates.H, 0)

# Measure the qubit
c.measure(0, 0)

# Simulate the circuit
result = c.simulate(shots=1000)

print("=" * 40)
print("Hello Quantum World!")
print("=" * 40)
print(f"Results: {result}")
print()
print("The Hadamard gate creates a superposition.")
print("You should see roughly 50% '0' and 50% '1'.")
print()
print(f"Got '0': {result.get('0', 0)} times")
print(f"Got '1': {result.get('1', 0)} times")