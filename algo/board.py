import numpy as np

# TODO add row and column indices to dump 

class Board():
    def __init__(self):
        self.matrix = np.zeros((19, 19), dtype=int)

    def dump(self):
        print(np.array2string(self.matrix, max_line_width=np.inf))
