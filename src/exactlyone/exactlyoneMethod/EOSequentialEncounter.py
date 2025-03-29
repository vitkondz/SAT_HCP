from exactlyone.ExactlyOneMethod import ExactlyOneMethod

class EOSequentialEncounter(ExactlyOneMethod):
    
    def __init__(self, var_manager=None):
        super().__init__(var_manager)
    
    def at_most_one(self, cnf, literals):
        n = len(literals)
        S = [self.new_var() for i in range(n-1)]
        cnf.append([-literals[0], S[0]])
        for i in range(1, n-1):
            cnf.append([-literals[i], S[i]])
            cnf.append([-S[i-1], S[i]])
            cnf.append([-literals[i], -S[i-1]])
        cnf.append([-S[n-2], -literals[n-1]])