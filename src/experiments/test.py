from enum import Enum
from math import pi, log2

from hume.simulator.circuit import QuantumRegister, QuantumCircuit
from hume.utils.common import complex_to_rgb

import panel as pn
import sympy as sp
from sty import bg, fg


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
                return "Error: Invalid symbol"
            
        for term in s.terms():
            if sum(term[0]) < 1:
                return "Error: No constants"
    
    terms = s.terms()
    print(f'terms for {poly_str}: {terms}')

    poly = [(int(term[1]), [i for i, val in enumerate(term[0]) if val > 0]) for term in terms]

    return poly

inputs = 2
outputs = 4
e1 = 'x0*x1'
p1 = terms_from_poly(e1, inputs, False)
print(p1)

e2 = 'x0'
p2 = terms_from_poly(e2, inputs, False)
print(p2)

e3 = 'x1'
p3 = terms_from_poly(e3, inputs, False)
print(p3)


c1 = build_polynomial_circuit(inputs, outputs, p1)
c2 = build_polynomial_circuit(inputs, outputs, p2)
c3 = build_polynomial_circuit(inputs, outputs, p3)


# e2 = '1*x**2 + 2*x + 3'
# p2 = terms_from_poly(e2, 2, True)
# print(p2)


def complex_to_rgb_ints(c):
    return [int(round(c * 255.0)) for c in complex_to_rgb(c)]

def grid_state(state, m=1, neg=False, show_probs=False):
    n = int(log2(len(state))) - m
    cols = 2**m
    rows = int(len(state) / cols) # first register
    from tabulate import tabulate
    print('\n')
    if neg:
        print(tabulate([[(str(k) if k < rows/2 else str(k - rows)) + ' = ' + bin(k)[2:].zfill(n)] + [
            bg(*complex_to_rgb_ints(state[k*cols + l]))+ int(abs(state[k*cols + l] * 10)) * ' ' + bg.rs +
            (' ' + (str(round(abs(state[k*cols + l])**2, 2)) if abs(state[k*cols + l]) > 0.01 else '') if show_probs else '')
            for l in range(cols)] for k in list(range(int(rows/2)))[::-1] + list(range(int(rows/2), rows))[::-1]],
                       headers=[str(l) + ' = ' + bin(l)[2:].zfill(m) for l in range(cols)],
                       tablefmt='fancy_grid'))
    else:
        print(tabulate([[str(k) + ' = ' + bin(k)[2:].zfill(n)] + [
            bg(*complex_to_rgb_ints(state[k*cols + l]))+ int(abs(state[k*cols + l] * 10)) * ' ' + bg.rs +
            (' ' + (str(round(abs(state[k*cols + l])**2, 2)) if abs(state[k*cols + l]) > 0.01 else '') if show_probs else '')
            for l in range(cols)] for k in range(rows)[::-1]],
                       headers=[str(l) + ' = ' + bin(l)[2:].zfill(m) for l in range(cols)],
                       tablefmt='fancy_grid'))
        
print(f'grid state for {e1}: {grid_state(c1.reports['qpe'][2], 2, False, True)}')
print(f'grid state for {e2}: {grid_state(c2.reports['qpe'][2], 2, False, True)}')
print(f'grid state for {e3}: {grid_state(c3.reports['qpe'][2], 2, False, True)}')
