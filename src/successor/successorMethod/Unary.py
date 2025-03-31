from successor.SuccessorMethod import SuccessorMethod
from utils.common import find_distance, find_distance_to_first

class Unary(SuccessorMethod):
        
    def __init__(self, var_manager=None):
        super().__init__(var_manager)
        self.H = {}
        self.U = {}
        
    def getH(self, i, j):
        if (i, j) not in self.H:
            self.H[(i, j)] = self.new_var()
        return self.H[(i, j)]
    
    def getU(self, i, j):
        if (i, j) not in self.U:
            self.U[(i, j)] = self.new_var()
        return self.U[(i, j)]
    
    def preprocessing(self, cnf, graph):
        n = graph.v
        start_v = graph.start_vertex
        distance = find_distance(graph.graph, start_v)
        distance_to_first = distance if not graph.is_directed else find_distance_to_first(graph.graph, start_v)
        
        for vertex in range(1, n+1):
            if vertex == start_v:
                continue
            
            # Uit = 0 if the minimun distance from vertex 1 to vertex i is greater than t
            for t in range(1, distance[vertex]+1):
                cnf.append([-self.getU(vertex, t)])
                
            # Uit = 0 if the minimun distance from vertex i to vertex 1 is greater than n-t
            for t in range(n-distance_to_first[vertex]+2, n+1):
                cnf.append([-self.getU(vertex, t)])  
                                 

    # add variables default with True/False to the cnf
    def add_default_variables(self, cnf, n, graph):
        # Hij = 0 if the arc (i, j) is not in the graph
        for i in range(1, n+1):
            for j in range(1, n+1):
                if j not in graph.graph[i]:
                    cnf.append([-self.getH(i, j)])
        # U_start_1 is initialized to True
        start_v = graph.start_vertex
        cnf.append([self.getU(start_v, 1)])
        
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

    # H1i -> Ui2 - constraints (3')
    def vertex_start(self, cnf, n, graph):
        start_v = graph.start_vertex
        for i in range(1, n+1):
            if i == start_v:
                continue
            cnf.append([-self.getH(start_v, i), self.getU(i, 2)])

    # Hi1 -> Uin - constraints (4')
    def vertex_end(self, cnf, n, graph):
        start_v = graph.start_vertex
        for i in range(1, n+1):
            if i == start_v:
                continue
            cnf.append([-self.getH(i, start_v), self.getU(i, n)])
            
    # Hij ^ Uip -> Uj(p+1) - constraints (5')
    def vertex_positions(self, cnf, n, graph):
        start_v = graph.start_vertex
        for i in range(1, n+1):
            for j in range(1, n+1):
                if i != start_v and j != start_v and i != j:
                    for p in range(2, n):
                        cnf.append([-self.getH(i, j), -self.getU(i, p), self.getU(j, p+1)])

    # exactly one position for each vertex - constraints (6)
    def vertex_EO_positions(self, cnf, n):
        for i in range(1, n+1):
            literals = [self.getU(i, p) for p in range(1, n+1)]
            self.exactly_one_constraint(cnf, literals)
    
    def build_clauses(self, cnf, graph):
        n = graph.v
        
        if self.is_preprocessing:
            self.preprocessing(cnf, graph)
            
        self.add_default_variables(cnf, n, graph)
        self.vertex_outgoing_arcs(cnf, n)
        self.vertex_incoming_arcs(cnf, n)
        self.vertex_start(cnf, n, graph)
        self.vertex_end(cnf, n, graph)
        self.vertex_positions(cnf, n, graph)
        self.vertex_EO_positions(cnf, n)
        return cnf
        