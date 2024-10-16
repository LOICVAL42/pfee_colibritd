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
                    if node.gate.inverse() == edge[1].gate.inverse():
                        gates_to_cancel.append(edge)

            self.simplify_gates(graph, gates_to_cancel)

    def simplify_gates(self, graph: nx.DiGraph, gates_to_cancel) -> None:
        for (left, right) in gates_to_cancel:
            left_nodes = ugraph.get_previous_nodes(graph, left)
            right_nodes = ugraph.get_next_nodes(graph, right)
            graph.remove_nodes_from([left, right])
            for l in left_nodes:
                for r in right_nodes:
                    graph.add_edge(l, r)
            
