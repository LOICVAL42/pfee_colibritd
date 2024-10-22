def commutation_cnot_rz(equation):
    if len(equation) < 2 :
        return equation 
    j = 0
    term = equation[j]
    if (isinstance(term, str) and'⊕' in term):
        return equation
    
    new_place = 0
    cnto_dict = {}
    while (j < len(equation)):
        good = True
        term = equation[j]
                
        if (isinstance(term, str) and'⊕' in term):
            if term in cnto_dict:
                cnto_dict[term] = cnto_dict[term] + 1
            else:
                cnto_dict[term] = 1
        
        for cnot , number in cnto_dict.items():
            if number % 2 != 0:
                good = False

        j = j+1
        if (good == True and len(cnto_dict.items()) != 0):
            new_place = j

    new_equation = []
    if (new_place != 0):
        rz_swap = equation[0]
        for i in range(1,new_place):
            new_equation.append(equation[i])
        new_equation.append(rz_swap)
        for i in range(new_place,len(equation)):
            new_equation.append(equation[i])
        return new_equation
    else:    
        return equation
        
        
        
def optimize_phase_polynomial(phase_polynomial):
    optimized_phase_poly = {}

    # Parcourir chaque qubit et son équation
    for qubit, equation in phase_polynomial.items():
        swap_equation = []
        while len(equation) != 0:
            first_term =  equation[0]
            equation = commutation_cnot_rz(equation)
            if(first_term == equation[0]):
                equation.remove(first_term)
                swap_equation.append(first_term)
        
        # Assigner la version optimisée à ce qubit
        optimized_phase_poly[qubit] = swap_equation
    
    return optimized_phase_poly