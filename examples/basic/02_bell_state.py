"""
Bell State (Entanglement)
Create a maximally entangled 2-qubit state.

The Bell state is: (|00⟩ + |11⟩) / √2

When measured, both qubits always give the same result.
This demonstrates quantum entanglement.
"""

from openquanta import Circuit, gates
from openquanta.modules import BellPair

print("=" * 50)
print("Bell State - Quantum Entanglement")
print("=" * 50)

# Method 1: Build circuit manually
print("\nMethod 1: Building the circuit manually")
print("-" * 40)

c = Circuit(2, name="Bell State")

# Step 1: Put qubit 0 in superposition
c.apply(gates.H, 0)
print("Applied H to qubit 0 (creates superposition)")

# Step 2: Entangle qubits with CNOT
c.apply(gates.CNOT, 0, 1)
print("Applied CNOT(0, 1) (creates entanglement)")

# Step 3: Measure
c.measure_all()
print("Measured both qubits")

# Simulate
result = c.simulate(shots=1000)
print(f"\nResults: {result}")
print("Notice: We only get '00' or '11' - never '01' or '10'!")
print("This is entanglement - both qubits are correlated.")

# Method 2: Use pre-built module
print("\n" + "=" * 50)
print("Method 2: Using the BellPair module")
print("-" * 40)

bell = BellPair()
result2 = bell.simulate(shots=1000)
print(f"Results: {result2}")

# Show circuit
print("\nCircuit structure:")
print(c.draw())