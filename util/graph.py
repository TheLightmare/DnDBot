
# abstract Node class
class Node():
    def __init__(self, name):
        self.name = name
        self.neighbors = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)


# abstract Edge class
class Edge():
    def __init__(self, name, node1, node2):
        self.name = name
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



    def get_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def get_edge(self, name):
        for edge in self.edges:
            if edge.name == name:
                return edge
        return None

