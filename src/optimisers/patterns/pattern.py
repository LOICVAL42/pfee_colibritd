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

    def __init__(self, pattern: nx.DiGraph, starting: Gate, completion_function: Callable, sqg_condition: Callable[[Gate], bool] = lambda _ : True):
        self.pattern = pattern
        self.starting = starting
        self.sqg_condition = sqg_condition
        self.completion_function = completion_function

    def is_pattern(self, graph: nx.DiGraph, graph_node: Gate):
        pattern_node = self.starting
        seen = []
        subgraph = nx.DiGraph()
        if self.rec_pattern(graph, pattern_node, graph_node, seen, subgraph):
            return self.completion_function(graph, subgraph)
        return None
        
    # Only doing for hadamard single qubit gate *for now*
    def rec_pattern(self, graph: nx.DiGraph, pattern_node: Gate, graph_node: Gate, seen: List[Gate], subgraph: nx.DiGraph):
        #FIXME Add inverse case
        if not self.sqg_condition(graph_node) or pattern_node.label != graph_node.label:
            return False

        subgraph.add_node(graph_node)

        # Will be used later, not needed in considered case *for now*
        seen.append(graph_node)

        #FIXME Add cnot case
        graph_edges = list(graph.out_edges(graph_node))
        pattern_edges = list(self.pattern.out_edges(pattern_node))

        # Both edges lists are empty, therefore we are done with pattern recognition
        # Or the pattern is empty and we are done
        if not any([graph_edges, pattern_edges]) or len(pattern_edges) == 0:
            return True
        
        # Graph edges are done but the pattern isn't, pattern not found
        if len(graph_edges) == 0:
            return False
        
        for e in graph_edges:
            subgraph.add_edge(*e)

        return self.rec_pattern(graph, pattern_edges[0][1], graph_edges[0][1], seen, subgraph)