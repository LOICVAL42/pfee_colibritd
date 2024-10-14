import matplotlib.pyplot as plt
import networkx as nx

def plot_graph(graph: nx.DiGraph, node_size: int = 2000) -> None:
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=node_size, node_color="lightblue")
    labels = {node: str(node) for node in graph.nodes()}
    nx.draw_networkx_labels(graph, pos, labels)
    plt.show()