import copy
import networkx as nx
from src.classes.gate import Gate
import src.utils.graphs as ugraph
from mpqp.gates import CNOT, Id

class HadamardGateReduction:

    def optimise(graph: nx.DiGraph) -> None:
        cnot_patterns = [HadamardGateReduction.detect_HH_CNOT_HH]
        h_patterns = [HadamardGateReduction.detect_H_P_H, HadamardGateReduction.detect_H_P_CNOT_Pd_H]
        while True:
            args = None
            func = None
            for node in graph.nodes:
                if node.label == 'CNOT':
                    for pattern in cnot_patterns:
                        (args, func) = pattern(graph, node)
                        if args != None:
                            break
                elif node.label == 'H':
                    for pattern in h_patterns:
                        (args, func) = pattern(graph, node)
                        if args != None:
                            break

                if args != None:
                    break

            if func is not None:
                func(graph, *args)
                continue
            break

    """
         ┌───┐┌───┐┌───┐
    q_0: ┤ H ├┤ P ├┤ H ├
         └───┘└───┘└───┘
    """
    def detect_H_P_H(graph, node):
        for edge in graph.out_edges(node):
            if not edge[1].is_single_qubit_gate() or not edge[1].is_phase_gate():
                # Not a single qubit gate
                return (None, None)
            for edge2 in graph.out_edges(edge[1]):
                if edge2[1].label == 'H':
                    return ((node, edge[1], edge2[1]), HadamardGateReduction.modify_H_P_H)
        return (None, None)
    
    def modify_H_P_H(graph: nx.DiGraph, left, P, right):
        (left_nodes, right_nodes) = ugraph.get_subgraph_adjacent_nodes(graph, left, right)
        graph.remove_nodes_from([left, P, right])
        p_dagger = P.create_inverse()

        # Beware, may need to copy
        new_left = p_dagger
        new_right = copy.copy(p_dagger)

        for node in left_nodes:
            graph.add_edge(node, new_left)

        # The left Hadamard gate becomes the middle Hadamard Gate
        graph.add_edge(new_left, left)
        graph.add_edge(left, new_right)

        for node in right_nodes:
            graph.add_edge(new_right, node)

    """
         ┌───┐     ┌───┐
    q_0: ┤ H ├──■──┤ H ├
         ├───┤┌─┴─┐├───┤
    q_1: ┤ H ├┤ X ├┤ H ├
         └───┘└───┘└───┘
    """
    def detect_HH_CNOT_HH(graph: nx.DiGraph, middle):
        left_gates = []
        for edge in graph.in_edges(middle):
            if edge[0].label != 'H':
                return (None, None)
            left_gates.append(edge[0])
        
        right_gates = []
        for edge in graph.out_edges(middle):
            if edge[1].label != 'H':
                return (None, None)
            right_gates.append(edge[1])
        
        if len(left_gates) != 2 or len(right_gates) != 2:
            return (None, None)

        return ((left_gates, middle, right_gates), HadamardGateReduction.modify_HH_CNOT_HH)

    def modify_HH_CNOT_HH(graph: nx.DiGraph, left_gates, middle, right_gates):
        left_nodes = ugraph.get_previous_nodes(graph, left_gates[0]) + ugraph.get_previous_nodes(graph, left_gates[1])
        right_nodes = ugraph.get_next_nodes(graph, right_gates[0]) + ugraph.get_next_nodes(graph, right_gates[1])

        graph.remove_nodes_from(left_gates + right_gates + [middle])
        
        # Otherwise it is a faulty CNOT
        assert len(middle.targets) == 1
        assert len(middle.controls) == 1

        new_gate = Gate(CNOT(*middle.targets, *middle.controls))
        graph.add_node(new_gate)
        for left in left_nodes:
            graph.add_edge(left, new_gate)
        for right in right_nodes:
            graph.add_edge(new_gate, right)

    """
    q_0: ────────────■────────────
         ┌───┐┌───┐┌─┴─┐┌───┐┌───┐
    q_1: ┤ H ├┤ P ├┤ X ├┤ P†├┤ H ├
         └───┘└───┘└───┘└───┘└───┘
    """
    def detect_H_P_CNOT_Pd_H(graph: nx.Graph, left: Gate) -> None:
        left_gates = [left]
        # There should be only one, need to redo graphs
        for edge in graph.out_edges(left):
            if edge[1].is_phase_gate():
                left_gates.append(edge[1])

        if len(left_gates) != 2:
            return (None, None)

        target = left.targets[0]
        pd_gate = None
        leftest_gate = left_gates[1]
        is_there_still_cnots = True
        middle_gates = []
        # problem
        while is_there_still_cnots:
            is_there_still_cnots = False
            for edge in graph.out_edges(leftest_gate):
                if edge[1].label == 'CNOT' and edge[1].targets[0] == target:
                    leftest_gate = edge[1]
                    middle_gates.append(leftest_gate)
                    is_there_still_cnots = True
                    break
                elif edge[1].is_phase_gate() and edge[1].targets[0] == target:
                    pd_gate = edge[1]
                    break
                elif edge[1].is_single_qubit_gate() and edge[1].targets[0] == target:
                    return (None, None)
        
        if len(middle_gates) == 0 or pd_gate is None or not left_gates[1].is_inverse(pd_gate):
            return (None, None)

        right_gates = [pd_gate]        
        for edge in graph.out_edges(pd_gate):
            if edge[1].label == 'H':
                right_gates.append(edge[1])

        if len(right_gates) != 2:
            return (None, None)

        return ((left_gates, middle_gates, right_gates), HadamardGateReduction.modify_H_P_CNOT_Pd_H)
            
    def modify_H_P_CNOT_Pd_H(graph: nx.Graph, left_gates, middle_gates, right_gates):
        (left_nodes, right_nodes) = ugraph.get_subgraph_adjacent_nodes(graph, left_gates[0], right_gates[1])

        graph.remove_nodes_from(left_gates + right_gates)
        for node in left_nodes:
            graph.add_edge(node, right_gates[0])
        for node in right_nodes:
            graph.add_edge(left_gates[1], node)

        graph.add_edge(right_gates[0], middle_gates[0])
        graph.add_edge(middle_gates[-1], left_gates[1])