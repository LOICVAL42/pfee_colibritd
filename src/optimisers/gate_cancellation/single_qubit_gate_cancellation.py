import networkx as nx
import numpy as np
from src.classes.gate import Gate
import src.utils.graphs as ugraph
from .gate_cancellation import GateCancellationABC

class SingleQubitGateCancellation(GateCancellationABC):

    def get_patterns():
        return [SingleQubitGateCancellation.commute_CNOT, SingleQubitGateCancellation.commute_CNOT_Rz_CNOT, SingleQubitGateCancellation.commute_H_CNOT_H]

    def is_required_gate(gate: Gate):
        return gate.is_single_qubit_gate()

    def is_adjoint_gate(gate, other_gate):
        return gate.is_inverse(other_gate)

    def can_commute(gate: Gate):
        return gate.is_P_gate()

    # Patterns
    def commute_H_CNOT_H(graph, gate, left):
        if not left.is_hadamard_gate() or left.targets != gate.targets:
            return None

        middle = None
        for edge in graph.out_edges(left):
            if edge[1].label != 'CNOT' or edge[1].targets != gate.targets:
                return None
            middle = edge[1]

        if middle is None:
            return None

        right = None
        # Different bc a CNOT has multiple out_edges (2)
        for edge in graph.out_edges(middle):
            if edge[1].is_hadamard_gate() and edge[1].targets == gate.targets:
                right = edge[1]

        if right == None:
            return None

        # Should be only one or less
        for edge in graph.out_edges(right):
            return edge[1]

        return None

    def commute_CNOT_Rz_CNOT(graph, gate, left):
        if left.label != 'CNOT' or left.targets != gate.targets:
            return None

        middle = None
        for edge in graph.out_edges(left):
            if edge[1].is_Rz_gate() and edge[1].targets == gate.targets:
                middle = edge[1]
                break

        if middle is None:
            return None

        right = None
        for edge in graph.out_edges(middle):
            if edge[1].label != 'CNOT' or edge[1].targets[0] not in gate.targets:
                return None
            right = edge[1]

        if right is None:
            return None

        for edge in graph.out_edges(right):
            if edge[1].targets == gate.targets:
                return edge[1]

        return None

    def commute_CNOT(graph, gate, cnot):
        if cnot.label != 'CNOT' or cnot.controls[0] not in gate.targets:
            return None

        for edge in graph.out_edges(cnot):
            if edge[1].targets[0] in gate.targets or (edge[1].controls and edge[1].controls[0] in gate.targets):
                return edge[1]

        return None

    pass