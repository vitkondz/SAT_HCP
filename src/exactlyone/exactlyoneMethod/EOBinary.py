from exactlyone.ExactlyOneMethod import ExactlyOneMethod
import math

class EOBinary(ExactlyOneMethod):
        
    def __init__(self, var_manager=None):
        super().__init__(var_manager)
    
    def at_most_one(self, cnf, literals):
        if len(literals) <= 1:
            return
        
        n = len(literals)
        m = int(math.ceil(math.log(n, 2)))
        
        newBinaryVars = [self.new_var() for i in range(m)]
        for i in range(n):
            biStr = bin(i)[2:].zfill(m)
            for j in range(m-1, -1, -1):
                if biStr[j] == '1':
                    cnf.append([-literals[i], newBinaryVars[j]])
                else:
                    cnf.append([-literals[i], -newBinaryVars[j]])
                    

                    
