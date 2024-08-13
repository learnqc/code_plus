#!/usr/bin/env python -m panel serve


import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from components.any_qubit_component import AnyQubit
from components.common import arg_gates, gates, get_circuit, state_table_to_string

import panel as pn

# # Explicitly set template and add some text to the header area
template = pn.template.BootstrapTemplate(title='Any Qubit Circuit')

qubits = pn.widgets.NumberInput(name='Number of qubits', start=1, end=5)

target = pn.widgets.NumberInput(name='Target', start=0, disabled=True)

gate = pn.widgets.Select(name='Gate', options=[None] + [gate.upper() for gate in gates], disabled=True)
arg = pn.widgets.NumberInput(name='Angle (in degrees)', disabled=True)
go = pn.widgets.Button(name='Apply', button_type='primary', disabled=True)

template.sidebar.extend([qubits, target, gate, arg, go])

component = None


def select_qubits(v):
    global component
    component = AnyQubit(qubits.value)

    target.end = qubits.value - 1
    target.disabled = qubits.value is None or qubits.value < 1

    global out
    out = f'Initial state\n-------------\n\n{component.get_state()}'

    go.value = True


def select_target(v):
    gate.disabled = target.value is None


def select_gate(v):
    arg.disabled = gate.value is None or not (gate.value.lower() in arg_gates)
    go.disabled = gate.value is None


def apply(v):
    global out
    if go.value is True and gate.value is not None:
        component.apply_gate(target.value, gate.value.lower(), arg.value)
        gate.value = None
        arg.value = None
        arg.disabled = True
        go.value = False

        s = component.get_state()

        qc_str = get_circuit(component.qc)
        out = f'Step {component.last_step()}\n-------\n\n{qc_str}\n\n{s}\n\n\n\n{out}'

    return pn.pane.Str(out)


out = ''

template.main.append(pn.Column(pn.bind(select_qubits, qubits),
                               pn.bind(select_target, target),
                               pn.bind(select_gate, gate),
                               pn.bind(apply, go)))
template.servable()

