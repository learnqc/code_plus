import pathlib
import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
from components.function_encoding_component import *

from enum import Enum
from math import pi, log2

from hume.qiskit.util import hume_to_qiskit

import panel as pn
import sympy as sp
from sty import bg, fg

def get_circuit(qc):
    qc_qiskit = hume_to_qiskit(qc.regs, qc.transformations)
    qc_str = str(qc_qiskit.draw())
    print(qc_str)
    return qc_str


e1 = 'x**2'
p1 = terms_from_poly(e1, 2, True)
print(p1)

e2 = 'x0 + 4*x0*x1 + 4*x1'
p2 = terms_from_poly(e2, 2, False)
print(p2)

c1 = build_polynomial_circuit(2, 4, p1)
c2 = build_polynomial_circuit(2, 4, p2)

widgets = pn.Column()
display = pn.Column()

pn.template.MaterialTemplate(
    title="Function Encoding",
    sidebar=[widgets],
    main=[display],
).servable()

s1 = c1.reports['qpe'][2]
s2 = c2.reports['qpe'][2]

g1 = pn.pane.HTML(grid_state_html(s1, 2, False, True))
g2 = pn.pane.HTML(grid_state_html(s2, 2, False, True))

display.extend([g1, g2])