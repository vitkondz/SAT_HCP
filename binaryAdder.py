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


def vertex_positions_v2(cnf, n, m):     # version 2 - two-bit incrementor
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
            
            # for bit in range:
            for bit in range(2, m-1, 2):
                # ¬Yi−1 ∧ Xi−1 ⇒ Yi = ¬Xi
                cnf.append([-getH(i, j), getP(j, bit-1), -getP(i, bit-1), -getP(j, bit), -getP(i,bit)])                
                cnf.append([-getH(i, j), getP(j, bit-1), -getP(i, bit-1), getP(j, bit), getP(i,bit)])
                
                # ¬Yi−1 ∧ Xi−1 ∧ Xi ⇒ Yi+1 = ¬Xi+1
                cnf.append([-getH(i, j), getP(j, bit-1), -getP(i, bit-1), -getP(i, bit), getP(j,bit+1), getP(i, bit+1)])
                cnf.append([-getH(i, j), getP(j, bit-1), -getP(i, bit-1), -getP(i, bit), -getP(j,bit+1), -getP(i, bit+1)])
                
                # otherwise: Yi-1 -> ...
                cnf.append([-getH(i, j), -getP(j, bit-1), -getP(i, bit), getP(j, bit)])
                cnf.append([-getH(i, j), -getP(j, bit-1), getP(i, bit), -getP(j, bit)])
                cnf.append([-getH(i, j), -getP(j, bit-1), -getP(i, bit+1), getP(j, bit+1)])
                cnf.append([-getH(i, j), -getP(j, bit-1), getP(i, bit+1), -getP(j, bit+1)])
                
                # otherwise: -Xi-1 -> ...
                cnf.append([-getH(i, j), getP(i, bit-1), -getP(i, bit), getP(j, bit)])
                cnf.append([-getH(i, j), getP(i, bit-1), getP(i, bit), -getP(j, bit)])
                cnf.append([-getH(i, j), getP(i, bit-1), -getP(i, bit+1), getP(j, bit+1)])
                cnf.append([-getH(i, j), getP(i, bit-1), getP(i, bit+1), -getP(j, bit+1)])
                

# CAUTION: This function is not correct at present, it is just a draft
def vertex_positions_v3(cnf, n, m):     # version 3 - four-bit incrementor
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
                
    
def binaryAdder(graph, AMO_method):
    n = graph.V
    set_AMO_encoding(AMO_method)
    global H, P
    H = {}
    P = {}
    m = math.ceil(math.log2(n)) if math.log2(n) != int(math.log2(n)) else int(math.log2(n)) + 1
    cnf = []
    set_varIndex(0)
        
    add_default_variables(cnf, n, m, graph)
    vertex_outgoing_arcs(cnf, n)
    vertex_incoming_arcs(cnf, n)
    vertex_start(cnf, n, m)
    vertex_end(cnf, n, m)
    vertex_positions_v3(cnf, n, m)
    
    return cnf

if __name__ == '__main__':
    
    graph = init_graph_from_file("graphs/v_set/v-120-5.txt")
    
    print("Loading clauses...")
    HCPcnf = binaryAdder(graph, "AMO_binomial")
    
    sol = solve(HCPcnf)
    
    print_result(sol["model"], graph.V, getH)
    print("Clauses:", sol["nofClauses"])
    print("Variables:", sol["nofVariables"])
    
