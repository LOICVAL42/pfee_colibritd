import copy
import networkx as nx
from src.classes.gate import Gate
import src.utils.graphs as ugraph
from mpqp.gates import CNOT, H, Id, S
from .patterns import Pattern
import src.utils.gates as ugate

class HadamardGateReduction:

    def optimise(graph: nx.DiGraph):
        patterns = HadamardGateReduction.get_patterns()
        res = None
        found_one = True
        while found_one:
            found_one = False
            res = None
            while res is None:
                res = None
                for node in graph.nodes:
                    for p in patterns:
                        res = p.is_pattern(graph, node)
                        if res != None:
                            found_one = True
                            break

                    if res != None:
                        break
                break
        return graph


    def get_patterns():
        return [
            HadamardGateReduction.get_H_P_H_pattern(),
            HadamardGateReduction.get_HH_CNOT_HH_pattern(),
            HadamardGateReduction.get_H_P_CNOT_Pd_H(),
        ]

    """
         ┌───┐┌───┐┌───┐
    q_0: ┤ H ├┤ P ├┤ H ├
         └───┘└───┘└───┘
    """

    def get_H_P_H_pattern():
        first_h_gate = Gate(H(0))
        s_gate = Gate(S(0))
        return Pattern(nx.DiGraph({
                first_h_gate: {s_gate},
                s_gate: {Gate(H(0))}
            }),
            first_h_gate,
            HadamardGateReduction.pre_modify_H_P_H)

    def pre_modify_H_P_H(graph: nx.DiGraph, subgraph: nx.DiGraph):
        start_nodes = [n for n, d in subgraph.in_degree() if d == 0]
        end_nodes = [n for n, d in subgraph.out_degree() if d == 0]
        P = list(subgraph.out_edges(start_nodes[0]))[0][1]
        HadamardGateReduction.modify_H_P_H(graph, start_nodes[0], P, end_nodes[0])
        return True
    
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
    def get_HH_CNOT_HH_pattern():
        first_h_gate = Gate(H(0))
        cnot_gate = Gate(CNOT(0, 1))
        return Pattern(nx.DiGraph({
            first_h_gate: {cnot_gate},
            Gate(H(1)): {cnot_gate},
            cnot_gate: {Gate(H(0)), Gate(H(1))}
        }), first_h_gate, HadamardGateReduction.pre_modify_HH_CNOT_HH)

    def pre_modify_HH_CNOT_HH(graph: nx.DiGraph, subgraph: nx.DiGraph):
        start_nodes = [n for n, d in subgraph.in_degree() if d == 0]
        end_nodes = [n for n, d in subgraph.out_degree() if d == 0]
        cnot = list(subgraph.out_edges(start_nodes[0]))[0][1]
        HadamardGateReduction.modify_HH_CNOT_HH(graph, start_nodes, cnot, end_nodes)
        return True

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
    def get_H_P_CNOT_Pd_H():
        first_h_gate = Gate(H(1))
        p_gate = Gate(S(1))
        cnot = Gate(CNOT(0, 1))
        p_dagger = Gate(ugate.Sdg(1))
        # FIXME handle infite amount of CNOTs between
        return Pattern(nx.DiGraph({
            first_h_gate: {p_gate},
            p_gate: {cnot},
            cnot: {p_dagger},
            p_dagger: {Gate(H(1))}
        }), first_h_gate, HadamardGateReduction.pre_modify_H_P_CNOT_Pd_H, repeated_gate=cnot)

    def pre_modify_H_P_CNOT_Pd_H(graph: nx.DiGraph, subgraph: nx.DiGraph):
        start_node = [n for n, d in subgraph.in_degree() if d == 0][0]
        second_start_node = list(subgraph.out_edges(start_node))[0][1]

        end_node = [n for n, d in subgraph.out_degree() if d == 0][0]
        second_end_node = list(subgraph.in_edges(end_node))[0][0]
        cnots = [n for n in subgraph.nodes if n.label == 'CNOT']
        HadamardGateReduction.modify_H_P_CNOT_Pd_H(graph, [start_node, second_start_node], cnots, [second_end_node, end_node])
        return True
            
    def modify_H_P_CNOT_Pd_H(graph: nx.Graph, left_gates, middle_gates, right_gates):
        (left_nodes, right_nodes) = ugraph.get_subgraph_adjacent_nodes(graph, left_gates[0], right_gates[1])

        graph.remove_nodes_from(left_gates + right_gates)
        for node in left_nodes:
            graph.add_edge(node, right_gates[0])
        for node in right_nodes:
            graph.add_edge(left_gates[1], node)

        graph.add_edge(right_gates[0], middle_gates[0])
        graph.add_edge(middle_gates[-1], left_gates[1])