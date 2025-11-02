from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np
from collections import Counter

class QuantumMusicGenerator:
    """Generate musical note arrays from quantum circuits"""
    
    def __init__(self, shots=1024):
        self.simulator = AerSimulator()
        self.shots = shots
    
    def run_circuit(self, circuit):
        """Execute a quantum circuit and return measurement results"""
        compiled_circuit = transpile(circuit, self.simulator)
        job = self.simulator.run(compiled_circuit, shots=self.shots)
        result = job.result()
        counts = result.get_counts(circuit)
        return counts
    
    def counts_to_numbers(self, counts, num_notes=20):
        """Convert measurement counts to an array of numbers"""
        numbers = []
        
        # Create weighted list based on measurement probabilities
        for bitstring, count in counts.items():
            value = int(bitstring, 2)  # Convert binary to decimal
            numbers.extend([value] * count)
        
        # Shuffle and take num_notes samples
        np.random.shuffle(numbers)
        return numbers[:num_notes]
    
    def counts_to_sequence(self, counts, num_notes=20):
        """Convert to sequential ordered notes"""
        # Sort by bitstring value
        sorted_items = sorted(counts.items(), key=lambda x: int(x[0], 2))
        
        numbers = []
        for bitstring, count in sorted_items:
            value = int(bitstring, 2)
            # Add proportional to count
            repeat = max(1, int(count / self.shots * num_notes))
            numbers.extend([value] * repeat)
        
        return numbers[:num_notes]
    
    def superposition_random(self, num_qubits=4, num_notes=20):
        """Pure quantum randomness from superposition"""
        qc = QuantumCircuit(num_qubits, num_qubits)

        for i in range(num_qubits):
            qc.h(i)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_numbers(counts, num_notes)
    
    def quantum_interference_pattern(self, num_qubits=4, num_notes=20):
        """Use quantum interference to create patterns"""
        qc = QuantumCircuit(num_qubits, num_qubits)

        for i in range(num_qubits):
            qc.h(i)

        for i in range(num_qubits):
            qc.p(np.pi / (2 ** i), i)

        for i in range(num_qubits):
            qc.h(i)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_sequence(counts, num_notes)
    
    def entangled_melody(self, num_qubits=4, num_notes=20):
        """Create correlated notes using entanglement"""
        qc = QuantumCircuit(num_qubits, num_qubits)

        qc.h(0)
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)

        for i in range(num_qubits):
            qc.ry(np.pi / 4 * i, i)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_numbers(counts, num_notes)
    
    def quantum_walk_melody(self, steps=5, num_notes=20):
        """Quantum walk creates a melodic progression"""
        num_qubits = 4
        qc = QuantumCircuit(num_qubits, num_qubits)

        qc.h(0)

        for step in range(steps):
            qc.h(0)
            for i in range(num_qubits - 1):
                qc.cx(0, i + 1)
            qc.p(np.pi / (step + 1), 0)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_sequence(counts, num_notes)
    
    def grover_pattern(self, num_qubits=4, iterations=2, num_notes=20):
        """Use Grover's algorithm to amplify certain notes"""
        qc = QuantumCircuit(num_qubits, num_qubits)

        for i in range(num_qubits):
            qc.h(i)

        for _ in range(iterations):
            # Oracle (mark state |1010⟩)
            qc.z(1)
            qc.z(3)

            # Diffusion operator
            for i in range(num_qubits):
                qc.h(i)
            for i in range(num_qubits):
                qc.x(i)

            qc.h(num_qubits - 1)
            qc.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            qc.h(num_qubits - 1)

            for i in range(num_qubits):
                qc.x(i)
            for i in range(num_qubits):
                qc.h(i)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_numbers(counts, num_notes)
    
    def qft_harmony(self, num_qubits=4, num_notes=20):
        """Quantum Fourier Transform for harmonic patterns"""
        qc = QuantumCircuit(num_qubits, num_qubits)

        for i in range(num_qubits):
            if i % 2 == 0:
                qc.x(i)

        for j in range(num_qubits):
            qc.h(j)
            for k in range(j + 1, num_qubits):
                qc.cp(np.pi / (2 ** (k - j)), k, j)

        for i in range(num_qubits // 2):
            qc.swap(i, num_qubits - i - 1)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_sequence(counts, num_notes)
    
    def parametric_melody(self, theta_values=None, num_notes=20):
        """Create melody from parametric rotations"""
        if theta_values is None:
            theta_values = [np.pi/4, np.pi/3, np.pi/2, np.pi]

        num_qubits = 4
        qc = QuantumCircuit(num_qubits, num_qubits)

        for i, theta in enumerate(theta_values[:num_qubits]):
            qc.ry(theta, i)

        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)

        for i in range(num_qubits):
            qc.rz(theta_values[i % len(theta_values)], i)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_numbers(counts, num_notes)
    
    def bell_state_chords(self, num_notes=20):
        """Create harmonious chords using Bell states"""
        qc = QuantumCircuit(4, 4)

        qc.h(0)
        qc.cx(0, 1)

        qc.h(2)
        qc.cx(2, 3)

        qc.cx(1, 2)
        qc.h(1)

        qc.measure(range(4), range(4))

        counts = self.run_circuit(qc)
        return self.counts_to_numbers(counts, num_notes)
    
    def phase_music(self, num_qubits=4, num_notes=20):
        """Create patterns using phase rotations"""
        qc = QuantumCircuit(num_qubits, num_qubits)

        for i in range(num_qubits):
            qc.h(i)

        for i in range(num_qubits):
            for j in range(i + 1):
                qc.p(np.pi / (2 ** j), i)

        for i in range(num_qubits):
            qc.h(i)

        qc.measure(range(num_qubits), range(num_qubits))

        counts = self.run_circuit(qc)
        return self.counts_to_sequence(counts, num_notes)
    
    def custom_circuit(self, circuit, num_notes=20, ordered=False):
        """Use your own custom circuit"""
        counts = self.run_circuit(circuit)
        
        if ordered:
            return self.counts_to_sequence(counts, num_notes)
        else:
            return self.counts_to_numbers(counts, num_notes)





if __name__ == "__main__":
    qm = QuantumMusicGenerator()

    # Generate quantum random notes
    numbers = qm.superposition_random(num_qubits=5, num_notes=30)
    print("Quantum random notes:", numbers)

    print("\nTrying different quantum patterns:\n")

    print("1. Quantum Interference:")
    numbers = qm.quantum_interference_pattern(num_qubits=4, num_notes=20)
    print(f"   {numbers}\n")

    print("2. Entangled Melody:")
    numbers = qm.entangled_melody(num_qubits=4, num_notes=20)
    print(f"   {numbers}\n")

    print("3. Quantum Walk:")
    numbers = qm.quantum_walk_melody(steps=5, num_notes=20)
    print(f"   {numbers}\n")

    print("4. Custom Circuit:")
    qc = QuantumCircuit(4, 4)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.ry(np.pi/4, 0)
    qc.ry(np.pi/3, 1)
    qc.measure(range(4), range(4))

    numbers = qm.custom_circuit(qc, num_notes=25, ordered=True)
    print(f"   {numbers}\n")

    print("5. Quantum Composition (multiple parts):")
    intro = qm.bell_state_chords(num_notes=10)
    verse = qm.quantum_walk_melody(steps=4, num_notes=15)
    chorus = qm.qft_harmony(num_qubits=4, num_notes=12)
    outro = qm.phase_music(num_qubits=4, num_notes=8)

    full_composition = intro + verse + chorus + outro
    print(f"   Full composition ({len(full_composition)} notes)")
    print(f"   {full_composition}\n")