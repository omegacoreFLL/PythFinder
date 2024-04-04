class BooleanEx():
    def __init__(self, value: bool):
        self.value = value
    
    def get(self):
        return self.value
    
    def set(self, new: bool):
        self.value = new
    
    def negate(self):
        self.value = not self.value
    
    def compare(self, other = True):
        return self.value == other
    
    def choose(self, fun: str, value = None):
        if fun == "set":
            if value == None:
                raise Exception("choose a boolean to be 'set'")
            self.set(value)
        elif fun == "get":
            self.get()
        elif fun == "negate":
            self.negate()
        elif fun == "compare":
            if value == None:
                raise Exception("choose a boolean to be 'set'")
            self.compare(value)
        else: raise Exception("not a valid function")