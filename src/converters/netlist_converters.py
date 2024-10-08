from mpqp import QCircuit
from mpqp.gates import Gate
import numpy as np

def qCircuit_to_netlist(qCircuit: QCircuit) -> np.ndarray[Gate]:
    return [gate for gate in qCircuit.instructions if isinstance(gate, Gate)]

def netlist_to_qCircuit(netlist: np.ndarray[Gate]) -> QCircuit:
    return QCircuit(netlist)