from typing import List
import networkx as nx
from mpqp import QCircuit


from src.converters.netlist_converters import qCircuit_to_netlist, netlist_to_qCircuit
from src.converters.graph_converter import create_graph_from_netlist, create_netlist_from_graph
from src.converters.phase_polynomial_converter import create_phase_polynomial_from_netlist, create_netlist_from_phase_polynomial

from src.optimisers.phase_polynomial_optimizer import optimize_phase_polynomial
from src.optimisers.hadamard_gate_reduction import HadamardGateReduction
from src.optimisers import SingleQubitGateCancellation
from src.optimisers import CNOTGateCancellation

class CircuitOptimiser:

    def phase_polynomial_optimise(graph: nx.DiGraph):
        netlist = create_netlist_from_graph(graph)
        phase_poly = create_phase_polynomial_from_netlist(netlist)
        phase_poly = optimize_phase_polynomial(phase_poly)
        netlist = create_netlist_from_phase_polynomial(phase_poly)
        return create_graph_from_netlist(netlist)

    optimisers = [HadamardGateReduction.optimise, SingleQubitGateCancellation.optimise, CNOTGateCancellation.optimise, phase_polynomial_optimise]
    
    def optimise(circ: QCircuit, order: List[int] = [1, 3, 2, 3, 1, 2, 4, 3, 2]):
        netlist = qCircuit_to_netlist(circ)
        graph: nx.DiGraph = create_graph_from_netlist(netlist)
        for i in order:
            graph = CircuitOptimiser.optimisers[i - 1](graph)
            print(f"{i}: {graph.nodes}")
        return netlist_to_qCircuit(create_netlist_from_graph(graph))