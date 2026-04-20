"""
Grover's Search Algorithm

This example demonstrates Grover's algorithm for searching
an unsorted database. Classical: O(N), Quantum: O(√N)
"""

from openquanta.modules import Grover

print("=" * 50)
print("Grover's Search Algorithm")
print("=" * 50)

# Search for a specific item
n_qubits = 2  # 4 items total
marked_state = 2  # Looking for item 2 (binary: 10)

print(f"\nSearching in 2^{n_qubits} = {2**n_qubits} items")
print(f"Looking for item {marked_state} (binary: {format(marked_state, '02b')})")

# Create Grover circuit
grover = Grover(n_qubits, marked_state, iterations=1)
result = grover.simulate(shots=1000)

print(f"\nResults: {result}")

# Find the most likely outcome
most_likely = max(result, key=result.get)
print(f"\nMost likely outcome: {most_likely}")
print(f"Expected: {format(marked_state, '02b')}")

if most_likely == format(marked_state, '02b'):
    print("\n✓ Grover's algorithm found the marked item!")
else:
    print("\nNote: May need more iterations or larger sample")

print("\nGrover's advantage:")
print(f"  Classical: {2**n_qubits} queries needed")
print(f"  Quantum: ~{int((2**n_qubits)**0.5)} queries needed")