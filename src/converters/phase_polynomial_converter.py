from mpqp.gates import Rz, CNOT
from ..classes.gate import Gate
import numpy as np

def hello():
    return "(hello)"

def create_phase_polynomial_from_netlist(netlist: np.ndarray[Gate]):
    """
    Convertit un circuit composé de portes Rz, CNOT, et NOT en polynôme de phase.
    
    :param circuit: Liste des objets Gate dans le circuit.
    :return: Un polynôme de phase représentant le circuit.
    """
    # Phase polynomiale pour chaque qubit
    phase_poly = {}
    
    # Initialiser les polynômes pour chaque qubit
    for gate in netlist:
        for qubit in gate.targets:
            if qubit not in phase_poly:
                phase_poly[qubit] = []
    
    # Parcourir les portes du circuit pour construire le polynôme
    for gate in netlist:
        if gate.label == 'Rz':
            qubit = gate.targets[0]
            angle = gate.gate.theta   # Paramètre d'angle pour la porte Rz
            phase_poly[qubit].append(angle)
        
        elif gate.label == 'CNOT':
            control_qubit = gate.controls[0]  # Le qubit de contrôle
            target_qubit = gate.targets[0]  # Le qubit cible
            # Modifier la dépendance du qubit cible par rapport au qubit de contrôle
            phase_poly[target_qubit].append(f"(x{control_qubit} ⊕ x{target_qubit})")
        
        elif gate.label == 'X':  # Pour une porte NOT (X)
            qubit = gate.targets[0]
            phase_poly[qubit].append(f"x{qubit} ⊕ 1")
    
    return phase_poly

def create_circuit_from_phase_polynomial(phase_poly):
    """
    Recrée un circuit à partir d'un polynôme de phase.
    
    :param phase_poly: Un dictionnaire représentant le polynôme de phase pour chaque qubit.
    :return: Une liste de portes quantiques qui correspond au polynôme.
    """
    circuit = []
    
    # Parcourir chaque qubit et ses termes dans le polynôme de phase
    for qubit, terms in phase_poly.items():
        for term in terms:
            if isinstance(term, str) and '⊕' in term:
                # C'est une porte CNOT
                control_qubit = int(term[term.find('x')+1:term.find('⊕')].strip())
                target_qubit = qubit
                cnot_gate = Gate(CNOT(control = control_qubit, target = target_qubit))
                circuit.append(cnot_gate)
            else:
                # C'est une porte Rz avec un certain angle
                rz_gate = Gate(Rz(term, qubit))
                circuit.append(rz_gate)
    
    return circuit

