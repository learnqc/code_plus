from math import pi

from hume.simulator.circuit import QuantumCircuit, QuantumRegister

from components.common import Display, arg_gates, add_gate, state_table_to_string


class AnyQubit():

    def __init__(self, qubits, display=Display.BROWSER):
        self.display = display
        self.qubits = qubits
        self.qc = QuantumCircuit(QuantumRegister(qubits))

    def apply_gate(self, target, gate, angle=None, report=True):
        gate = gate.lower()
        if gate in arg_gates:
            assert(angle is not None)
        add_gate(self.qc, [], target, gate, angle / 180 * pi if gate in arg_gates else None)
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

    def reset(self):
        self.qc = QuantumCircuit(QuantumRegister(self.qubits))

    def last_step(self):
        return len(self.qc.reports)

    def run(self):
        return self.qc.run()
