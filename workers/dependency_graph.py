import networkx as nx
import pickle
from tree_sitter import Node

# Global directed graph
graph = nx.DiGraph()

GRAPH_FILE = "/app/cache/dependency_graph.pkl"


def save_graph():
    with open(GRAPH_FILE, "wb") as f:
        pickle.dump(graph, f)


def load_graph():
    global graph
    try:
        with open(GRAPH_FILE, "rb") as f:
            graph = pickle.load(f)
    except Exception:
        pass

def update_graph(method_signature: str,
                 method_code: str = None,
                 tree=None,
                 **kwargs):
    """
    Updates dependency graph with method relationships.

    Accepts:
        method_signature (required)
        method_code (optional)
        tree (optional)
    """

    if not method_signature:
        return

    # Add method node
    graph.add_node(method_signature)

    # If no tree provided, only register node
    if tree is None:
        save_graph()
        return

    def traverse(node: Node):
        if node.type == "method_invocation":
            called_method = node.child_by_field_name("name")
            if called_method:
                called_name = called_method.text.decode("utf-8")
                graph.add_edge(method_signature, called_name)

        for child in node.children:
            traverse(child)

    traverse(tree.root_node)
    save_graph()

def get_graph():
    """
    Returns the current dependency graph.
    """
    return graph


def get_neighbors(method_signature: str):
    """
    Returns methods called by this method.
    """
    if method_signature in graph:
        return list(graph.successors(method_signature))
    return []