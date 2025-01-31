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

    def add_previous(netlist, subgraph, seen, qubit, i):
        for j in range(i, -1, -1):
            gate: Gate = netlist[j]
            if gate.label == "CNOT" or not (gate.is_Rz_gate() or gate.label == "X"):
                break
            if gate.targets[0] != qubit:
                continue
            subgraph.append(gate)
            seen.append(gate)

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
                            other_gate.phase_index = j
                            sg.insert(indexes[qubit_index] - 1, other_gate)
                            seen.append(other_gate)
                            qubits.append(other_gate.targets[0])
                            indexes.append(j)
                        elif other_gate.targets[0] == qubit:
                            other_gate.phase_index = j
                            sg.insert(indexes[qubit_index] - 1, other_gate)
                            seen.append(other_gate)
                    elif other_gate.targets[0] != qubit:
                        continue
                    elif not (other_gate.is_Rz_gate() or other_gate.label == "X"):
                        break
                    else:
                        gate.phase_index = j
                        sg.insert(indexes[qubit_index] - 1, other_gate)
                        seen.append(other_gate)
                
                for j in range(indexes[qubit_index]+1, len(netlist), 1):
                    other_gate: Gate = netlist[j]
                    if other_gate in seen:
                        continue
                    if other_gate.label == "CNOT":
                        if other_gate.controls[0] == qubit and (not other_gate.targets[0] in qubits):
                            other_gate.phase_index = j
                            sg.append(other_gate)
                            seen.append(other_gate)
                            qubits.append(other_gate.targets[0])
                            indexes.append(j)
                        elif other_gate.targets[0] == qubit:
                            other_gate.phase_index = j
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
        i = {}
        last_beg = 0
        for sg in subgraphs:
            sg_opti = CircuitOptimiser.phase_polynomial_optimise(sg)
            gate: Gate = None
            last_phase_index_on_qubit = {}
            for k in range(last_beg, sg[0].phase_index):
                g = netlist[k]
                if not g.label in ["CNOT", "X", "X†"] and not g.is_Rz_gate():
                    new_netlist.append(g)
                    i[g.targets[0]] = k + 1

            for gate in sg_opti:
                if gate.label == "CNOT":
                    # If phase_index is -1, it means that it is NOT in a subgraph. Also, every CNOT is in a subgraph
                    i_qubit = i.get(gate.targets[0])
                    if not i_qubit:
                        i[gate.targets[0]] = 0
                    #new_netlist += [g for g in netlist[i[gate.targets[0]]:gate.phase_index] if not g.label in ["CNOT", "X", "X†"] and g.targets[0] == gate.targets[0] and not g.is_Rz_gate()]
                    added = False
                    for j in range(len(new_netlist)):
                        g2: Gate = new_netlist[j]
                        if g2.label == "CNOT" and g2.phase_index > gate.phase_index:
                            added = True
                            to_add = [g for g in netlist[i[gate.targets[0]]:gate.phase_index] if not g.label in ["CNOT", "X", "X†"] and g.targets[0] == gate.targets[0] and not g.is_Rz_gate()]
                            nb_added = len(to_add)
                            for k in range(nb_added):
                                new_netlist.insert(j + k, to_add[k])
                            new_netlist.insert(j + nb_added, gate)
                            last_phase_index_on_qubit[gate.targets[0]] = j + nb_added
                            break
                    if not added:
                        new_netlist += [g for g in netlist[i[gate.targets[0]]:gate.phase_index] if not g.label in ["CNOT", "X", "X†"] and g.targets[0] == gate.targets[0] and not g.is_Rz_gate()]
                        last_phase_index_on_qubit[gate.targets[0]] = len(new_netlist)
                        new_netlist.append(gate)
                    i[gate.targets[0]] = gate.phase_index
                else:
                    last = last_phase_index_on_qubit.get(gate.targets[0])
                    if last:
                        new_netlist.insert(last + 1, gate)
                        for key in last_phase_index_on_qubit.keys():
                            if (last_phase_index_on_qubit[key] >= last + 1):
                                last_phase_index_on_qubit[key] += 1

                    else:
                        new_netlist.append(gate)
            
            last_beg = max(i.values()) + 1
        for key in i.keys():
            new_netlist += [g for g in netlist[i[key]:] if not g.label in ["CNOT", "X", "X†"] and g.targets[0] == key and not g.is_Rz_gate()]
        return new_netlist
    
    optimisers = [HadamardGateReduction.optimise, SingleQubitGateCancellation.optimise, CNOTGateCancellation.optimise, optimise_subgraphs]

    def optimise(circ: QCircuit, order: List[int] = [1, 3, 2, 3, 1, 2, 4, 3, 2]):
        netlist = qCircuit_to_netlist(circ)
        graph: nx.DiGraph = create_graph_from_netlist(netlist)
        for i in order:
            graph = CircuitOptimiser.optimisers[i - 1](graph)
            print(f"{i}: {graph.nodes}")
        return netlist_to_qCircuit(create_netlist_from_graph(graph))