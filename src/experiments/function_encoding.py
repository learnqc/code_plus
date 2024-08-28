#!/usr/bin/env python -m panel serve


import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from components.common import *
from components.function_encoding_component import *
from enum import Enum


from hume.simulator.circuit import QuantumCircuit, QuantumRegister
from hume.qiskit.util import hume_to_qiskit
from hume.utils.common import complex_to_rgb
from math import log2, floor, log10, atan2, pi
import panel as pn

widgets = pn.Column()

display = pn.Column()

pn.template.MaterialTemplate(
    title="Function Encoding",
    sidebar=[widgets],
    main=[display],
).servable()

n_key = pn.widgets.IntInput(name="# Input Qubits", value=2)
n_value = pn.widgets.IntInput(name="# Output Qubits", value=4)
input_select = pn.widgets.Select(name="Type of input", options=['Integer variable', 'Binary variable'], value='Integer variable')
poly = pn.widgets.TextInput(name="Function", value = 'x**2')
go = pn.widgets.Button(name='Apply', button_type='primary')
negative = pn.widgets.Select(name="Negative values for output?", options=['Yes', 'No'],value='No')

widgets.extend([n_key, n_value, poly, input_select, negative, go])

@pn.depends(input_select, watch=True)
def change_expression(v):
    if input_select.value == 'Binary variable':
        poly.value = 'x0'

    else:
        poly.value = 'x**2'

@pn.depends(go, watch=True)
def function_encoding(v):
    while(len(display) > 0):
        display.pop(0)

    coeffs = terms_from_poly(poly.value, n_key.value, input_select.value == 'Integer variable')
    # coeffs = terms_from_poly(poly.value, n_key.value, False)
    qc = build_polynomial_circuit(n_key.value, n_value.value, coeffs)

    c = f'Circuit:\n{get_circuit(qc)}'

    state = qc.reports['qpe'][2]
    # grid_state = grid_state_html(state, n_key.value, negative.value == 'Yes', True)
    grid_state = grid_state_html(state, n_key.value, negative.value == 'Yes', True)
    s = f'State:\n{grid_state}'
    # s = f'State:\n{state_table_to_string(state)}'

    grid = pn.pane.HTML(f'{s}')
    out = pn.pane.Str(f'{c}\n\n')
    display.append(grid)
    display.append(out)

    return out