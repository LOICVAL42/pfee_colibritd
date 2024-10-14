from mpqp import QCircuit
from mpqp.gates import Gate as MPQP_gate
from ..classes.gate import Gate
import numpy as np

def qCircuit_to_netlist(qCircuit: QCircuit) -> np.ndarray[MPQP_gate]:
    return [Gate(gate) for gate in qCircuit.instructions if isinstance(gate, MPQP_gate)]

def netlist_to_qCircuit(netlist: np.ndarray[MPQP_gate]) -> QCircuit:
    return QCircuit(netlist)