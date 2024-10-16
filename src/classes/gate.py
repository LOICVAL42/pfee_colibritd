from mpqp.gates import Gate as MPQP_gate
from mpqp.gates import ControlledGate
from typing import List, Optional


class Gate:
    def __init__(self, gate: MPQP_gate):
        self.targets = gate.targets
        self.label = gate.label
        if isinstance(gate, ControlledGate):
            self.controls = gate.controls
        else:
            self.controls = None
        self.gate = gate

    def __repr__(self):
        return f"{self.label}({self.targets})" if self.controls == None else f"{self.label}(·{self.controls}, {self.targets})"

    def is_single_qubit_gate(self) -> bool:
        return self.controls == None and len(self.targets) == 1