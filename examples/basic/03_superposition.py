"""
Superposition on Multiple Qubits

This example shows how to create equal superposition
across multiple qubits using Hadamard gates.
"""

from openquanta import Circuit, gates
from openquanta.modules import Superposition

print("=" * 50)
print("Superposition - Multiple Qubits")
print("=" * 50)

# Method 1: Manual circuit
print("\nMethod 1: Manual construction")
print("-" * 40)

n_qubits = 3
c = Circuit(n_qubits, name="Superposition")

# Apply H to each qubit
for i in range(n_qubits):
    c.apply(gates.H, i)

c.measure_all()

result = c.simulate(shots=1000)
print(f"Results with {n_qubits} qubits: {result}")
print(f"Number of possible states: 2^{n_qubits} = {2**n_qubits}")
print("Each state should appear roughly equally.")

# Method 2: Use module
print("\n" + "=" * 50)
print("Method 2: Using Superposition module")
print("-" * 40)

sup = Superposition(3)
result2 = sup.simulate(shots=1000)
print(f"Results: {result2}")

# Show that distribution is roughly uniform
print("\nDistribution analysis:")
total_shots = sum(result2.values())
for state, count in sorted(result2.items()):
    percentage = count / total_shots * 100
    bar = "#" * int(percentage / 2)
    print(f"  |{state}⟩: {count:4d} ({percentage:5.1f}%) {bar}")