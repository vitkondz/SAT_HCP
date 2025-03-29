from successor.SuccessorMethod import SuccessorMethod

class LFSR(SuccessorMethod):
    
    def __init__(self, var_manager=None):
        super().__init__(var_manager)
        self.H = {}
        self.P = {}
        
    def getH(self, i, j):
        if (i, j) not in self.H:
            self.H[(i, j)] = self.new_var()
        return self.H[(i, j)]
    
    def getP(self, i, bit): # P(i, bit) = 1 if the i-th bit of the Pi is 1
        if (i, bit) not in self.P:
            self.P[(i, bit)] = self.new_var()
        return self.P[(i, bit)]
    
    def add_default_variables(self, cnf, n, m, graph):
        # Hij = 0 if the arc (i, j) is not in the graph
        for i in range(1, n+1):
            for j in range(1, n+1):
                if j not in graph.graph[i]:
                    cnf.append([-self.getH(i, j)])
        # P1 = 1 (00..01)
        for bit in range(m):
            if bit == m-1:
                cnf.append([self.getP(1, bit)])
            else:
                cnf.append([-self.getP(1, bit)])
                
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
    def vertex_start(self, cnf, n, m):
        for i in range(2, n+1):
            for bit in range(m):
                if bit == m-2: 
                    cnf.append([-self.getH(1, i), self.getP(i, bit)])
                else:
                    cnf.append([-self.getH(1, i), -self.getP(i, bit)])
                    
    # Hi1 -> Pi = n - constraints (4")
    def vertex_end(self, cnf, n, m):
        pass
    
    # Hij -> Pj = Pi + 1 - constraints (5")
    def vertex_positions(self, cnf, n, m):
        for i in range(2, n+1):
            for j in range(2, n+1):
                for bit in range(m-1):
                    # Xi = Yi+1
                    cnf.append([-self.getH(i, j), -self.getP(i, bit), self.getP(j, bit+1)])
                    cnf.append([-self.getH(i, j), self.getP(i, bit), -self.getP(j, bit+1)])
                # >> Y0 = Xm-1 ^ Xm-2
                # -Y0 v (Xm-1 v Xm-2)
                cnf.append([-self.getH(i, j), -self.getP(j, 0), self.getP(i, m-1), self.getP(i, m-2)])
                # -Y0 v (-Xm-1 v -Xm-2)
                cnf.append([-self.getH(i, j), -self.getP(j, 0), -self.getP(i, m-1), -self.getP(i, m-2)])
                # Xm-1 v Y0 v -Xm-2
                cnf.append([-self.getH(i, j), self.getP(i, m-1), self.getP(j, 0), -self.getP(i, m-2)])
                # Xm-2 v Y0 v -Xm-1
                cnf.append([-self.getH(i, j), self.getP(i, m-2), self.getP(j, 0), -self.getP(i, m-1)])

                