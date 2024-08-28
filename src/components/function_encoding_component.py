from enum import Enum
from math import pi, log2

from hume.simulator.circuit import QuantumRegister, QuantumCircuit
from hume.utils.common import complex_to_rgb

import panel as pn
import sympy as sp
from sty import bg, fg

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