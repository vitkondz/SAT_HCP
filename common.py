# common.py

import math

########################################################################################
# Common variable
varIndex = 0
H = {}
U = {}
P = {}
HCPcnf = []

########################################################################################
# Common function
def new_var():
    global varIndex
    varIndex += 1
    return varIndex

# class Graph impliment by adjacency list
class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = {i: [] for i in range(1, self.V+1)}

    def add_edge(self, u, v):
        self.graph[u].append(v)

    def setGraph(self, graph):
        self.graph = graph
        
# function to load graph from file
def load_adjacency_list(url):
    graph = {}
    with open(url) as f:
        for line in f:
            if line.startswith("p"):
                n = int(line.split()[2])
                graph = {i: [] for i in range(1, n+1)}
            elif line.startswith("e"):
                u, v = map(int, line.split()[1:])
                if v not in graph[u]:
                    graph[u].append(v)
    return graph

def init_graph_from_file(url):
    gr = load_adjacency_list(url)
    N = len(gr)
    graph = Graph(N)
    graph.setGraph(gr)
    return graph

########################################################################################
# ALO constraint
def ALO(cnf, literals):
    cnf.append(literals)

# AMO by binomial
def AMO_binomial(cnf, literals):
    for i in range(len(literals)):
            for j in range(i+1, len(literals)):
                cnf.append([-literals[i], -literals[j]])

def AMO_binary(cnf, literals):
    if len(literals) <= 1:
        return
    
    n = len(literals)
    m = int(math.ceil(math.log(n, 2)))
    
    newBinaryVars = [new_var() for i in range(m)]
    for i in range(n):
        biStr = bin(i)[2:].zfill(m)
        for j in range(m-1, -1, -1):
            if biStr[j] == '1':
                cnf.append([-literals[i], newBinaryVars[j]])
            else:
                cnf.append([-literals[i], -newBinaryVars[j]])