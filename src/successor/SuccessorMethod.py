class SuccessorMethod:        
    def __init__(self, var_manager):
        self.var_manager = var_manager
        self.cnf = []
        self.exactly_one_method = None
        self.graph = None
        self.is_preprocessing = True
        
    def set_graph(self, graph):
        self.graph = graph
    
    def set_exactly_one_method(self, EO_method):
        self.exactly_one_method = EO_method
        
    def exactly_one_constraint(self, cnf, literals):
        self.exactly_one_method.exactly_one(cnf, literals)
        
    def set_var_manager(self, var_manager):
        self.var_manager = var_manager
        
    def set_is_preprocessing(self, is_preprocessing):
        self.is_preprocessing = is_preprocessing
        
    def new_var(self):
        return self.var_manager.new_var()
    
    def build_clauses():
        pass
    
    