from pysat.solvers import Glucose3
import math

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
def load_graph(url):
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
    
# function to generate new variables
def new_var():
    global varIndex
    varIndex += 1
    return varIndex

# function to get variable for H and P
def getH(i, j):
    global H
    if (i, j) not in H:
        H[(i, j)] = new_var()
    return H[(i, j)]

def getP(i, bit):
    global P
    if (i, bit) not in P:
        P[(i, bit)] = new_var()
    return P[(i, bit)]

# AMO, ALO, EO constraints
def at_least_one(cnf, literals):
    cnf.append(literals)
    
def at_most_one(cnf, literals):
    for i in range(len(literals)):
        for j in range(i+1, len(literals)):
            cnf.append([-literals[i], -literals[j]])
            
def exactly_one(cnf, literals):
    at_least_one(cnf, literals)
    at_most_one(cnf, literals)
    
# add variables with default value to the cnf
def add_default_variables(cnf, n, m, graph):
    # Hij = 0 if the arc (i, j) is not in the graph
    for i in range(1, n+1):
        for j in range(1, n+1):
            if j not in graph.graph[i]:
                cnf.append([-getH(i, j)])
    # P1 = 1 (00..01)
    for bit in range(m):
        if bit == 0:
            cnf.append([getP(1, bit)])
        else:
            cnf.append([-getP(1, bit)])

# each vertex has exactly one outgoing arc - constraints (1)
def vertex_outgoing_arcs(cnf, n):
    for i in range(1, n+1):
        literals = []
        for j in range(1, n+1):
            literals.append(getH(i, j))
        exactly_one(cnf, literals)
    
# each vertex has exactly one incoming arc - constraints (2)
def vertex_incoming_arcs(cnf, n):
    for j in range(1, n+1):
        literals = []
        for i in range(1, n+1):
            literals.append(getH(i, j))
        exactly_one(cnf, literals)
        
# H1i -> Pi = 2 (00..10) - constraints (3")
def vertex_start(cnf, n, m):
    for i in range(2, n+1):
        for bit in range(m):
            if bit == 1: 
                cnf.append([-getH(1, i), getP(i, bit)])
            else:
                cnf.append([-getH(1, i), -getP(i, bit)])
        
# Hi1 -> Pi = n - constraints (4")
def vertex_end(cnf, n, m):
    binaryN = bin(n)[2:][::-1]
    for i in range(2, n+1):
        for bit in range(m):
            if binaryN[bit] == '1':
                cnf.append([-getH(i, 1), getP(i, bit)])
            else:
                cnf.append([-getH(i, 1), -getP(i, bit)])
            
# Hij -> Pj = Pi + 1 - constraints (5")
def vertex_positions(cnf, n, m):
    for i in range(2, n+1):
        for j in range(2, n+1):
            for bit in range(m):
                if bit == 0: # y0 = -x0
                    cnf.append([-getH(i, j), getP(i, bit), getP(j, bit)])
                    cnf.append([-getH(i, j), -getP(i, bit), -getP(j, bit)])
                elif bit == 1: # x0 -> y1 = -x1 and -x0 -> y1 = x1
                    cnf.append([-getH(i, j), -getP(i, 0), getP(i, 1), getP(j, 1)])
                    cnf.append([-getH(i, j), -getP(i, 0), -getP(i, 1), -getP(j, 1)])
                    cnf.append([-getH(i, j), getP(i, 0), getP(i, 1), -getP(j, 1)])
                    cnf.append([-getH(i, j), getP(i, 0), -getP(i, 1), getP(j, 1)])
                    
            # version 1 - one-bit incrementor
                # else:
                #     #carry = 1, -Yi-1 ^ Xi-1 -> Yi = -Xi
                #     cnf.append([-getH(i, j), getP(j, bit-1), -getP(i, bit-1), getP(j, bit), getP(i, bit)])
                #     cnf.append([-getH(i, j), getP(j, bit-1), -getP(i, bit-1), -getP(j, bit), -getP(i, bit)])
                #     # carry = 0, -Yi-1 ^ -Xi-1 -> Yi = Xi
                #     cnf.append([-getH(i, j), -getP(j, bit-1), getP(i, bit-1), getP(j, bit), -getP(i, bit)])
                #     cnf.append([-getH(i, j), -getP(j, bit-1), getP(i, bit-1), -getP(j, bit), getP(i, bit)])
                #     # carry = 0, Yi-1 -> Yi = Xi
                #     cnf.append([-getH(i, j), -getP(j, bit-1), getP(j, bit), -getP(i, bit)])
                #     cnf.append([-getH(i, j), -getP(j, bit-1), -getP(j, bit), getP(i, bit)])
                    
            # version 2 - 4-bits incrementor
            for bit in range(7, m+1, 4):
                cnf.append([-getH(i, j), getP(i, bit-1), getP(i, bit-4), -getP(j, bit-1)])      #1
                cnf.append([-getH(i, j), getP(i, bit-1), -getP(j, bit-1), -getP(j, bit-2)])     #2
                cnf.append([-getH(i, j), getP(i, bit-1), -getP(j, bit-1), -getP(j, bit-3)])     #3
                cnf.append([-getH(i, j), getP(i, bit-1), -getP(j, bit-1), -getP(j, bit-4)])     #4
                cnf.append([-getH(i, j), getP(i, bit-3), -getP(j, bit-3), -getP(j, bit-4)])     #5
                cnf.append([-getH(i, j), -getP(i, bit-4), -getP(j, bit-5), getP(j, bit-4)])     #6
                cnf.append([-getH(i, j), getP(i, bit-2), -getP(i, bit-3), getP(j, bit-2), getP(j, bit-3)])
                cnf.append([-getH(i, j), getP(i, bit-4), getP(i, bit-5), -getP(j, bit-4)])      #8
                cnf.append([-getH(i, j), -getP(i, bit-1), getP(j, bit-1)])                      #9
                cnf.append([-getH(i, j), -getP(i, bit-2), -getP(i, bit-3), -getP(j, bit-2), getP(j, bit-3)])
                cnf.append([-getH(i, j), -getP(i, bit-3), -getP(i, bit-4), -getP(i, bit-5), getP(j, bit-5), -getP(j, bit-3)])
                cnf.append([-getH(i, j), getP(i, bit-2), getP(i, bit-4), -getP(j, bit-2)])      #12
                cnf.append([-getH(i, j), getP(i, bit-3), getP(i, bit-4), -getP(j, bit-3)])      #13
                cnf.append([-getH(i, j), getP(i, bit-2), -getP(j, bit-2), -getP(j, bit-3)])     #14
                cnf.append([-getH(i, j), getP(i, bit-2), -getP(j, bit-2), -getP(j, bit-4)])     #15
                cnf.append([-getH(i, j), -getP(i, bit-4), getP(i, bit-5), getP(j, bit-4)])      #16
                cnf.append([-getH(i, j), getP(i, bit-1), -getP(i, bit-2), getP(j, bit-1), getP(j, bit-2)])
                cnf.append([-getH(i, j), getP(i, bit-4), -getP(i, bit-5), getP(j, bit-5), getP(j, bit-4)])
                cnf.append([-getH(i, j), getP(i, bit-4), -getP(j, bit-5), -getP(j, bit-4)])     #19
                cnf.append([-getH(i, j), -getP(i, bit-1), -getP(i, bit-2), -getP(j, bit-1), getP(j, bit-2)])
                cnf.append([-getH(i, j), getP(i, bit-3), -getP(i, bit-4), -getP(i, bit-5), getP(j, bit-5), getP(j, bit-3)])
                


                
                    
if __name__ == '__main__':
    
    # example   
    # gr = {1: [2], 2: [1, 4], 3: [1, 4], 4: [3]}
    # gr = {1: [2, 4], 2: [1, 3, 4, 5], 3: [2, 5], 4: [1, 2, 5], 5: [2, 3, 4]}
    # gr = {1: [2, 4], 2: [1, 3, 4, 5], 3: [2, 5], 4: [1, 2], 5: [2, 3]}
    gr = load_graph("graphs/hc-15.col")
    
    N = len(gr)
    
    # initialize
    graph = Graph(N)
    graph.setGraph(gr)
    
    varIndex = 0
    m = math.ceil(math.log2(N)) if math.log2(N) != int(math.log2(N)) else int(math.log2(N)) + 1
    H = {}
    P = {}
    HCPcnf = []
        
    # HCP binary adder encoding constraints
    add_default_variables(HCPcnf, N, m, graph)      # default variables
    vertex_outgoing_arcs(HCPcnf, N)                 # constraints (1)
    vertex_incoming_arcs(HCPcnf, N)                 # constraints (2)
    vertex_start(HCPcnf, N, m)                      # constraints (3")
    vertex_end(HCPcnf, N, m)                        # constraints (4")
    vertex_positions(HCPcnf, N, m)                  # constraints (5")
    
    
    # print("hcp")
    # print(HCPcnf)
    
    
    # SAT solver
    solver = Glucose3()
    solver.append_formula(HCPcnf)
    
    if solver.solve():
        print("Solution found")
        model = solver.get_model()
        HCP = []
        for var in model:
            for i in range(1, N+1):
                for j in range(1, N+1):
                    if var == getH(i, j):
                        print(i, "->", j)
                        HCP.append((i, j))
                
        print("Hamiltonian cycle:", end=" ")
        vertex = 1
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
    else:
        print("No solution")   