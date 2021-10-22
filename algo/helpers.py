import numpy as np

def array_to_trinary(array: np.ndarray) -> int:
    string = ''.join(map(str, array))
    return int(string, 3)
