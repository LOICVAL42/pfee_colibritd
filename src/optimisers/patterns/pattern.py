import networkx as nx
from src.classes import Gate
from typing import Callable, List

class Pattern:
    """
    Generic pattern class

    completion_function is a function taking the found pattern in graph as subgraph in argument.
    In hadamard reduction case, it optimises the graph
    In gate_cancellation case, returns the next node to commute with or cancel with.

    sqd_condition is the condition on single qubit gates (such as Rz only for commutation patterns in sqg cancellation)
    """

    def __init__(self, pattern: nx.DiGraph, starting: Gate, completion_function: Callable, sqg_condition: Callable[[Gate], bool] = lambda _ : True, repeated_gate: Gate = None):
        self.pattern = pattern
        self.starting = starting
        self.sqg_condition = sqg_condition
        self.completion_function = completion_function
        self.repeated_gate = repeated_gate

    def is_pattern_gate(self, graph_label, pattern_label, is_inverse):
        if is_inverse and (((graph_label[-1] == '†') == pattern_label[-1] == '†') or pattern_label.replace('†', '') != graph_label.replace('†', '')):
            return False
        elif not is_inverse and pattern_label != graph_label:
            return False
        return True

    def is_pattern(self, graph: nx.DiGraph, graph_node: Gate):
        pattern_node = self.starting
        seen = []
        subgraph = nx.DiGraph()
        if self.rec_pattern(graph, pattern_node, graph_node, seen, subgraph) and len(subgraph.nodes) >= len(self.pattern.nodes):
            return self.completion_function(graph, subgraph)
        return None

    def get_next_gate(self, graph: nx.DiGraph, node:Gate, is_inwards):
        graph_edges = list(graph.out_edges(node)) if not is_inwards else list(graph.in_edges(node))
        other_node = 0 if is_inwards else 1
        for e in graph_edges:
            if e[other_node].targets == node.targets:
                return e[other_node]
        return None
        
    # Only doing for hadamard single qubit gate *for now*
    def rec_pattern(self, graph: nx.DiGraph, pattern_node: Gate, graph_node: Gate, seen: List[Gate], subgraph: nx.DiGraph, is_inwards=False, is_inverse=None, is_repeated=False):
        if graph_node in seen:
            return True

        #FIXME Add inverse case
        if not self.sqg_condition(graph_node):
            return False

        # Inverse case
        # In case of an inverse (which means the graph would be h-pdg-cnot-p-h instead of h-p-cnot-pdg-h)
        # The pattern is the reference thus never inversed. First inversed gate should always be the non dagger one.
        if graph_node.label[-1] == '†' and is_inverse is None:
            # Means both are inverse
            if pattern_node.label == graph_node.label:
                is_inverse = False
            elif pattern_node.label == graph_node.label[:-1]:
                is_inverse = True
            else:
                return False

        if not self.is_pattern_gate(graph_node.label, pattern_node.label, is_inverse):
            return False

        subgraph.add_node(graph_node)

        # Will be used later, not needed in considered case *for now*
        seen.append(graph_node)

        is_repeated = self.repeated_gate and graph_node.label.replace('†', '') == self.repeated_gate.label
        while is_repeated:
            next: Gate = self.get_next_gate(graph, graph_node, is_inwards)
            if next and self.is_pattern_gate(next.label, self.repeated_gate.label, is_inverse):
                subgraph.add_node(next)
                subgraph.add_edge(graph_node, next)
                seen.append(next)
                graph_node = next
            else:
                is_repeated = False

        other_gates = True
        if pattern_node.label == 'CNOT':
            other_gates = self.rec_explore_edges(graph, pattern_node, graph_node, seen, subgraph, not is_inwards, is_inverse, is_repeated)

        return other_gates and self.rec_explore_edges(graph, pattern_node, graph_node, seen, subgraph, is_inwards, is_inverse, is_repeated)

    def rec_explore_edges(self, graph: nx.DiGraph, pattern_node, graph_node, seen, subgraph, is_inwards, is_inverse, is_repeated):

        graph_edges = list(graph.out_edges(graph_node)) if not is_inwards else list(graph.in_edges(graph_node))
        pattern_edges = list(self.pattern.out_edges(pattern_node)) if not is_inwards else list(self.pattern.in_edges(pattern_node))

        # Both edges lists are empty, therefore we are done with pattern recognition
        # Or the pattern is empty and we are done
        if not any([graph_edges, pattern_edges]) or len(pattern_edges) == 0:
            return True
        
        # Graph edges are done but the pattern isn't, pattern not found
        if len(graph_edges) == 0:
            return False
        
        for e in graph_edges:
            subgraph.add_edge(*e)

        distant_node = 1 if not is_inwards else 0
        found_one = False
        for ge in graph_edges:
            for pe in pattern_edges:
                if pattern_node.label == 'CNOT':
                    # To refactor in a big boolean, testing all cases here
                    if pe[1 - distant_node].targets == pe[distant_node].targets and ge[1 - distant_node].targets == ge[distant_node].targets:
                        found_one = True
                        if not self.rec_pattern(graph, pe[distant_node], ge[distant_node], seen, subgraph, is_inwards, is_inverse, is_repeated):
                            return False
                    elif pe[1 - distant_node].controls == pe[distant_node].targets and ge[1 - distant_node].controls == ge[distant_node].targets:
                        found_one = True
                        if not self.rec_pattern(graph, pe[distant_node], ge[distant_node], seen, subgraph, is_inwards, is_inverse, is_repeated):
                            return False
                    elif pe[distant_node].controls is not None and ge[distant_node].controls is not None:
                        if pe[1 - distant_node].targets == pe[distant_node].controls and ge[1 - distant_node].targets == ge[distant_node].controls:
                            found_one = True
                            if not self.rec_pattern(graph, pe[distant_node], ge[distant_node], seen, subgraph, is_inwards, is_inverse, is_repeated):
                                return False
                        elif pe[1 - distant_node].controls == pe[distant_node].controls and ge[1 - distant_node].controls == ge[distant_node].controls:
                            found_one = True
                            if not self.rec_pattern(graph, pe[distant_node], ge[distant_node], seen, subgraph, is_inwards, is_inverse, is_repeated):
                                return False
                else:
                    found_one = True
                    if not self.rec_pattern(graph, pe[distant_node], ge[distant_node], seen, subgraph, is_inwards, is_inverse, is_repeated):
                        return False
            if not found_one:
                return False

        return True