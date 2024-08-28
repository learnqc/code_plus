#!/usr/bin/env python -m panel serve


import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))

from components.common import *
from components.frequency_encoding_component import *
from components.function_encoding_component import *
from components.combined_component import *
import panel as pn

app_select = pn.widgets.Select(name="App", options=['Select', 'Any qubit', 'Single qubit', 'Function encoding',
                                                    'Frequency encoding'])

widgets = pn.Column(app_select)

display = pn.Column()

pn.template.MaterialTemplate(
    title="Building Quantum Software",
    sidebar=[widgets],
    main=[display],
).servable()



@pn.depends(app_select, watch=True, on_init=True)
def run(v):
    # js.clearInputs()
    while(len(widgets) > 1):
        widgets.pop(1)

    # js.clearInfo()
    while (len(display) > 0):
        display.pop(0)

    if app_select.value == 'Any qubit':
        qubits = pn.widgets.NumberInput(name='Number of qubits', start=1, end=5)
        target = pn.widgets.NumberInput(name='Target', start=0, disabled=True)
        gate = pn.widgets.Select(name='Gate', options=[None] + [gate.upper() for gate in gates])
        arg = pn.widgets.NumberInput(name='Angle (in degrees)', disabled=True)
        go = pn.widgets.Button(name='Apply', button_type='primary')

        widgets.extend([qubits, target, gate, arg, go])

        info = pn.pane.Str('')

        global qc
        qc = create_any_qubit(qubits.value)
        c = pn.pane.Str(f'Circuit:\n{get_circuit(qc)}'.strip())
        display.append(c)
        display.append(info)
        target.end = qubits.value - 1
        target.disabled = qubits.value is None or qubits.value < 1
        global output
        output = f'Initial state\n-------------\n\n{get_state_any(qc)}'
        go.value = True
        info.object = output

        display.append(info)

        @pn.depends(qubits, watch=True, on_init=True)
        def select_qubits(v):
            global qc
            qc = create_any_qubit(qubits.value)
            c = pn.pane.Str(f'Circuit:\n{get_circuit(qc)}'.strip())
            display.pop(0)
            display.insert(0, c)
            target.end = qubits.value - 1
            target.disabled = qubits.value is None or qubits.value < 1
            global output
            output = f'Initial state\n-------------\n\n{get_state_any(qc)}'
            go.value = True
            info.object = output

        @pn.depends(target, watch=True)
        def select_target(v):
            gate.disabled = target.value is None

        @pn.depends(gate, watch=True)
        def select_gate(v):
            arg.disabled = gate.value is None or not (gate.value.lower() in arg_gates)
            go.disabled = gate.value is None

        @pn.depends(go, watch=True)
        def apply(v):
            global qc
            global output
            if go.value is True and gate.value is not None:
                apply_gate_any(qc, target.value, gate.value.lower(), arg.value)
                gate.value = None
                arg.value = None
                arg.disabled = True
                go.value = False

                s = get_state_any(qc)

                c = pn.pane.Str(f'Circuit:\n{get_circuit(qc)}'.strip())
                display.pop(0)
                display.insert(0, c)

                output = f'Step {last_step(qc)}\n-------\n\n{s}\n\n{output}'

            info.object = output

    if app_select.value == 'Single qubit':
        gate = pn.widgets.Select(name='Gate', options=[None] + [gate.upper() for gate in gates])
        arg = pn.widgets.NumberInput(name='Angle (in degrees)', disabled=True)
        go = pn.widgets.Button(name='Apply', button_type='primary')

        widgets.extend([gate, arg, go])

        info = pn.pane.Str('')

        qc = create_single_qubit()
        c = pn.pane.Str(f'Circuit:\n{get_circuit(qc)}'.strip())
        display.append(c)
        display.append(info)
        global out

        @pn.depends(gate, watch=True)
        def select_gate(v):
            arg.disabled = gate.value is None or not (gate.value.lower() in arg_gates)
            print('gate', v)

        @pn.depends(go, watch=True)
        def apply(v):
            global out
            if go.value is True and gate.value is not None:
                # add_gate(qc, [], 0, gate.value.lower(), arg.value/180*pi if gate.value.lower() in arg_gates else None)
                apply_gate(qc, gate.value.lower(), arg.value)
                gate.value = None
                arg.value = None
                arg.disabled = True
                go.value = False

                s = get_state(qc)

                qc_str = get_circuit(qc)  # component.get_circuit()
                c = pn.pane.Str(f'Circuit:\n{qc_str}'.strip())
                display.pop(0)
                display.insert(0, c)

                print(display)
                out = f'Step {last_step(qc)}\n-------\n{s}\n{out}'

            info.object = out

        reset(qc)

        out = f'Initial state\n-------------\n\n{get_state(qc)}'
        info.object = out

    if app_select.value == 'Function encoding':
        n_key = pn.widgets.IntInput(name="# Input Qubits", value=2)
        n_value = pn.widgets.IntInput(name="# Output Qubits", value=4)
        input_select = pn.widgets.Select(name="Type of input", options=['Integer variable', 'Binary variable'], value='Integer variable')
        poly = pn.widgets.TextInput(name="Function", value = 'x**2')
        go = pn.widgets.Button(name='Apply', button_type='primary')
        negative = pn.widgets.Select(name="Negative values for output?", options=['Yes', 'No'], value ='No')

        widgets.extend([n_key, n_value, poly, input_select, negative, go])

        @pn.depends(input_select, watch=True)
        def change_expression(v):
            if input_select.value == 'Binary variable':
                poly.value = 'x0'

            else:
                poly.value = 'x**2'
        @pn.depends(go, watch=True)

        def function_encoding(v):
            while(len(display) > 0):
                display.pop(0)

            coeffs = terms_from_poly(poly.value, n_key.value, input_select.value == 'Integer variable')
            qc = build_polynomial_circuit(n_key.value, n_value.value, coeffs)

            c = f'Circuit:\n{get_circuit(qc)}'

            state = qc.reports['qpe'][2]
            # grid_state = grid_state_html(state, n_key.value, negative.value == 'Yes', True)
            grid_state = grid_state_html(state, n_key.value, negative.value == 'Yes', True)
            s = f'State:\n{grid_state}'
            # s = f'State:\n{state_table_to_string(state)}'

            grid = pn.pane.HTML(f'{s}')
            out = pn.pane.Str(f'{c}\n\n')
            display.append(grid)
            display.append(out)

            return out



    if app_select.value == 'Frequency encoding':
        qubits = pn.widgets.IntInput(name="Qubits", value=3, start=1, end=5)
        frequency = pn.widgets.FloatInput(name="Frequency", value=4.3, start=0)
        go = pn.widgets.Button(name='Apply', button_type='primary')

        widgets.extend([qubits, frequency, go])

        @pn.depends(go, watch=True)
        def run(v):
            while(len(display) > 0):
                display.pop(0)

            qc = encode_frequency(qubits.value, frequency.value)
            c = f'Circuit:\n{get_circuit(qc)}'

            state = qc.reports['iqft'][2]
            s = f'State:{state_table_to_string(state)}'


            n = qubits.value
            v = frequency.value
            f = (f'Frequency:\n{v}' + (f' mapped to {round(v % 2 ** n, 2)}' if v >= 2 ** n or v < 0 else ''))

            out = pn.pane.Str(f'{s}\n\n{f}\n\n{c}')
            display.append(out)
            return out

