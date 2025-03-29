class VariableManager:
    def __init__(self):
        self.var_index = 0
        
    def new_var(self):
        self.var_index += 1
        return self.var_index
    
    def get_var(self):
        return self.var_index
    
    def set_var(self, var_index):
        self.var_index = var_index
    
    def reset_var(self):
        self.var_index = 0
        

    