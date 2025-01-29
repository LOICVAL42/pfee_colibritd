from ..tools.tools_phase_polynomial import extract_control_target

def commutation_cnot_rz(equation):
    """
    Optimize the position of Rz gates by commuting them through CNOT gates if possible.

    :param equation: List of terms representing a sequence of gates (e.g., Rz and CNOT).
    :return: Optimized sequence with Rz gates moved forward if they commute with an even number of CNOT gates.
    """
    # If the equation has fewer than 2 terms, return it as is
    if len(equation) < 2:
        return equation

    # Initialization
    rz_term = equation[0]
    if isinstance(rz_term, str) and '⊕' in rz_term:
        # If the first term is a CNOT, we cannot commute it
        return equation

    _, target_rz = rz_term  # Get the target qubit of the initial Rz
    cnot_count = {}  # Dictionary to count CNOT gates affecting the same target as Rz
    last_commutable_position = 0

    # Iterate through the equation to check commutativity
    for j, term in enumerate(equation[1:], start=1):
        if isinstance(term, str) and '⊕' in term:
            # Extract control and target qubits of the CNOT
            control, target = extract_control_target(term)
            if target == target_rz:
                # Count CNOTs acting on the same qubit as the Rz
                cnot_count[term] = cnot_count.get(term, 0) + 1
            # Case of a control in the CNOT Pattern
            elif control == target_rz and not all(count % 2 == 0 for count in cnot_count.values()):
                break

        # Check if all relevant CNOT gates appear an even number of times to allow commutation
        if all(count % 2 == 0 for count in cnot_count.values()) and cnot_count:
            last_commutable_position = j

    # If commutation is possible, rearrange the equation
    if last_commutable_position > 0:
        new_equation = equation[1:last_commutable_position + 1] + [rz_term] + equation[last_commutable_position + 1:]
        return new_equation

    # Otherwise, return the original equation unchanged
    return equation

def swap_phase_polynomial(equation):
    # Parcourir chaque qubit et son équation
    swap_equation = []

    while equation:
        commute_equation = commutation_cnot_rz(equation)
        if(commute_equation == equation):
            term = equation.pop(0)
            swap_equation.append(term)
        else:
            equation = commute_equation
    return swap_equation


def reduction_phase_polynomial(swap_equation):       
    reduct_equation = []
    while swap_equation:
        actual_term = swap_equation.pop(0)
        terms_to_remove = []
        
        if isinstance(actual_term, str) and '⊕' in actual_term:
            reduct_equation.append(actual_term)
        else:
            j = 0
            actual_theta, actual_target = actual_term
            all_theta = actual_theta
            
            while j < len(swap_equation):
                term = swap_equation[j]
                if isinstance(term, str) and '⊕' in term:
                    _ , target = extract_control_target(term)
                    if actual_target == target:
                        break
                    else:
                        j = j + 1
                else:
                    theta, target = term
                    if actual_target == target:
                        all_theta = all_theta + theta
                        terms_to_remove.append(term)
                    j = j + 1
                    
            if all_theta != 0:
                reduct_equation.append((all_theta, actual_target))
            
            # Supprimer les termes en commençant par la fin pour ne pas perturber les indices
            for term in reversed(terms_to_remove):
                swap_equation.remove(term)
                
    return reduct_equation
                
    

def optimize_phase_polynomial(equation):
    swap_equation = swap_phase_polynomial(equation)
    reduct_equation = reduction_phase_polynomial(swap_equation)
    return reduct_equation