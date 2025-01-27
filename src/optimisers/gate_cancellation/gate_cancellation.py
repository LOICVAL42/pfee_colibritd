from abc import ABC, abstractmethod
import networkx as nx
import src.utils.graphs as ugraph
from src.classes.gate import Gate

class GateCancellationABC(ABC):

    @abstractmethod
    def get_patterns():
        pass

    @classmethod
    def optimise(cls, graph: nx.DiGraph) -> None:
        gates_to_cancel = [None]
        # mfw no do while in python
        while len(gates_to_cancel) != 0:
            gates_to_cancel = []
            for node in graph.nodes:
                if not cls.is_required_gate(node) or any(node in e for e in gates_to_cancel):
                    continue
                count = 0
                to_cancel = False
                for edge in graph.out_edges(node):
                    count += 1
                    # Already adjacent
                    if cls.is_required_gate(edge[1]) and cls.is_adjoint_gate(node, edge[1]):
                        to_cancel = True
                    elif cls.can_commute(edge[0]):
                        if cls.commute_optimise(graph, edge, gates_to_cancel):
                            break
                
                # To avoid a case where 2 cancellable CNOTs are linked in the graph but there's a gate between their controls XOR their targets.
                if cls.verify_count(count) and to_cancel:
                    gates_to_cancel.append((*edge, True))

            cls.simplify_gates(graph, gates_to_cancel)
        return graph
    
    @classmethod
    def commute_optimise(cls, graph: nx.DiGraph, edge, gates_to_cancel):
        patterns = cls.get_patterns()
        current_node = edge[1]
        found_gate = False
        while current_node != None:
            for pattern in patterns:
                # A pattern takes as argument the commuted gate and the one it is being verified to commute with
                new_node = pattern(graph, edge[0], current_node)
                if new_node != None:
                    break
            if new_node != None:
                if cls.is_required_gate(new_node) and cls.is_adjoint_gate(edge[0], new_node):
                    gates_to_cancel.append((edge[0], new_node, False))
                    new_node = None
                    found_gate = True
            current_node = new_node

        return found_gate

    def simplify_gates(graph: nx.DiGraph, gates_to_cancel) -> None:
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

    @abstractmethod
    def is_required_gate(gate: Gate):
        pass

    @abstractmethod
    def is_adjoint_gate(gate: Gate, other_gate: Gate):
        pass

    @abstractmethod
    def verify_count(count):
        return True

    @abstractmethod
    def can_commute(gate: Gate):
        return True