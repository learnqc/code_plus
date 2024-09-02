#!/usr/bin/env python -m panel serve


import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from components.single_qubit_component import SingleQubit
from components.common import *

import panel as pn

# # Explicitly set template and add some text to the header area
template = pn.template.BootstrapTemplate(title='Building Quantum Software')

template.header.append('### Single Qubit Circuit')

gate = pn.widgets.Select(name='Gate', options=[None] + [gate.upper() for gate in gates])
arg = pn.widgets.NumberInput(name='Angle (in degrees)', disabled=True)
go = pn.widgets.Button(name='Apply', button_type='primary')

template.sidebar.extend([gate, arg, go])

component = SingleQubit()


def select_gate(v):
    arg.disabled = gate.value is None or not (gate.value.lower() in arg_gates)


def apply(v):
    global out
    if go.value is True and gate.value is not None:
        # add_gate(qc, [], 0, gate.value.lower(), arg.value/180*pi if gate.value.lower() in arg_gates else None)
        component.apply_gate(gate.value.lower(), arg.value)
        gate.value = None
        arg.value = None
        arg.disabled = True
        go.value = False

        s = component.get_state()

        # s = state_table_to_string(state)
        qc_str = get_circuit(component.qc)
        out = f'Step {component.last_step()}\n-------\n\n{qc_str}\n\n{s}\n\n\n\n{out}'
    # else:
    #     s = component.get_state()
    #     # s = state_table_to_string(state)
    #     out = f'Initial state\n-------------\n\n{component.get_state()}'

    return pn.pane.Str(out)

component.reset()
out = f'Initial state\n-------------\n\n{component.get_state()}'

template.main.append(pn.Column(pn.bind(select_gate, gate), pn.bind(apply, go)))
template.servable()

