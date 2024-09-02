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


widgets = pn.Column()
display = pn.Column()

pn.template.MaterialTemplate(
    title="Frequency Encoding",
    sidebar=[widgets],
    main=[display],
).servable()

qubits = pn.widgets.IntInput(name="Qubits", value=3, start=1, end=5)
frequency = pn.widgets.FloatInput(name="Frequency", value=4.3, start=0)
go = pn.widgets.Button(name='Apply', button_type='primary')

widgets.extend([qubits, frequency, go])

@pn.depends(go, watch=True)
def run(v):
    while(len(display) > 0):
        display.pop(0)

    qc = encode_frequency(qubits.value, frequency.value)
    c = f'Circuit:\n{get_circuit(qc)}'

    state = qc.reports['iqft'][2]
    s = f'State:{state_table_to_string(state)}'


    n = qubits.value
    v = frequency.value
    f = (f'Frequency:\n{v}' + (f' mapped to {round(v % 2 ** n, 2)}' if v >= 2 ** n or v < 0 else ''))

    out = pn.pane.Str(f'{s}\n\n{f}\n\n{c}')
    display.append(out)
    return out