class ReturnSignal(Exception): # exception for signalling return stmt in a function
    def __init__(self, value):
        super().__init__()
        self.value = value

class BreakSignal(Exception): # exception for signalling break stmt in a loop
    pass