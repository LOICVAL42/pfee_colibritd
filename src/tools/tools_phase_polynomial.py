import re

def extract_control_target(term):
    """
    Extracts control and target qubits from a CNOT term in the form "x1 ⊕ x2".
    
    :param term: A string representing a CNOT gate in the form "x1 ⊕ x2".
    :return: A tuple (control, target) with the control and target qubits as integers.
    """
    match = re.search(r"x(\d+)\s⊕\s*x(\d+)", term)
    if match:
        target = int(match.group(1))
        control = int(match.group(2))
        return control, target
    else:
        raise ValueError("Format invalide pour le terme CNOT")