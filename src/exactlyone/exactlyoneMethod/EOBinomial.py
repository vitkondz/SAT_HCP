from exactlyone.ExactlyOneMethod import ExactlyOneMethod

class EOBinomial(ExactlyOneMethod):
    
    def __init__(self, var_manager=None):
        super().__init__(var_manager)
    
    def at_most_one(self, cnf, literals):
        for i in range(len(literals)):
            for j in range(i+1, len(literals)):
                cnf.append([-literals[i], -literals[j]])
                
    @staticmethod
    def AMO(cnf, literals):
        for i in range(len(literals)):
            for j in range(i+1, len(literals)):
                cnf.append([-literals[i], -literals[j]])