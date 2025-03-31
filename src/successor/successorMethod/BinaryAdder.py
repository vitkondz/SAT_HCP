from successor.SuccessorMethod import SuccessorMethod
from utils.common import find_distance, find_distance_to_first
import math

class BinaryAdder(SuccessorMethod):
        
    def __init__(self, var_manager=None):
        super().__init__(var_manager)
        self.H = {}
        self.P = {}
        
    def getH(self, i, j):
        if (i, j) not in self.H:
            self.H[(i, j)] = self.new_var()
        return self.H[(i, j)]
    
    def getP(self, i, bit): # P(i, bit) = 1 if the bit-th bit of the Pi is 1
        if (i, bit) not in self.P:
            self.P[(i, bit)] = self.new_var()
        return self.P[(i, bit)]
    
    def preprocessing(self, cnf, graph, m):
        n = graph.v
        start_v = graph.start_vertex
        distance = find_distance(graph.graph, start_v)
        distance_to_first = distance if not graph.is_directed else find_distance_to_first(graph.graph, start_v)
        
        for vertex in range(1, n+1):
            if vertex == start_v:
                continue
            
            # Pi != t if the minimum distance from vertex 1 to vertex i is greater than t
            for t in range(1, distance[vertex]+1):
                binaryT = bin(t)[2:].zfill(m)[::-1]     # convert t to binary
                cnf.append([-self.getP(vertex, bit) if binaryT[bit] == '1' else self.getP(vertex, bit) for bit in range(m)])
            
            # Pi != t if the minimum distance from vertex i to vertex 1 is greater than n-t
            for t in range(n-distance_to_first[vertex]+2, n+1):
                binaryT = bin(t)[2:].zfill(m)[::-1]
                cnf.append([-self.getP(vertex, bit) if binaryT[bit] == '1' else self.getP(vertex, bit) for bit in range(m)])
        
    def preprocessing_v2(self, cnf, graph, m):
        n = graph.v
        start_v = graph.start_vertex
        distance = find_distance(graph.graph, start_v)
        distance_to_first = distance if not graph.is_directed else find_distance_to_first(graph.graph, start_v)
        
        for vertex in range(1, n+1):
            if vertex == start_v:
                continue
            
            # Pi >= t+1 if the minimum distance from vertex 1 to vertex i is t
            d_v = distance[vertex]
            binaryD = bin(d_v + 1)[2:].zfill(m)[::-1]     # convert d to binary
            for bit in range(m):
                if binaryD[bit] == '1':
                    cnf.append([self.getP(vertex, bit)] + 
                               [self.getP(vertex, i) if binaryD[i] == '0' else -self.getP(vertex, i) for i in range(bit+1, m)])
                        
            # Pi <= n-t+1 if the minimun distance from vertex i to vertex 1 is t
            d_v_to_first = distance_to_first[vertex]
            binaryD = bin(n - d_v_to_first + 1)[2:].zfill(m)[::-1]
            for bit in range(m):
                if binaryD[bit] == '0':
                    cnf.append([-self.getP(vertex, bit)] +
                               [self.getP(vertex, i) if binaryD[i] == '0' else -self.getP(vertex, i) for i in range(bit+1, m)])
            
        
    # add variables with default value to the cnf
    def add_default_variables(self, cnf, n, m, graph):
        # Hij = 0 if the arc (i, j) is not in the graph
        for i in range(1, n+1):
            for j in range(1, n+1):
                if j not in graph.graph[i]:
                    cnf.append([-self.getH(i, j)])
        
        # P_start = 1 (00..01)            
        start_v = graph.start_vertex
        for bit in range(m):
            if bit == 0:
                cnf.append([self.getP(start_v, bit)])
            else:
                cnf.append([-self.getP(start_v, bit)])  
    
    # each vertex has exactly one outgoing arc - constraints (1)
    def vertex_outgoing_arcs(self, cnf, n):
        for i in range(1, n+1):
            literals = []
            for j in range(1, n+1):
                literals.append(self.getH(i, j))
            self.exactly_one_constraint(cnf, literals)
            
    # each vertex has exactly one incoming arc - constraints (2)
    def vertex_incoming_arcs(self, cnf, n):
        for j in range(1, n+1):
            literals = []
            for i in range(1, n+1):
                literals.append(self.getH(i, j))
            self.exactly_one_constraint(cnf, literals)
            
    # H1i -> Pi = 2 (00..10) - constraints (3")
    def vertex_start(self, cnf, n, m, graph):
        start_v = graph.start_vertex
        for i in range(1, n+1):
            if i == start_v:
                continue
            for bit in range(m):
                if bit == 1: 
                    cnf.append([-self.getH(start_v, i), self.getP(i, bit)])
                else:
                    cnf.append([-self.getH(start_v, i), -self.getP(i, bit)])
                    
    # Hi1 -> Pi = n - constraints (4")
    def vertex_end(self, cnf, n, m, graph):
        start_v = graph.start_vertex
        binaryN = bin(n)[2:][::-1]
        for i in range(1, n+1):
            if i == start_v:
                continue
            for bit in range(m):
                if binaryN[bit] == '1':
                    cnf.append([-self.getH(i, start_v), self.getP(i, bit)])
                else:
                    cnf.append([-self.getH(i, start_v), -self.getP(i, bit)])
         
    # version final - 2 bit and top 4 bit incrementor - only use for graph more than 32 vertex
    def vertex_positions_final(self, cnf, n, m, graph):
        start_v = graph.start_vertex
        for i in range(1, n+1):
            for j in range(1, n+1):
                if i == start_v or j == start_v or i == j:
                    continue
                
                # bit == 0: # y0 = -x0
                cnf.append([-self.getH(i, j), self.getP(i, 0), self.getP(j, 0)])
                cnf.append([-self.getH(i, j), -self.getP(i, 0), -self.getP(j, 0)])
                # bit == 1: # x0 -> y1 = -x1 and -x0 -> y1 = x1
                cnf.append([-self.getH(i, j), -self.getP(i, 0), self.getP(i, 1), self.getP(j, 1)])
                cnf.append([-self.getH(i, j), -self.getP(i, 0), -self.getP(i, 1), -self.getP(j, 1)])
                cnf.append([-self.getH(i, j), self.getP(i, 0), self.getP(i, 1), -self.getP(j, 1)])
                cnf.append([-self.getH(i, j), self.getP(i, 0), -self.getP(i, 1), self.getP(j, 1)]) 
                
                # 2-bit incrementor
                for bit in range(2, m-4, 2):
                    # ¬Yi−1 ∧ Xi−1 ⇒ Yi = ¬Xi
                    # remove the clause of -getP(j, bit) and -getP(j, bit)
                    cnf.append([-self.getH(i, j), self.getP(j, bit-1), -self.getP(i, bit-1), self.getP(j, bit), self.getP(i, bit)])
                    
                    # ¬Yi−1 ∧ Xi−1 ∧ Xi ⇒ Yi+1 = ¬Xi+1
                    cnf.append([-self.getH(i, j), self.getP(j, bit-1), -self.getP(i, bit-1), -self.getP(i, bit), self.getP(j, bit+1), self.getP(i, bit+1)])       # so far so good
                    cnf.append([-self.getH(i, j), self.getP(j, bit-1), -self.getP(i, bit-1), -self.getP(i, bit), -self.getP(j, bit+1), -self.getP(i, bit+1)])     # so far so good
                    
                    # otherwise: Yi-1 -> Yi = Xi
                    cnf.append([-self.getH(i, j), -self.getP(j, bit-1), -self.getP(i, bit), self.getP(j, bit)])
                    cnf.append([-self.getH(i, j), -self.getP(j, bit-1), self.getP(i, bit), -self.getP(j, bit)])
                    
                    # otherwise: -Xi-1 -> Yi = Xi
                    cnf.append([-self.getH(i, j), self.getP(i, bit-1), -self.getP(i, bit), self.getP(j, bit)])
                    cnf.append([-self.getH(i, j), self.getP(i, bit-1), self.getP(i, bit), -self.getP(j, bit)])
                    
                    #special: -Xi -> Yi+1 = Xi+1
                    cnf.append([-self.getH(i, j), self.getP(i, bit), self.getP(j, bit+1), -self.getP(i, bit+1)])
                    cnf.append([-self.getH(i, j), self.getP(i, bit), -self.getP(j, bit+1), self.getP(i, bit+1)])
                    
                    #special: Yi -> Yi+1 = Xi+1
                    cnf.append([-self.getH(i, j), -self.getP(j, bit), self.getP(j, bit+1), -self.getP(i, bit+1)])
                    cnf.append([-self.getH(i, j), -self.getP(j, bit), -self.getP(j, bit+1), self.getP(i, bit+1)])
                
                # the last bit if remain using 1-bit incrementor
                if m%2 == 1:
                    bit = m-5
                    #carry = 1, -Yi-1 ^ Xi-1 -> Yi = -Xi
                    cnf.append([-self.getH(i, j), self.getP(j, bit-1), -self.getP(i, bit-1), self.getP(j, bit), self.getP(i, bit)])
                    cnf.append([-self.getH(i, j), self.getP(j, bit-1), -self.getP(i, bit-1), -self.getP(j, bit), -self.getP(i, bit)])
                    # carry = 0, -Xi-1 -> Yi = Xi
                    cnf.append([-self.getH(i, j), self.getP(i, bit-1), self.getP(j, bit), -self.getP(i, bit)])
                    cnf.append([-self.getH(i, j), self.getP(i, bit-1), -self.getP(j, bit), self.getP(i, bit)])
                    # carry = 0, Yi-1 -> Yi = Xi
                    cnf.append([-self.getH(i, j), -self.getP(j, bit-1), self.getP(j, bit), -self.getP(i, bit)])
                    cnf.append([-self.getH(i, j), -self.getP(j, bit-1), -self.getP(j, bit), self.getP(i, bit)])
                    
                # top 4 bits 
                bit = m
                cnf.append([-self.getH(i, j), self.getP(i, bit-1), self.getP(i, bit-4), -self.getP(j, bit-1)])                                  #1
                cnf.append([-self.getH(i, j), self.getP(i, bit-1), -self.getP(j, bit-1), -self.getP(j, bit-2)])                                 #2
                cnf.append([-self.getH(i, j), self.getP(i, bit-1), -self.getP(j, bit-1), -self.getP(j, bit-3)])                                 #3
                cnf.append([-self.getH(i, j), self.getP(i, bit-1), -self.getP(j, bit-1), -self.getP(j, bit-4)])                                 #4
                cnf.append([-self.getH(i, j), self.getP(i, bit-3), -self.getP(j, bit-3), -self.getP(j, bit-4)])                                 #5
                cnf.append([-self.getH(i, j), -self.getP(i, bit-4), -self.getP(j, bit-5), self.getP(j, bit-4)])                                 #6
                cnf.append([-self.getH(i, j), self.getP(i, bit-2), -self.getP(i, bit-3), self.getP(j, bit-2), self.getP(j, bit-3)])                  #7
                cnf.append([-self.getH(i, j), self.getP(i, bit-4), self.getP(i, bit-5), -self.getP(j, bit-4)])                                  #8
                cnf.append([-self.getH(i, j), -self.getP(i, bit-1), self.getP(j, bit-1)])                                                  #9
                cnf.append([-self.getH(i, j), -self.getP(i, bit-2), -self.getP(i, bit-3), -self.getP(j, bit-2), self.getP(j, bit-3)])                #10
                cnf.append([-self.getH(i, j), -self.getP(i, bit-3), -self.getP(i, bit-4), -self.getP(i, bit-5), self.getP(j, bit-5), -self.getP(j, bit-3)]) #11
                cnf.append([-self.getH(i, j), self.getP(i, bit-2), self.getP(i, bit-4), -self.getP(j, bit-2)])                                  #12
                cnf.append([-self.getH(i, j), self.getP(i, bit-3), self.getP(i, bit-4), -self.getP(j, bit-3)])                                  #13
                cnf.append([-self.getH(i, j), self.getP(i, bit-2), -self.getP(j, bit-2), -self.getP(j, bit-3)])                                 #14
                cnf.append([-self.getH(i, j), self.getP(i, bit-2), -self.getP(j, bit-2), -self.getP(j, bit-4)])                                 #15
                cnf.append([-self.getH(i, j), -self.getP(i, bit-4), self.getP(i, bit-5), self.getP(j, bit-4)])                                  #16
                cnf.append([-self.getH(i, j), self.getP(i, bit-1), -self.getP(i, bit-2), self.getP(j, bit-1), self.getP(j, bit-2)])                  #17
                cnf.append([-self.getH(i, j), self.getP(i, bit-4), -self.getP(i, bit-5), self.getP(j, bit-5), self.getP(j, bit-4)])                  #18
                cnf.append([-self.getH(i, j), self.getP(i, bit-4), -self.getP(j, bit-5), -self.getP(j, bit-4)])                                 #19
                cnf.append([-self.getH(i, j), -self.getP(i, bit-1), -self.getP(i, bit-2), -self.getP(j, bit-1), self.getP(j, bit-2)])                #20
                cnf.append([-self.getH(i, j), self.getP(i, bit-3), -self.getP(i, bit-4), -self.getP(i, bit-5), self.getP(j, bit-5), self.getP(j, bit-3)]) #21
                
    def build_clauses(self, cnf, graph):
        n = graph.v
        m = math.ceil(math.log2(n)) if math.log2(n) != int(math.log2(n)) else int(math.log2(n)) + 1
        
        if self.is_preprocessing:
            self.preprocessing_v2(cnf, graph, m)
            
        self.add_default_variables(cnf, n, m, graph)
        self.vertex_outgoing_arcs(cnf, n)
        self.vertex_incoming_arcs(cnf, n)
        self.vertex_start(cnf, n, m, graph)
        self.vertex_end(cnf, n, m, graph)
        self.vertex_positions_final(cnf, n, m, graph) # for final version

        return cnf