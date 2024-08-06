from hume.simulator.circuit import QuantumCircuit, QuantumRegister
from math import log2, floor, log10, atan2, pi

def encode_frequency(n, v):
    q = QuantumRegister(n)
    qc = QuantumCircuit(q)

    for j in range(n):
        qc.h(q[j])
        qc.p(pi * 2 ** -j * v, q[j])

    qc.report('signal')

    qc.append_iqft(q, reversed=True, swap=False) #Apply the IQFT to qubit in reverse order and skip the qubit swapping in the IQFT

    qc.report('iqft')

    return qc