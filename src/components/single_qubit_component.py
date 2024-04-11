from enum import Enum
from math import log2, floor, log10, atan2, pi

from hume.qiskit.util import hume_to_qiskit
from hume.simulator.circuit import QuantumCircuit, QuantumRegister
from hume.utils.common import complex_to_rgb
from sty import fg

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


class Display(Enum):
    BROWSER = 1
    TERMINAL = 2


class SingleQubit():

    def __init__(self, display=Display.BROWSER):
        self.display = display
        self.qc = QuantumCircuit(QuantumRegister(1))

    def apply_gate(self, gate, angle=None, report=True):
        gate = gate.lower()
        if gate in arg_gates:
            assert(angle is not None)
        add_gate(self.qc, [], 0, gate, angle/180*pi if gate in arg_gates else None)
        if report:
            self.qc.report(f'Step {len(self.qc.reports) + 1}')

    def get_state(self):
        if not self.qc.reports:
            state = self.qc.state
        else:
            state = self.qc.reports[f'Step {len(self.qc.reports)}'][2]

        print(state_table_to_string(state, display=Display.TERMINAL))
        if self.display == Display.TERMINAL:
            return ''
        else:
            return f'{state_table_to_string(state)}'

    # def report(self):
    #     return self.qc.report(f'Step {len(self.qc.reports)}')[2]

    def get_circuit(self):
        qc_qiskit = hume_to_qiskit(self.qc.regs, self.qc.transformations)
        qc_str = str(qc_qiskit.draw())
        print(qc_str)
        return qc_str

    def reset(self):
        self.qc = QuantumCircuit(QuantumRegister(1))

    def last_step(self):
        return len(self.qc.reports)

    def run(self):
        return self.qc.run()


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


def state_table_data(s, cols=list(range(8)), neg=False):
    data = [[str(k - len(s)) if neg and k >= len(s) / 2 else k,
             bin(k)[2:].zfill(int(log2(len(s)))),
             s[k],
             str(round(atan2(s[k].imag, s[k].real) / (2 * pi) * 360, 1)) + '\u00b0' if abs(s[k]) > 10 ** -4 else '',
             abs(s[k]),
             s[k],
             abs(s[k]) ** 2,
             abs(s[k] ** 2)] for k in range(len(s))]

    return [[data[k][col] for col in cols] for k in range(len(data))]
