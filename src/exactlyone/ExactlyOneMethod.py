class ExactlyOneMethod:
        
    def __init__(self, var_manager):
        self.var_manager = var_manager
    
    def exactly_one(self, cnf, literals):
        self.at_least_one(cnf, literals)
        self.at_most_one(cnf, literals)
        
    def at_least_one(self, cnf, literals):
        cnf.append(literals)
                
    def at_most_one(self, cnf, literals):
        pass
    
    def set_var_manager(self, var_manager):
        self.var_manager = var_manager
    
    def new_var(self):
        return self.var_manager.new_var()