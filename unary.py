from pysat.solvers import Glucose3
import time

from common import *

# function to get variable for H and U
def getH(i, j):
    global H
    if (i, j) not in H:
        H[(i, j)] = new_var()
    return H[(i, j)]

def getU(i, j):
    global U
    if (i, j) not in U:
        U[(i, j)] = new_var()
    return U[(i, j)]

# exactly one constraint
def exactly_one(cnf, literals):
    ALO(cnf, literals)
    AMO_binomial(cnf, literals) # AMO by binomial
    
    
# add variables default with True/False to the cnf
def add_default_variables(cnf, n, graph):
    # Hij = 0 if the arc (i, j) is not in the graph
    for i in range(1, n+1):
        for j in range(1, n+1):
            if j not in graph.graph[i]:
                cnf.append([-getH(i, j)])
    # U11 is initialized to True
    cnf.append([getU(1, 1)])
    
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

# H1i -> Ui2 - constraints (3')
def vertex_start(cnf, n):
    for i in range(2, n+1):
        cnf.append([-getH(1, i), getU(i, 2)])

# Hi1 -> Uin - constraints (4')
def vertex_end(cnf, n):
    for i in range(2, n+1):
        cnf.append([-getH(i, 1), getU(i, n)])
        
# Hij ^ Uip -> Uj(p+1) - constraints (5')
def vertex_positions(cnf, n):
    for i in range(2, n+1):
        for j in range(2, n+1):
            for p in range(2, n):
                cnf.append([-getH(i, j), -getU(i, p), getU(j, p+1)])

# exactly one position for each vertex - constraints (6)
def vertex_EO_positions(cnf, n, U):
    for i in range(1, n+1):
        literals = [getU(i, p) for p in range(1, n+1)]
        exactly_one(cnf, literals)

def unary(graph):
    n = graph.V
    
    global H, U
    H = {}
    U = {}
    cnf = []
    
    add_default_variables(cnf, n, graph)
    vertex_outgoing_arcs(cnf, n)
    vertex_incoming_arcs(cnf, n)
    vertex_start(cnf, n)
    vertex_end(cnf, n)
    vertex_positions(cnf, n)
    vertex_EO_positions(cnf, n, U)
    
    return cnf

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
    
def print_result(model, N):
    HCP = []
    for var in model:
        for i in range(1, N+1):
            for j in range(1, N+1):
                if var == getH(i, j):
                    # print(i, "->", j)
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
    print("Veticles: ", len(HCP))
    

if __name__ == '__main__':

    graph = init_graph_from_file("graphs/hc-28-5-2.col")
    
    HCPcnf = unary(graph)
    
    isSat = solve(HCPcnf)
    
    if isSat[0] is not None:
        print("Solution found")
        print_result(isSat[0], graph.V)
        print("Time:", isSat[1])
    else:
        print("No solution")