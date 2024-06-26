#!/usr/bin/env python -m panel serve

import pathlib
import sys
from enum import Enum


from hume.simulator.circuit import QuantumCircuit, QuantumRegister
from hume.qiskit.util import hume_to_qiskit
from hume.utils.common import complex_to_rgb
from math import log2, floor, log10, atan2, pi
# from components.common import Display, get_circuit, state_table_to_string
import panel as pn


class Display(Enum):
    BROWSER = 1
    TERMINAL = 2
def get_circuit(qc):
    qc_qiskit = hume_to_qiskit(qc.regs, qc.transformations)
    qc_str = str(qc_qiskit.draw())
    print(qc_str)
    return qc_str

def state_table_to_string(state, display=Display.BROWSER, decimals=4, symbol='\u2588'):
    assert (decimals <= 10)
    n = int(log2(len(state)))
    round_state = [round(state[k].real, decimals) + 1j * round(state[k].imag, decimals) for k in range(len(state))]

    headers = ['Outcome', 'Binary', 'Amplitude', 'Magnitude', 'Direction', 'Amplitude Bar', 'Probability']
    offsets = [max(len(headers[0]), floor(log10(len(state)))),  # outcome
               max(len(headers[1]), n),  # binary
               max(len(headers[2]), 2 * (decimals + 2) + 6),  # amplitude
               max(len(headers[3]), (decimals + 2)),  # magnitude
               max(len(headers[4]), decimals),  # direction
               max(len(headers[5]), 24),  # amplitude bar
               max(len(headers[6]), decimals + 2),  # probability
               ]

    for i in range(len(offsets)):
        headers[i] = headers[i] + ' ' * (offsets[i] - len(headers[i]))

    header_str = '  '.join(headers)

    output = '\n'
    output += header_str
    output += '\n'
    output += len(header_str) * '-'
    output += '\n'

    for k in range(len(round_state)):
        direction = round(atan2(round_state[k].imag, round_state[k].real) * 180 / pi, 2)

        output += '  '.join([str(k).ljust(offsets[0], ' '),

                             str(bin(k)[2:].zfill(n)).ljust(offsets[1] - 1, ' '),

                             ((' ' if round_state[k].real >= 0 else '-') +
                              str(abs(round_state[k].real)).ljust(decimals + 2, '0') +
                              (' + ' if round_state[k].imag >= 0 else ' - ') + 'i' +
                              str(abs(round_state[k].imag)).ljust(decimals + 2, '0')).ljust(offsets[2] + 1, ' '),

                             str(round(abs(state[k]), decimals)).ljust(decimals + 2, ' ').ljust(offsets[3], ' '),

                             (str(((' ' if direction >= 0 else '-') + str(floor(abs(direction)))).rjust(4, ' ') +
                                  '.' + str(int(100 * round(direction - floor(direction), 2))).ljust(2,
                                                                                                     '0')) + '\u00b0' if
                              abs(round_state[k]) > 0 else offsets[4] * ' ').ljust(offsets[4], ' '),

                             f'<font style="color:rgb{complex_to_rgb(round_state[k], ints=True)}">' + (
                                         int(abs(state[k] * 24)) * symbol).ljust(offsets[5],
                                                                                 ' ') + '</font>' if display == display.BROWSER else
                             fg(*[int(255 * a) for a in complex_to_rgb(state[k])]) + (
                                         int(abs(state[k] * 24)) * symbol).ljust(offsets[5], ' ') + fg.rs,

                             str(round(abs(state[k]) ** 2, decimals)).ljust(decimals + 2, ' ')
                             ])
        output += '\n'

    return output

# template = pn.template.BootstrapTemplate(title='Building Quantum Software')

# template.header.append('### Frequency Encoding')

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
widgets = pn.Column(qubits, frequency, sizing_mode='fixed', width=100)

display = pn.GridBox(
    mapped,
    circuit,
    state,
    ncols=1,
    sizing_mode='fixed',
    width = 800
)

pn.Column(widgets, display)

pn.template.MaterialTemplate(
    title="Frequency Encoding",
    sidebar=[qubits, frequency],
    main=[display],
).servable();