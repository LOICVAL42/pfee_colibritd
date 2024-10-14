import networkx as nx

class Hadamard_gate_reduction:

    def optimise(netgraph: nx.DiGraph) -> None:
        for node in netgraph.nodes:
            print(node)