from typing import List
import networkx as nx
from mpqp import QCircuit

from src.classes.gate import Gate

from src.converters.netlist_converters import qCircuit_to_netlist, netlist_to_qCircuit
from src.converters.graph_converter import create_graph_from_netlist, create_netlist_from_graph
from src.converters.phase_polynomial_converter import create_phase_polynomial_from_netlist, create_netlist_from_phase_polynomial

from src.optimisers.phase_polynomial_optimizer import optimize_phase_polynomial
from src.optimisers.hadamard_gate_reduction import HadamardGateReduction
from src.optimisers import SingleQubitGateCancellation
from src.optimisers import CNOTGateCancellation

class CircuitOptimiser:

    def phase_polynomial_optimise(netlist):
        phase_poly = create_phase_polynomial_from_netlist(netlist)
        phase_poly = optimize_phase_polynomial(phase_poly)
        return create_netlist_from_phase_polynomial(phase_poly)

    def split_graph(netlist):
        seen = []
        subgraphs = []
        for i in range(len(netlist)):
            gate: Gate = netlist[i]
            if gate in seen:
                continue
            if gate.label != "CNOT":
                continue
            # current subgraph
            gate.phase_index = i
            sg = [gate]
            seen.append(gate)
            qubits = [gate.targets[0], gate.controls[0]]
            indexes = [i, i]
            qubit_index = 0
            while qubit_index < len(qubits):
                qubit = qubits[qubit_index]
                for j in range(indexes[qubit_index]-1, -1, -1):
                    other_gate: Gate = netlist[j]
                    if other_gate in seen:
                        continue
                    if other_gate.label == "CNOT":
                        if other_gate.controls[0] == qubit and (not other_gate.targets[0] in qubits):
                            gate.phase_index = j
                            sg.append(other_gate)
                            seen.append(other_gate)
                            qubits.append(other_gate.targets[0])
                            indexes.append(j)
                        elif other_gate.targets[0] == qubit:
                            gate.phase_index = j
                            sg.append(other_gate)
                            seen.append(other_gate)
                    elif other_gate.targets[0] != qubit:
                        continue
                    elif not (other_gate.is_Rz_gate() or other_gate.label == "X"):
                        break
                    else:
                        gate.phase_index = j
                        sg.append(other_gate)
                        seen.append(other_gate)
                
                for j in range(indexes[qubit_index]+1, len(netlist), 1):
                    other_gate: Gate = netlist[j]
                    if other_gate in seen:
                        continue
                    if other_gate.label == "CNOT":
                        if other_gate.controls[0] == qubit and (not other_gate.targets[0] in qubits):
                            gate.phase_index = j
                            sg.append(other_gate)
                            seen.append(other_gate)
                            qubits.append(other_gate.targets[0])
                            indexes.append(j)
                        elif other_gate.targets[0] == qubit:
                            gate.phase_index = j
                            sg.append(other_gate)
                            seen.append(other_gate)
                    elif other_gate.targets[0] != qubit:
                        continue
                    elif not (other_gate.is_Rz_gate() or other_gate.label == "X"):
                        break
                    else:
                        gate.phase_index = j
                        sg.append(other_gate)
                        seen.append(other_gate)
                qubit_index += 1
            subgraphs.append(sg)
        
        ## To remove
        #print(subgraphs)
        #for i in range(len(subgraphs)):
        #    sg = subgraphs[i]
        #    for j in range(len(sg)):
        #       gate = sg[j]
        #       gate.label += f"-{i}"
        #       gate.gate.label += f"-{i}"
        
        return subgraphs

    def optimise_subgraphs(netlist):
        subgraphs = CircuitOptimiser.split_graph(netlist)
        new_netlist = []
        i = 0
        for sg in subgraphs:
            print(sg)
            sg_opti = CircuitOptimiser.phase_polynomial_optimise(sg)
            gate: Gate = None
            for gate in sg_opti:
                if gate.label == "CNOT":
                    # If phase_index is -1, it means that it is NOT in a subgraph. Also, every CNOT is in a subgraph
                    new_netlist += [g for g in netlist[i:gate.phase_index] if g.label != "CNOT" and g.phase_index != -1]
                    i = gate.phase_index
                    added = False
                    for j in range(len(new_netlist)):
                        g2: Gate = new_netlist[j]
                        if g2.label == "CNOT" and g2.phase_index > gate.phase_index:
                            added = True
                            new_netlist.insert(j, gate)
                            break
                    if not added:
                        new_netlist.append(gate)
                else:
                    added = False
                    for j in range(len(new_netlist)):
                        g2: Gate = new_netlist[j]
                        if g2.label == "CNOT" and g2.phase_index > gate.phase_index:
                            added = True
                            new_netlist.insert(j, gate)
                            break
                    if not added:
                        new_netlist.append(gate)
        new_netlist += [g for g in netlist[i:] if g.label != "CNOT" and g.phase_index != -1]
        return new_netlist
    
    optimisers = [HadamardGateReduction.optimise, SingleQubitGateCancellation.optimise, CNOTGateCancellation.optimise, optimise_subgraphs]

    def optimise(circ: QCircuit, order: List[int] = [1, 3, 2, 3, 1, 2, 4, 3, 2]):
        netlist = qCircuit_to_netlist(circ)
        graph: nx.DiGraph = create_graph_from_netlist(netlist)
        for i in order:
            graph = CircuitOptimiser.optimisers[i - 1](graph)
            print(f"{i}: {graph.nodes}")
        return netlist_to_qCircuit(create_netlist_from_graph(graph))