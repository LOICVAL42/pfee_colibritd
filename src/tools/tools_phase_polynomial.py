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
        raise ValueError("Invalid format for CNOT term")
    
def extract_p_number(expression):
    """
    Extracts the number from expressions like '(x1 ⊕ x0) p-1' where p-1 represents -1
    Valid range is [-1, +inf[
    
    Args:
        expression (str): The expression to analyze
        
    Returns:
        int: The extracted number (-1 for p-1, 0 for p0, 1 for p1, etc.)
        None: If no valid number is found
        
    Examples:
        >>> extract_p_number("(x1 ⊕ x0) p-1")
        -1
        >>> extract_p_number("(x1 ⊕ x0) p0")
        0
        >>> extract_p_number("(x1 ⊕ x0) p1")
        1
    """
    try:
        # Search for pattern 'p' optionally followed by '-' and digits
        pattern = r'p(-?\d+)'
        match = re.search(pattern, expression)
        
        if match:
            number = int(match.group(1))
            # Check if number is in valid range [-1, +inf[
            if number >= -1:
                return number
        return None
        
    except (AttributeError, ValueError):
        return None