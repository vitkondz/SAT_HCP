from pysat.solvers import Glucose3
import time

from common import *

# function to get variable for H and P
def getH(i, j):
    global H
    if (i, j) not in H:
        H[(i, j)] = new_var()
    return H[(i, j)]

def getP(i, bit):  # P(i, bit) = 1 if the i-th bit of the Pi is 1
    global P
    if (i, bit) not in P:
        P[(i, bit)] = new_var()
    return P[(i, bit)]

def exactly_one(cnf, literals):
    ALO(cnf, literals)
    AMO_binomial(cnf, literals)

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
                
# Hij -> Pj = Pi + 1 - constraints (5") - one-bit incrementor
def vertex_positions(cnf, n, m):
    for i in range(2, n+1):
        for j in range(2, n+1):
            for bit in range(m):
                if bit == 0: # y0 = -x0
                    cnf.append([-getH(i, j), getP(i, 0), getP(j, 0)])
                    cnf.append([-getH(i, j), -getP(i, 0), -getP(j, 0)])
                elif bit == 1: # x0 -> y1 = -x1 and -x0 -> y1 = x1
                    cnf.append([-getH(i, j), -getP(i, 0), getP(i, 1), getP(j, 1)])
                    cnf.append([-getH(i, j), -getP(i, 0), -getP(i, 1), -getP(j, 1)])
                    cnf.append([-getH(i, j), getP(i, 0), getP(i, 1), -getP(j, 1)])
                    cnf.append([-getH(i, j), getP(i, 0), -getP(i, 1), getP(j, 1)]) 
                # version 1 - one-bit incrementor
                else:
                    #carry = 1, -Yi-1 ^ Xi-1 -> Yi = -Xi
                    cnf.append([-getH(i, j), getP(j, bit-1), -getP(i, bit-1), getP(j, bit), getP(i, bit)])
                    cnf.append([-getH(i, j), getP(j, bit-1), -getP(i, bit-1), -getP(j, bit), -getP(i, bit)])
                    # carry = 0, -Yi-1 ^ -Xi-1 -> Yi = Xi
                    cnf.append([-getH(i, j), getP(j, bit-1), getP(i, bit-1), getP(j, bit), -getP(i, bit)])
                    cnf.append([-getH(i, j), getP(j, bit-1), getP(i, bit-1), -getP(j, bit), getP(i, bit)])
                    # carry = 0, Yi-1 -> Yi = Xi
                    cnf.append([-getH(i, j), -getP(j, bit-1), getP(j, bit), -getP(i, bit)])
                    cnf.append([-getH(i, j), -getP(j, bit-1), -getP(j, bit), getP(i, bit)])

# CAUTION: This function is not correct at present, it is just a draft
def vertex_positions_v2(cnf, n, m):     # version 2 - four-bit incrementor
    for i in range(2, n+1):
        for j in range(2, n+1):
            # bit == 0: # y0 = -x0
            cnf.append([-getH(i, j), getP(i, 0), getP(j, 0)])
            cnf.append([-getH(i, j), -getP(i, 0), -getP(j, 0)])
            # bit == 1: # x0 -> y1 = -x1 and -x0 -> y1 = x1
            cnf.append([-getH(i, j), -getP(i, 0), getP(i, 1), getP(j, 1)])
            cnf.append([-getH(i, j), -getP(i, 0), -getP(i, 1), -getP(j, 1)])
            cnf.append([-getH(i, j), getP(i, 0), getP(i, 1), -getP(j, 1)])
            cnf.append([-getH(i, j), getP(i, 0), -getP(i, 1), getP(j, 1)]) 

            for bit in range(6, m+1, 4):
                cnf.append([-getH(i, j), getP(i, bit-1), getP(i, bit-4), -getP(j, bit-1)])                                  #1
                cnf.append([-getH(i, j), getP(i, bit-1), -getP(j, bit-1), -getP(j, bit-2)])                                 #2
                cnf.append([-getH(i, j), getP(i, bit-1), -getP(j, bit-1), -getP(j, bit-3)])                                 #3
                cnf.append([-getH(i, j), getP(i, bit-1), -getP(j, bit-1), -getP(j, bit-4)])                                 #4
                cnf.append([-getH(i, j), getP(i, bit-3), -getP(j, bit-3), -getP(j, bit-4)])                                 #5
                cnf.append([-getH(i, j), -getP(i, bit-4), -getP(j, bit-5), getP(j, bit-4)])                                 #6
                cnf.append([-getH(i, j), getP(i, bit-2), -getP(i, bit-3), getP(j, bit-2), getP(j, bit-3)])                  #7
                cnf.append([-getH(i, j), getP(i, bit-4), getP(i, bit-5), -getP(j, bit-4)])                                  #8
                cnf.append([-getH(i, j), -getP(i, bit-1), getP(j, bit-1)])                                                  #9
                cnf.append([-getH(i, j), -getP(i, bit-2), -getP(i, bit-3), -getP(j, bit-2), getP(j, bit-3)])                #10
                cnf.append([-getH(i, j), -getP(i, bit-3), -getP(i, bit-4), -getP(i, bit-5), getP(j, bit-5), -getP(j, bit-3)]) #11
                cnf.append([-getH(i, j), getP(i, bit-2), getP(i, bit-4), -getP(j, bit-2)])                                  #12
                cnf.append([-getH(i, j), getP(i, bit-3), getP(i, bit-4), -getP(j, bit-3)])                                  #13
                cnf.append([-getH(i, j), getP(i, bit-2), -getP(j, bit-2), -getP(j, bit-3)])                                 #14
                cnf.append([-getH(i, j), getP(i, bit-2), -getP(j, bit-2), -getP(j, bit-4)])                                 #15
                cnf.append([-getH(i, j), -getP(i, bit-4), getP(i, bit-5), getP(j, bit-4)])                                  #16
                cnf.append([-getH(i, j), getP(i, bit-1), -getP(i, bit-2), getP(j, bit-1), getP(j, bit-2)])                  #17
                cnf.append([-getH(i, j), getP(i, bit-4), -getP(i, bit-5), getP(j, bit-5), getP(j, bit-4)])                  #18
                cnf.append([-getH(i, j), getP(i, bit-4), -getP(j, bit-5), -getP(j, bit-4)])                                 #19
                cnf.append([-getH(i, j), -getP(i, bit-1), -getP(i, bit-2), -getP(j, bit-1), getP(j, bit-2)])                #20
                cnf.append([-getH(i, j), getP(i, bit-3), -getP(i, bit-4), -getP(i, bit-5), getP(j, bit-5), getP(j, bit-3)]) #21
                
    
def binaryAdder(graph):
    n = graph.V
    
    global H, P
    H = {}
    P = {}
    m = math.ceil(math.log2(n)) if math.log2(n) != int(math.log2(n)) else int(math.log2(n)) + 1
    cnf = []
    
    add_default_variables(cnf, n, m, graph)
    vertex_outgoing_arcs(cnf, n)
    vertex_incoming_arcs(cnf, n)
    vertex_start(cnf, n, m)
    vertex_end(cnf, n, m)
    vertex_positions(cnf, n, m)
    
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
        if var > 0:
            for i in range(1, N+1):
                for j in range(1, N+1):
                    if var == getH(i, j):
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
    print("Veticles: ", num)

if __name__ == '__main__':
    
    graph = init_graph_from_file("graphs/hc-28-4-1.col")
    
    HCPcnf = binaryAdder(graph)
    
    isSat = solve(HCPcnf)
    
    if isSat[0] is not None:
        print("Solution found")
        print_result(isSat[0], graph.V)
        print("Time:", isSat[1])
    else:
        print("No solution")
    