import matplotlib.pyplot as plt
import networkx as nx

def plot_graph(graph: nx.DiGraph, node_size: int = 2000) -> None:
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=node_size, node_color="lightblue")
    labels = {node: str(node) for node in graph.nodes()}
    nx.draw_networkx_labels(graph, pos, labels)
    plt.show()

def get_previous_nodes(graph: nx.DiGraph, node):
    left_nodes = []
    for edge in graph.in_edges(node):
        left_nodes.append(edge[0])
    return left_nodes

def get_next_nodes(graph: nx.DiGraph, node):
    right_nodes = []
    for edge in graph.out_edges(node):
        right_nodes.append(edge[1])
    return right_nodes

def get_subgraph_adjacent_nodes(graph: nx.DiGraph, left, right):
    return (get_previous_nodes(graph, left), get_next_nodes(graph, right))

def remove_single_node(graph: nx.DiGraph, node) -> None:
    (left_nodes, right_nodes) = get_subgraph_adjacent_nodes(graph, node, node)
    graph.remove_node(node)
    for l in left_nodes:
        for r in right_nodes:
            graph.add_edge(l, r)

def remove_subgraph(graph: nx.DiGraph, left, right, inbetween = []) -> None:
    (left_nodes, right_nodes) = get_subgraph_adjacent_nodes(graph, left, right)
    graph.remove_node(left)
    graph.remove_node(right)
    for n in inbetween:
        graph.remove_node(n)
    for l in left_nodes:
        for r in right_nodes:
            graph.add_edge(l, r)