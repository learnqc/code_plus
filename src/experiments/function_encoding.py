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


def get_circuit_str(k, v, p, i, n):
    coeffs = terms_from_poly(p, k, i == 'Polynomial')
    qc = build_polynomial_circuit(k, v, coeffs)
    c = f'Circuit:\n{get_circuit(qc)}'
    return pn.pane.Str(c)

def get_grid(k, v, p, i, n):
    coeffs = terms_from_poly(p, k, i == 'Polynomial')
    qc = build_polynomial_circuit(k, v, coeffs)
    state = qc.reports['qpe'][2]
    grid = grid_state_html(state, k, n == 'Yes', True)
    return pn.pane.HTML(grid)

get_circuit_str(2, 2, 'x**2', 'Polynomial', 'No')
get_grid(2, 2, 'x**2', 'Polynomial', 'No')

n_key = pn.widgets.IntInput(name="# of Qubits", value=2)
n_value = pn.widgets.IntInput(name="# of Bits", value=2)
poly = pn.widgets.TextInput(name="Polynomial", value='x**2')
input_select = pn.widgets.Select(name="Type of expression", options=['Polynomial', 'Binary Terms'], value='Polynomial')
negative = pn.widgets.Select(name="Negative values for grid state?", options=['Yes', 'No'], value='No')

circuit = pn.bind(
    get_circuit_str, k=n_key, v=n_value, p=poly, i=input_select, n=negative
)

grid = pn.bind(
    get_grid, k=n_key, v=n_value, p=poly, i=input_select, n=negative
)

widgets = pn.Column(n_key, n_value, poly, input_select, negative, sizing_mode='fixed', width=100)

display = pn.GridBox(
    circuit,
    grid,
    ncols=1,
    sizing_mode='fixed',
    width = 800
)

pn.Column(widgets, display)

pn.template.MaterialTemplate(
    title="Function Encoding",
    sidebar=[n_key, n_value, poly, input_select, negative],
    main=[display],
).servable()