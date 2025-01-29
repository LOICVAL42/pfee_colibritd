import copy
from mpqp.gates import Gate as MPQP_gate
from mpqp.gates import ControlledGate
from typing import List, Optional


class Gate:
    def __init__(self, gate: MPQP_gate, phase_index = -1):
        self.targets = gate.targets
        self.label = gate.label
        if isinstance(gate, ControlledGate):
            self.controls = gate.controls
        else:
            self.controls = None
        self.gate = gate
        # used in subgraph extraction
        self.phase_index = phase_index

    def __repr__(self):
        return f"{self.label}({self.targets})" if self.controls == None else f"{self.label}(·{self.controls}, {self.targets})"

    def is_single_qubit_gate(self) -> bool:
        return self.controls == None and len(self.targets) == 1

    def create_inverse(self):
        gate = Gate(self.gate)
        gate.inverse()
        return gate

    def inverse(self) -> None:
        if not self.is_single_qubit_gate():
            raise Exception("Only need to invert single qubit gates")
        self.label = self.label[:-1] if self.label[-1] == '†' else self.label + '†'
        self.gate.label = self.label
        self.gate = self.gate.inverse()

    def is_inverse(self, other_gate) -> bool:
        if not self.is_single_qubit_gate() or not other_gate.is_single_qubit_gate():
            raise Exception("Verifying inverse on single qubit gates only")
        return self.gate.inverse().is_equivalent(other_gate.gate)

    def is_hadamard_gate(self) -> bool:
        return self.is_single_qubit_gate and self.label == "H"

    def is_phase_gate(self) -> bool:
        return self.is_single_qubit_gate() and (self.label == "S" or self.label == "S†")

    def is_P_gate(self) -> bool:
        return self.is_single_qubit_gate() and self.label in ["S", "S†", "T", "T†"]
    
    def is_Rz_gate(self) -> bool:
        return self.is_single_qubit_gate() and self.label in ["Rz", "Rz†"]