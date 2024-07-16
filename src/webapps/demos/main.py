from enum import Enum
from math import pi, log2, log10, floor, atan2

from hume.simulator.circuit import QuantumRegister, QuantumCircuit
from hume.utils.common import complex_to_rgb

import panel as pn
import sympy as sp
from sty import bg, fg

from tabulate import tabulate

pn.extension(sizing_mode="stretch_width")

class Display(Enum):
    BROWSER = 1
    TERMINAL = 2

def circuit_to_string(qc):
    qs = [{ 'id': i } for i in range(sum(qc.regs))]
    ops = [{'gate': tr.name.upper() if tr.arg is None else f'{tr.name.upper()}({round(tr.arg, 2)})',
            'isControlled': len(tr.controls) > 0,
            'controls': [{ 'qId': c } for c in tr.controls],
            'targets': [{ 'qId': tr.target }]} for tr in qc.transformations]

    circ = {'qubits': qs, 'operations': ops}
    return str(circ).replace('True', 'true').replace('False', 'false')

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

def grid_state(state, m=1, neg=False, show_probs=False):
    n = int(log2(len(state))) - m
    cols = 2**m
    rows = int(len(state) / cols) # first register
    print('\n')
    if neg:
        out = tabulate([[(str(k) if k < rows/2 else str(k - rows)) + ' = ' + bin(k)[2:].zfill(n)] + [
            (' ' + (str(round(abs(state[k*cols + l])**2, 2)) if abs(state[k*cols + l]) > 0.01 else ''))
            for l in range(cols)] for k in list(range(int(rows/2)))[::-1] + list(range(int(rows/2), rows))[::-1]],
                       headers=[str(l) + ' = ' + bin(l)[2:].zfill(m) for l in range(cols)],
                       tablefmt='fancy_grid')
    else:
        out = tabulate([[str(k) + ' = ' + bin(k)[2:].zfill(n)] + [
            (' ' + (str(round(abs(state[k*cols + l])**2, 2)) if abs(state[k*cols + l]) > 0.01 else ''))
            for l in range(cols)] for k in range(rows)[::-1]],
                       headers=[str(l) + ' = ' + bin(l)[2:].zfill(m) for l in range(cols)],
                       tablefmt='fancy_grid')

    return out

# ----------------------- QPE FUNCTIONS ----------------------- #
def encode_term(coeff, vars, circuit, key, value):
    if isinstance(coeff, int) is False:
        coeff = coeff.value
    for i in range(len(value)):
        if len(vars) > 1:
            # circuit.mcp(2*pi * 2 ** (i - N) * coeff, [key[j] for j in vars], value[i])
            circuit.mcp(pi * 2 ** -i * coeff, [key[j] for j in vars], value[i])
        elif len(vars) > 0:
            # circuit.cp(2*pi * 2 ** (i - N) * coeff, key[vars[0]], value[i])
            circuit.cp(pi * 2 ** -i * coeff, key[vars[0]], value[i])
        else:
            # circuit.p(2*pi * 2 ** (i - N) * coeff, value[i])
            circuit.p(pi * 2 ** -i * coeff, value[i])

def build_polynomial_circuit(key_size, value_size, terms):
    key = QuantumRegister(key_size)
    value = QuantumRegister(value_size)
    circuit = QuantumCircuit(key, value)

    for i in range(len(key)):
        circuit.h(key[i])

    for i in range(len(value)):
        circuit.h(value[i])

    for (coeff, vars) in terms:
        encode_term(coeff, vars, circuit, key, value)

    circuit.iqft(value[::-1], swap=False)

    circuit.report('qpe')
    return circuit

def terms_from_poly(poly_str, num_bits, is_poly):
    for i in range(num_bits):
        globals()[f'x{i}'] = sp.Symbol(f'x{i}')

    if is_poly:
        temp = [f'{2 ** i}*x{i}' for i in range(num_bits)]
        bin_var_str = '+'.join(temp[::-1])
        bin_var = sp.sympify(bin_var_str)

        new_poly = poly_str.replace('x', f"({str(bin_var)})")
    else:
        new_poly = poly_str
    s = sp.poly(new_poly)

    terms = s.terms()

    poly = []
    for term in terms:
        temp = (int(term[1]), [int(i) for i in range(len(term[0])) if term[0][i] > 0])
        poly.append(temp)

    return poly

# ----------------------- FE FUNCTIONS ----------------------- #
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