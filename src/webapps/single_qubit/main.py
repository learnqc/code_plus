from enum import Enum
from math import pi, log2, log10, floor, atan2

from hume.simulator.circuit import QuantumRegister, QuantumCircuit
from hume.utils.common import complex_to_rgb

import panel as pn

pn.extension(sizing_mode="stretch_width")


def circuit_to_string(qc):
    qs = [{ 'id': i } for i in range(sum(qc.regs))]
    ops = [{'gate': tr.name.upper() if tr.arg is None else f'{tr.name.upper()}({round(tr.arg, 2)})',
            'isControlled': len(tr.controls) > 0,
            'controls': [{ 'qId': c } for c in tr.controls],
            'targets': [{ 'qId': tr.target }]} for tr in qc.transformations]

    circ = {'qubits': qs, 'operations': ops}
    return str(circ).replace('True', 'true').replace('False', 'false')


class Display(Enum):
    BROWSER = 1
    TERMINAL = 2



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

                             f'<font style="color:rgb{tuple(complex_to_rgb(round_state[k], ints=True))}">' + (
                                     int(abs(state[k] * 24)) * symbol).ljust(offsets[5],
                                                                             ' ') + '</font>' if display == display.BROWSER else
                             fg(*[int(255 * a) for a in complex_to_rgb(state[k])]) + (
                                     int(abs(state[k] * 24)) * symbol).ljust(offsets[5], ' ') + fg.rs,

                             str(round(abs(state[k]) ** 2, decimals)).ljust(decimals + 2, ' ')
                             ])
        output += '\n'

    return output

no_arg_gates = ['h', 'x', 'y', 'z']
arg_gates = ['p', 'rx', 'ry', 'rz']
gates = no_arg_gates + arg_gates


def add_gate(qc, cs, target, gate, angle):
    if len(cs) == 1:
        gate = 'c' + gate
    elif len(cs) > 1:
        gate = 'mc' + gate

    m = getattr(qc, gate)

    if angle is None:
        if len(cs) == 1:
            m(cs[0], int(target))
        elif len(cs) > 1:
            m(cs, int(target))
        else:
            m(int(target))
    else:
        if len(cs) == 1:
            m(angle, cs[0], int(target))
        elif len(cs) > 1:
            m(angle, cs, int(target))
        else:
            m(angle, int(target))
def create_single_qubit():
    return QuantumCircuit(QuantumRegister(1))


def apply_gate(qc, gate, angle=None, report=True):
    gate = gate.lower()
    if gate in arg_gates:
        assert (angle is not None)
    add_gate(qc, [], 0, gate, angle / 180 * pi if gate in arg_gates else None)
    if report:
        qc.report(f'Step {len(qc.reports) + 1}')

def last_step(qc):
    return len(qc.reports)

def get_state(qc):
    if not qc.reports:
        state = qc.state
    else:
        state = qc.reports[f'Step {len(qc.reports)}'][2]

    # print(state_table_to_string(state, display=Display.TERMINAL))
    return f'{state_table_to_string(state)}'

def reset(qc):
    qc = QuantumCircuit(QuantumRegister(1))

def last_step(qc):
    return len(qc.reports)