import networkx as nx
import numpy as np
from src.classes.gate import Gate
import src.utils.graphs as ugraph
from mpqp.gates import CNOT, H, Id, S
from ..patterns import Pattern
from .gate_cancellation import GateCancellationABC

class SingleQubitGateCancellation(GateCancellationABC):

    #def get_patterns():
    #    return [SingleQubitGateCancellation.commute_CNOT, SingleQubitGateCancellation.commute_CNOT_Rz_CNOT, SingleQubitGateCancellation.commute_H_CNOT_H]

    def is_required_gate(gate: Gate):
        return gate.is_single_qubit_gate()

    def is_adjoint_gate(gate, other_gate):
        return gate.is_inverse(other_gate)

    def can_commute(gate: Gate):
        return gate.is_Rz_gate()


    def get_patterns():
        return [
            SingleQubitGateCancellation.get_H_CNOT_H_pattern(),
            SingleQubitGateCancellation.get_CNOT_Rz_CNOT_pattern(),
            SingleQubitGateCancellation.get_CNOT_pattern(),
        ]

    def get_H_CNOT_H_pattern():
        first_h_gate = Gate(H(1))
        cnot = Gate(CNOT(0, 1))
        return Pattern(nx.DiGraph({
                first_h_gate: {cnot},
                cnot: {Gate(H(1))}
            }),
            first_h_gate,
            SingleQubitGateCancellation.return_next_gate)
    
    def return_next_gate(graph: nx.DiGraph, subgraph: nx.DiGraph):
        # Should be one, same target as commuting gate
        start_node = [n for n, d in subgraph.in_degree() if d == 0][0]
        end_nodes = [n for n, d in subgraph.out_degree() if d == 0]
        
        # Sole CNOT case
        if start_node == end_nodes:
            for node in end_nodes:
                if start_node.controls == node.targets:
                    # Should be only 1
                    for edge in graph.out_edges(node):
                        return edge[1]
            return None

        for node in end_nodes:
            if start_node.targets == node.targets:
                # Should be only 1
                for edge in graph.out_edges(node):
                    return edge[1]
        return None

    def get_CNOT_Rz_CNOT_pattern():
        cnot1 = Gate(CNOT(0, 1))
        rz_gate = Gate(S(1))
        rz_gate.should_be_rz = True
        cnot2 = Gate(CNOT(0, 1))
        return Pattern(nx.DiGraph({
                cnot1: {rz_gate},
                rz_gate: {cnot2}
            }),
            cnot1,
            SingleQubitGateCancellation.return_next_gate)

    def get_CNOT_pattern():
        cnot1 = Gate(CNOT(0, 1))
        return Pattern(nx.DiGraph({ cnot1: {} }),
            cnot1,
            SingleQubitGateCancellation.return_next_gate)