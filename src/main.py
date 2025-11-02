import os
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime import QiskitRuntimeService

token = os.getenv("IBM_QUANTUM_API_TOKEN")
instance = os.getenv("IBM_QUANTUM_CRN")

# QiskitRuntimeService.save_account(
#     token=token,
#     instance=instance
# )

service = QiskitRuntimeService()

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

sampler = StatevectorSampler()
result = sampler.run([qc], shots=1024).result()
print(result[0].data.meas.get_counts())

counts = result[0].data.meas.get_counts()
plot_histogram(counts)

# ======================================= #
# Create and run a simple quantum program #
# ======================================= #

# Circuit for Bell state, a state wherein two qubits are fully entangled with each other

# from qiskit.quantum_info import SparsePauliOp
# from qiskit.transpiler import generate_preset_pass_manager
# from qiskit_ibm_runtime import EstimatorV2 as Estimator

# qc = QuantumCircuit(2) # create new cirbuit with two qubits
# qc. h(0)               # add hadamard gate to qubit 0
# qc.cx(0, 1)            # perform controlled-X gate on qubit 1, controlled by qubit 0

# circuit = qc.draw("mpl")
# circuit.savefig("circuit_visualization.png")
