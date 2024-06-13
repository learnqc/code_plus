#!/usr/bin/env python -m panel serve

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from hume.simulator.circuit import QuantumCircuit, QuantumRegister
from hume.qiskit.util import print_circuit, show_reports
from math import pi
from components.common import Display, arg_gates, get_circuit, state_table_to_string
import panel as pn

# template = pn.template.BootstrapTemplate(title='Building Quantum Software')

# template.header.append('### Frequency Encoding')

def encode_frequency(n, v):
    q = QuantumRegister(n)
    qc = QuantumCircuit(q)

    for j in range(n):
        qc.h(q[j])

    for j in range(n):
        qc.p(2 * pi / 2 ** (n - j) * v, q[j]) # <1>

    qc.report('geometric_sequence')

    qc.append_iqft(q)

    qc.report('iqft')

    return qc

def run(n, v):
    global out
    qc = encode_frequency(n, v)

    #frequency
    f = (f'Frequency:\n{v}' + (f' mapped to {round(v%2**n, 2)}' if v >= 2**n or v < 0 else ''))

    #circuit
    c = f'Circuit:\n{get_circuit(qc)}'

    #state
    state = qc.reports['iqft'][2]
    s = f'State:\n{state_table_to_string(state)}'



    #combining string
    out = f"{f}\n\n{c}\n\n{s}"


    return pn.pane.Str(out)

run(3, 4.3)

qubits = pn.widgets.IntInput(name="Qubits", value=3, start=1, end=5)
frequency = pn.widgets.FloatInput(name="Frequency", value=4.3, start=0)

display = pn.bind(
    run, n=qubits, v=frequency
)

widgets = pn.Column(qubits, frequency, sizing_mode='fixed', width=300)

pn.Column(widgets, display)

pn.template.MaterialTemplate(
    title="Frequency Encoding",
    sidebar=[qubits, frequency],
    main=[display],
).servable();