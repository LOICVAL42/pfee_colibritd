import networkx as nx
import numpy as np
from src.classes.gate import Gate
import src.utils.graphs as ugraph

class CNOTGateCancellation:

    def optimise(self, graph: nx.DiGraph) -> None:
        gates_to_cancel = [None]
        # mfw no do while in python
        while len(gates_to_cancel) != 0:
            gates_to_cancel = []
            for node in graph.nodes:
                if node.label != 'CNOT' or any(node in e for e in gates_to_cancel):
                    continue
                count = 0
                to_cancel = None
                for edge in graph.out_edges(node):
                    count += 1
                    # Already adjacent
                    if node.label == 'CNOT' and node.targets == edge[1].targets and node.controls == edge[1].controls:
                        to_cancel = edge
                    else:
                        if self.commute_optimise(graph, edge, gates_to_cancel):
                            break
                
                # To avoid a case where 2 cancellable CNOTs are linked in the graph but there's a gate between their controls XOR their targets.
                if count == 1 and to_cancel != None:
                    gates_to_cancel.append((*edge, True))

            self.simplify_gates(graph, gates_to_cancel)

    def commute_optimise(self, graph: nx.DiGraph, edge, gates_to_cancel):
        patterns = [self.commute_same_target, self.commute_same_control, self.commute_H_CNOT_H]
        current_node = edge[1]
        found_gate = False
        while current_node != None:
            for pattern in patterns:
                new_node = pattern(graph, edge[0], current_node)
                if new_node != None:
                    break
            if new_node != None:
                if new_node.label == 'CNOT' and edge[0].targets == new_node.targets and edge[0].controls == new_node.controls:
                    gates_to_cancel.append((edge[0], new_node, False))
                    new_node = None
                    found_gate = True
            current_node = new_node

        return found_gate

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


    def commute_same_target(self, graph: nx.DiGraph, cnot, node):
        if node.label != 'CNOT' or cnot.targets != node.targets or cnot.controls == node.controls:
            return None
        for edge in graph.out_edges(node):
            if cnot.targets == edge[1].targets:
                return edge[1]
        return None

    def commute_same_control(self, graph: nx.DiGraph, cnot, node):
        if node.label != 'CNOT' or cnot.targets == node.targets or cnot.controls != node.controls:
            return None
        for edge in graph.out_edges(node):
            if cnot.controls == edge[1].controls:
                return edge[1]
        return None

    def commute_H_CNOT_H(self, graph: nx.DiGraph, cnot, node):
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