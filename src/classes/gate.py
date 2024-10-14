from mpqp.gates import Gate as MPQP_gate
from typing import List, Optional


class Gate:
    def __init__(self, gate: MPQP_gate):
        self.targets = gate.targets
        self.label = gate.label
        self.gate = gate

    def __repr__(self):
        return f"{self.label}({self.targets})"