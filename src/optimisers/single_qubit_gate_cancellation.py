import networkx as nx
import numpy as np
from src.classes.gate import Gate
import src.utils.graphs as ugraph

class Single_qubit_gate_cancellation:

    # primitive version, does *NOT* apply commutative rules
    def optimise(self, graph: nx.DiGraph) -> None:
        gates_to_cancel = [None]
        # mfw no do while in python
        while len(gates_to_cancel) != 0:
            gates_to_cancel = []
            for node in graph.nodes:
                if not node.is_single_qubit_gate() or any(node in e for e in gates_to_cancel):
                    continue
                # As it's a single qubit gate, there should be only one
                for edge in graph.out_edges(node):
                    if edge[1].is_single_qubit_gate() and node.is_inverse(edge[1]):
                        gates_to_cancel.append((*edge, True))
                    elif edge[0].is_Rz_gate():
                        self.commute_optimise(graph, edge, edge[0].targets, gates_to_cancel)

            self.simplify_gates(graph, gates_to_cancel)

    def commute_optimise(self, graph: nx.DiGraph, edge, targets, gates_to_cancel):
        patterns = [self.commute_CNOT, self.commute_CNOT_Rz_CNOT, self.commute_H_CNOT_H]
        current_node = edge[1]
        while current_node != None:
            for pattern in patterns:
                new_node = pattern(graph, current_node, targets)
                if new_node != None:
                    break
            if new_node != None:
                if new_node.is_single_qubit_gate() and edge[0].is_inverse(new_node):
                    gates_to_cancel.append((edge[0], new_node, False))
                    new_node = None
            current_node = new_node


    def simplify_gates(self, graph: nx.DiGraph, gates_to_cancel) -> None:
        for (left, right, is_adjacent) in gates_to_cancel:
            if is_adjacent:
                left_nodes = ugraph.get_previous_nodes(graph, left)
                right_nodes = ugraph.get_next_nodes(graph, right)
                graph.remove_nodes_from([left, right])
                for l in left_nodes:
                    for r in right_nodes:
                        graph.add_edge(l, r)
            else:
                ugraph.remove_single_node(graph, left)
                ugraph.remove_single_node(graph, right)


    def commute_H_CNOT_H(self, graph, left, targets):
        if not left.is_hadamard_gate() or left.targets != targets:
            return None

        middle = None
        for edge in graph.out_edges(left):
            if edge[1].label != 'CNOT' or edge[1].targets != targets:
                return None
            middle = edge[1]

        if middle is None:
            return None

        right = None
        # Different bc a CNOT has multiple out_edges (2)
        for edge in graph.out_edges(middle):
            if edge[1].is_hadamard_gate() and edge[1].targets == targets:
                right = edge[1]

        if right == None:
            return None

        # Should be only one or less
        for edge in graph.out_edges(right):
            return edge[1]

        return None

    def commute_CNOT_Rz_CNOT(self, graph, left, targets):
        if left.label != 'CNOT' or left.targets != targets:
            return None

        middle = None
        for edge in graph.out_edges(left):
            if edge[1].is_Rz_gate() and edge[1].targets == targets:
                middle = edge[1]
                break

        if middle is None:
            return None

        right = None
        for edge in graph.out_edges(middle):
            if edge[1].label != 'CNOT' or edge[1].targets[0] not in targets:
                return None
            right = edge[1]

        if right is None:
            return None

        for edge in graph.out_edges(right):
            if edge[1].targets == targets:
                return edge[1]

        return None

    def commute_CNOT(self, graph, cnot, targets):
        if cnot.label != 'CNOT' or cnot.controls[0] not in targets:
            return None

        for edge in graph.out_edges(cnot):
            if edge[1].targets[0] in targets or edge[1].controls[0] in targets:
                return edge[1]

        return None