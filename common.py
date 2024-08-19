# common.py

import math
import time
from pysat.solvers import Glucose3

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

def get_varIndex():
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
        
# function to load graph from file in hc_set
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

def load_adjacency_list_from_alb_file(url):
    graph = {}
    with open(url) as f:
        for line in f:
            if line.startswith("p"):
                n = int(line.split()[2])
                graph = {i: [] for i in range(1, n+1)}
            else:
                u, v = map(int, line.split())
                if v not in graph[u]:
                    graph[u].append(v)
                if u not in graph[v]:
                    graph[v].append(u)
    return graph

def load_adjacency_list_from_test_set(url):
    graph = {}
    with open(url) as f:
        for line in f:
            if line.startswith("p"):
                n = int(line.split()[2])
                graph = {i: [] for i in range(1, n+1)}
            else:
                if line.startswith("e"):
                    u, v = map(int, line.split()[1:])
                else:
                    u, v = map(int, line.split())
                if v not in graph[u]:
                    graph[u].append(v)
    return graph

def init_graph_from_file(url):
    gr = load_adjacency_list_from_test_set(url)
    N = len(gr)
    graph = Graph(N)
    graph.setGraph(gr)
    return graph

def solve(cnf):
    g = Glucose3()
    g.append_formula(cnf)
    
    start = time.time()
    if g.solve():
        end = time.time()
        return g.get_model(), end-start
    else:
        end = time.time()
        return None, end-start
    
def print_result(model, N, getH):
    HCP = []
    for i in range(1, N+1):
        for j in range(1, N+1):
            if getH(i, j) in model:
                # print(i, "->", j)
                HCP.append((i, j))
                    
    print("Hamiltonian cycle:", end=" ")
    vertex = 1
    num = 1
    while True:
        print(vertex, end=" ")
        for i, j in HCP:
            if i == vertex:
                vertex = j
                break
        if vertex == 1:
            print("-> 1")
            break
        print("->", end=" ")
        num += 1
    print("Veticles of HC: ", num)
    print("Number of variables:", varIndex)

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
                
def AMO_sequential_encounter(cnf, literals):
    n = len(literals)
    S = [new_var() for i in range(n-1)]
    cnf.append([-literals[0], S[0]])
    for i in range(1, n-1):
        cnf.append([-literals[i], S[i]])
        cnf.append([-S[i-1], S[i]])
        cnf.append([-literals[i], -S[i-1]])
    cnf.append([-S[n-2], -literals[n-1]])
    
def AMO_commander(cnf, literals):
    n = len(literals)
    m = int(math.sqrt(n))
    k = n//m
    C = [new_var() for i in range(m)]
    
    AMO_binomial(cnf, C)
    
    G = [[] for i in range(m)]
    for i in range(m):
        G[i] = [literals[j] for j in range(i*k, (i+1)*k)] if i != m-1 else [literals[j] for j in range(i*k, n)]
        cnf.append([-C[i]] + G[i]) # ALO
        
        for ii in range(len(G[i])): # AMO
            for jj in range(ii+1, len(G[i])):
                cnf.append([-C[i], -G[i][ii], -G[i][jj]])
    
        for j in range(len(G[i])):
            cnf.append([C[i], -G[i][j]])
    
def AMO_product(cnf, literals):
    n = len(literals)
    p = math.ceil(math.sqrt(n))
    q = math.ceil(n/p)
    R = [new_var() for i in range(p)]
    C = [new_var() for i in range(q)]
    
    AMO_binomial(cnf, R)
    AMO_binomial(cnf, C)
    for i in range(n):
        cnf.append([-literals[i], R[i//q]])
        cnf.append([-literals[i], C[i%q]])
        
    
    
    
