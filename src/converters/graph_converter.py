import networkx as nx
from typing import List, Optional
import numpy as np
from mpqp.gates import Gate

def create_graph_from_netlist(netlist: np.ndarray[Gate]) -> nx.DiGraph:
    dag = nx.DiGraph() 
    
    # Dictionnaire pour garder une trace de la dernière porte sur chaque qubit
    last_gate_on_qubit = {}


    for gate in netlist:
        # Ajouter la porte comme un nœud dans le DAG
        dag.add_node(gate)

        # Pour chaque qubit sur lequel cette porte agit
        for qubit in gate.targets:
            # Si une autre porte a agi précédemment sur ce qubit, il y a une dépendance
            if qubit in last_gate_on_qubit:
                # Ajouter un arc entre la dernière porte sur ce qubit et la porte actuelle
                dag.add_edge(last_gate_on_qubit[qubit], gate)
        
        for qubit in gate.controls:
            # Si une autre porte a agi précédemment sur ce qubit, il y a une dépendance
            if qubit in last_gate_on_qubit:
                # Ajouter un arc entre la dernière porte sur ce qubit et la porte actuelle
                dag.add_edge(last_gate_on_qubit[qubit], gate)
            
            # Mettre à jour la dernière porte agissant sur ce qubit
            last_gate_on_qubit[qubit] = gate

    return dag