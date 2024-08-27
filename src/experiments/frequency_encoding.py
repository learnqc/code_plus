#!/usr/bin/env python -m panel serve


import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from components.common import *
from components.frequency_encoding_component import *
from enum import Enum


from hume.simulator.circuit import QuantumCircuit, QuantumRegister
from hume.qiskit.util import hume_to_qiskit
from hume.utils.common import complex_to_rgb
from math import log2, floor, log10, atan2, pi
import panel as pn

def get_frequency(n, v):
    f = (f'Frequency:\n{v}' + (f' mapped to {round(v%2**n, 2)}' if v >= 2**n or v < 0 else ''))
    return pn.pane.Str(f)

def get_circuit_str(n, v):
    qc = encode_frequency(n, v)
    c = f'Circuit:\n{get_circuit(qc)}'
    return pn.pane.Str(c)

def get_state_str(n, v):
    qc = encode_frequency(n, v)
    state = qc.reports['iqft'][2]
    s = f'State:\n{state_table_to_string(state)}'
    return pn.pane.Str(s)

get_frequency(3, 4.3)
get_circuit_str(3, 4.3)
get_state_str(3, 4.3)

qubits = pn.widgets.IntInput(name="Qubits", value=3, start=1, end=5)
frequency = pn.widgets.FloatInput(name="Frequency", value=4.3, start=0)

circuit = pn.bind(
    get_circuit_str, n=qubits, v=frequency
)

state = pn.bind(
    get_state_str, n=qubits, v=frequency
)

mapped = pn.bind(
    get_frequency, n=qubits, v=frequency
)

widgets = pn.Column(qubits)
widgets.append(frequency)

display = pn.GridBox(
    mapped,
    state,
    circuit,
    ncols=1,
    sizing_mode='fixed',
    width = 800
)

pn.Column(widgets, display)

pn.template.MaterialTemplate(
    title="Frequency Encoding",
    sidebar=[widgets],
    main=[display],
).servable()