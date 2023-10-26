
# abstract Node class
class Node():
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.neighbors = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)


# abstract Edge class
class Edge():
    def __init__(self, name, id, node1, node2):
        self.name = name
        self.id = id
        self.node1 = node1
        self.node2 = node2



# abstract Graph class
class Graph():
    def __init__(self):

        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)
        for node in self.nodes:
            if node.name == edge.node1:
                node.add_neighbor(edge.node2)
            elif node.name == edge.node2:
                node.add_neighbor(edge.node1)

    def clear(self):
        self.nodes = []
        self.edges = []

    def get_node(self, id):
        for node in self.nodes:
            if node.id == id:
                return node
        return None

    def get_edge(self, name):
        for edge in self.edges:
            if edge.name == name:
                return edge
        return None

    def get_edge_between(self, node1, node2):
        for edge in self.edges:
            if edge.node1 == node1 and edge.node2 == node2 or edge.node1 == node2 and edge.node2 == node1:
                return edge
        return None