from mpqp.gates import Rz, CNOT
from ..classes.gate import Gate
import numpy as np

import re

def extract_control_target(term):
    """
    Extracts control and target qubits from a CNOT term in the form "x1 ⊕ x2".
    
    :param term: A string representing a CNOT gate in the form "x1 ⊕ x2".
    :return: A tuple (control, target) with the control and target qubits as integers.
    """
    match = re.search(r"x(\d+)\s⊕\s*x(\d+)", term)
    if match:
        control = int(match.group(1))
        target = int(match.group(2))
        return control, target
    else:
        raise ValueError("Format invalide pour le terme CNOT")


def create_phase_polynomial_from_netlist(netlist: np.ndarray[Gate]):
    """
    Converts a circuit of Rz, CNOT, and NOT gates into a phase polynomial.

    :param netlist: List of Gate objects in the circuit.
    :return: A phase polynomial representing the circuit.
    """
    phase_poly = []
    
    for gate in netlist:
        if gate.label == 'Rz':
            phase_poly.append((gate.gate.theta, gate.targets[0]))
        elif gate.label == 'CNOT':
            control, target = gate.controls[0], gate.targets[0]
            phase_poly.append(f"(x{control} ⊕ x{target})")
        elif gate.label == 'X':
            phase_poly.append(f"x{gate.targets[0]} ⊕ 1")
    
    return phase_poly



def create_netlist_from_phase_polynomial(phase_poly):
    """
    Recreates a circuit from a phase polynomial.

    :param phase_poly: Dictionary representing the phase polynomial for each qubit.
    :return: A list of quantum gates corresponding to the polynomial.
    """

    circuit = []
    
    for term in phase_poly:
        if isinstance(term, str) and '⊕' in term:
            control, target = extract_control_target(term)
            circuit.append(Gate(CNOT(control=control, target=target)))
        else:
            theta, target = term
            circuit.append(Gate(Rz(theta, target)))
    
    return circuit



