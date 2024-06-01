from math import pi

from hume.qiskit.util import hume_to_qiskit
from hume.simulator.circuit import QuantumCircuit, QuantumRegister

from components.common import arg_gates, add_gate, Display, state_table_to_string


class SingleQubit():

    def __init__(self, display=Display.BROWSER):
        self.display = display
        self.qc = QuantumCircuit(QuantumRegister(1))

    def apply_gate(self, gate, angle=None, report=True):
        gate = gate.lower()
        if gate in arg_gates:
            assert(angle is not None)
        add_gate(self.qc, [], 0, gate, angle if gate in arg_gates else None)
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
            return (''.join(['{0} -> {1}\n'.format(k, v) for k,v in enumerate(map(str, state))]), f'{state_table_to_string(state)}')

    # def report(self):
    #     return self.qc.report(f'Step {len(self.qc.reports)}')[2]

    def get_circuit(self):
        qc_qiskit = hume_to_qiskit(self.qc.regs, self.qc.transformations)
        qc_str = str(qc_qiskit.draw())
        print(qc_str)
        return ('The circuit is shown by the system.', qc_str)

    def reset(self):
        self.qc = QuantumCircuit(QuantumRegister(1))

    def last_step(self):
        return len(self.qc.reports)

    def run(self):
        return self.qc.run()


