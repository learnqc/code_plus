from enum import Enum
from math import pi, log2, log10, floor, atan2

from hume.simulator.circuit import QuantumRegister, QuantumCircuit
from hume.utils.common import complex_to_rgb

import panel as pn
import sympy as sp

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

                             f'<font style="color:rgb{complex_to_rgb(round_state[k], ints=True)}">' + (
                                         int(abs(state[k] * 24)) * symbol).ljust(offsets[5],
                                                                                 ' ') + '</font>' if display == display.BROWSER else
                             fg(*[int(255 * a) for a in complex_to_rgb(state[k])]) + (
                                         int(abs(state[k] * 24)) * symbol).ljust(offsets[5], ' ') + fg.rs,

                             str(round(abs(state[k]) ** 2, decimals)).ljust(decimals + 2, ' ')
                             ])
        output += '\n'

    return output

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

# polynomial stuff
def get_boolean_poly(poly_str, num_bits):
    def to_binary(num, num_bits):
        return [int(i) for i in format(num, '0' + str(num_bits) + 'b')]

    def generate_binary_values(num_bits):
        return [to_binary(i, num_bits) for i in range(2**num_bits)]

    def boolean_polynomial(func, num_bits):
        terms = {}

        binary_values = generate_binary_values(num_bits)

        for binary_x in binary_values:
            x = int(''.join(map(str, binary_x)), 2)
            fx = func(x)
            
            for bit_values in binary_values:
                term_val = 1
                for bit, value in zip(binary_x, bit_values):
                    if bit != value:
                        term_val = 0
                        break
                if term_val:
                    term_key = tuple(i for i, bit in enumerate(bit_values) if bit)
                    if term_key in terms:
                        terms[term_key] += fx
                    else:
                        terms[term_key] = fx

        return [(coef, list(term)) for term, coef in terms.items() if coef != 0]

    def polynomial_func_factory(my_poly):
        x = sp.Symbol('x')
        def polynomial_func(x_val):
            return int(my_poly.eval(x_val))
        return polynomial_func
    x = sp.Symbol('x')
    my_poly = sp.polys.polytools.poly_from_expr(poly_str)[0]
    polynomial_func = polynomial_func_factory(my_poly)
    boolean_poly = boolean_polynomial(polynomial_func, num_bits)
    return boolean_poly