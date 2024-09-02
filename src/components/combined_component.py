from enum import Enum
from math import pi, log2, log10, floor, atan2

from hume.simulator.circuit import QuantumRegister, QuantumCircuit
from hume.utils.common import complex_to_rgb

import panel as pn
import sympy as sp
from sty import bg, fg

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

# ----------------------- FUNCTION ENCODING FUNCTIONS ----------------------- #
def grid_state_html(state, m=1, neg=False, show_probs=False, symbol='\u2588'):
    n = int(log2(len(state))) - m
    cols = 2**m
    rows = int(len(state) / cols) # first register
    # adding styles
    html_table = '<style> table, th, td {border: 1px solid black; border-collapse: collapse;} th, td { padding-top: 5px; padding-bottom: 5px; padding-left: 10px; padding-right: 10px;}</style>'
    html_table += '<table>'

    # header row
    headers = []
    headers.append(f'<th></th>')
    for l in range(cols):
        headers.append(f'<th>{l} = {bin(l)[2:].zfill(m)}</th>')
    html_table += '<tr>' + ''.join(headers) + '</tr>'

    # rows
    if neg:
        range_func = lambda x: list(range(x // 2))[::-1] + list(range(x // 2, x))[::-1]
    else:
        range_func = lambda x: range(x)[::-1]

    for k in range_func(rows):
        row_label = f'{(k if k < rows / 2 else k - rows)} = {bin(k)[2:].zfill(n)}' if neg else f'{k} = {bin(k)[2:].zfill(n)}'
        row = f'<tr><td>{row_label}</td>'

        for l in range(cols):
            index = k * cols + l
            color = complex_to_rgb(state[index], True)
            magnitude = int(abs(state[index] * 10))
            probability = round(abs(state[index]) ** 2, 2) if show_probs and abs(state[index]) > 0.01 else ''
            # Construct cell with embedded style
            row += f'<td><font style="color:rgb{color}">{symbol * magnitude}</font>&nbsp;{probability}</td>'

        html_table += row + '</tr>'

    html_table += '</table>'

    return html_table

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
    var_list = [sp.Symbol(f'x{i}') for i in range(num_bits)]

    if is_poly:
        try:
            temp = [f'{2 ** i}*x{i}' for i in range(num_bits)]
            bin_var_str = '+'.join(temp[::-1])
            bin_var = sp.sympify(bin_var_str)
            new_poly = poly_str.replace('x', f"({str(bin_var)})")
            s = sp.poly(new_poly)
        except:
            return "Error: Polynomial should be in form of a*x**n + b*x**(n-1) + ... + z*x + c"
    else:
        new_poly = poly_str
        expr = sp.sympify(new_poly)
        s = sp.poly(expr, var_list)

        for symbol in s.free_symbols:
            if symbol not in var_list:

                return f"Error: {symbol} is invalid"
            
        # for term in s.terms():
        #     if sum(term[0]) < 1:
        #         return "Error: No constants"
    
    terms = s.terms()

    poly = [(int(term[1]), [i for i, val in enumerate(term[0]) if val > 0]) for term in terms]

    return poly

# ----------------------- FREQUENCY ENCODING FUNCTIONS ----------------------- #
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


# ----------------------- SINGLE QUBIT FUNCTIONS ----------------------- #
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

# ----------------------- MULTI QUBIT FUNCTIONS ----------------------- #
def create_multi_qubit(qubits):
    return QuantumCircuit(QuantumRegister(qubits))


def apply_gate_multi(qc, target, gate, angle=None, report=True):
    gate = gate.lower()
    if gate in arg_gates:
        assert (angle is not None)
    add_gate(qc, [], target, gate, angle / 180 * pi if gate in arg_gates else None)
    if report:
        qc.report(f'Step {len(qc.reports) + 1}')

def last_step_multi(qc):
    return len(qc.reports)

def get_state_multi(qc):
    if not qc.reports:
        state = qc.state
    else:
        state = qc.reports[f'Step {len(qc.reports)}'][2]

    # print(state_table_to_string(state, display=Display.TERMINAL))
    return f'{state_table_to_string(state)}'


def reset_multi(qc, qubits):
    qc = QuantumCircuit(QuantumRegister(qubits))

def last_step_multi(qc):
    return len(qc.reports)