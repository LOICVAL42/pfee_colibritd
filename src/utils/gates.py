from mpqp.gates import S, T

def Sdg(qubit):
    sdg = S(qubit).inverse()
    sdg.label = "S†"
    return sdg

def Tdg(qubit):
    tdg = T(qubit).inverse()
    tdg.label = "T†"
    return tdg