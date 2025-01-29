from mpqp.gates import Rz, CNOT, S
from ..classes.gate import Gate
import numpy as np
from ..tools.tools_phase_polynomial import extract_control_target, extract_p_number


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
            phase_index = gate.phase_index
            phase_poly.append(f"(x{target} ⊕ x{control}) p{phase_index}")
        elif gate.label == 'X':
            phase_poly.append(f"x{gate.targets[0]} ⊕ 1")
        else:
            raise TypeError("It's not a X, Rz or Cnot")
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
            phase_poly = extract_p_number(term)
            circuit.append(Gate(CNOT(control=control, target=target),phase_poly))
        else:
            theta, target = term
            circuit.append(Gate(Rz(theta, target)))
    
    return circuit



