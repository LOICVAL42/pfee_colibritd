import networkx as nx
import numpy as np
from src.classes.gate import Gate
import src.utils.graphs as ugraph
from .gate_cancellation import GateCancellationABC

class CNOTGateCancellation(GateCancellationABC):

    def get_patterns():
        return [CNOTGateCancellation.commute_same_target, CNOTGateCancellation.commute_same_control, CNOTGateCancellation.commute_H_CNOT_H]

    def is_required_gate(gate: Gate):
        return gate.label == 'CNOT'

    def is_adjoint_gate(gate: Gate, other_gate: Gate):
        return gate.targets == other_gate.targets and gate.controls == other_gate.controls

    def verify_count(count):
        return count == 1

    # patterns
    def commute_same_target(graph: nx.DiGraph, cnot, node):
        if node.label != 'CNOT' or cnot.targets != node.targets or cnot.controls == node.controls:
            return None
        for edge in graph.out_edges(node):
            if cnot.targets == edge[1].targets:
                return edge[1]
        return None

    def commute_same_control(graph: nx.DiGraph, cnot, node):
        if node.label != 'CNOT' or cnot.targets == node.targets or cnot.controls != node.controls:
            return None
        for edge in graph.out_edges(node):
            if cnot.controls == edge[1].controls:
                return edge[1]
        return None

    def commute_H_CNOT_H(graph: nx.DiGraph, cnot, node):
        if not node.is_hadamard_gate() or node.targets != cnot.targets:
            return None
        
        middle = None
        for edge in graph.out_edges(node):
            if edge[1].label == 'CNOT' and node.targets == edge[1].controls and cnot.controls != edge[1].targets:
                middle = edge[1]
                break

        if middle is None:
            return None

        right = None
        for edge in graph.out_edges(middle):
            if edge[1].is_hadamard_gate() and cnot.targets == edge[1].targets:
                right = edge[1]
                break

        if right is None:
            return None
        
        for edge in graph.out_edges(right):
            return edge[1]

    pass