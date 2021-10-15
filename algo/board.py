import numpy as np
from hashlib import sha1
from algo.move import Move
from algo.constants import EMPTY
from algo.errors import YouAreDumbException

# TODO add row and column indices to dump 

class Board():
    def __init__(self):
        self.matrix = np.zeros((19, 19), dtype=int)
        self.move_history = []

    def __find_captures(self, move: Move):
        capture_directions = []
        y, x = move.position
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (x + 3*i < 0 or y + 3*j < 0) or \
                    (x + 3*i >= 18 or y + 3*j >= 18): 
                    continue
                if self.matrix[x + i][y + j] == move.get_opposite_color() and \
                   self.matrix[x + 2*i][y + 2*j] == move.get_opposite_color() and \
                   self.matrix[x + 3*i][y + 3*j] == move.color:
                        capture_directions.append((i, j))
        return capture_directions

    def get_hash(self):
        # self.matrix.flags.writeable = False
        hash_value = sha1(self.matrix)
        # self.matrix.flags.writeable = True
        return hash_value.hexdigest()

    def dump(self):
        print(np.array2string(self.matrix, max_line_width=np.inf))

    def record_new_move(self, move: Move) -> int:
        if self.matrix[move.position] != EMPTY:
            raise YouAreDumbException("The cell is already taken you dum-dum.")
        self.matrix[move.position] = move.color
        self.move_history.append(move)
        captures_count = self.record_captures(move)
        return captures_count

    def record_captures(self, move: Move) -> int:
        capture_directions = self.__find_captures(move)
        y, x = move.position
        for i, j in capture_directions:
            self.matrix[x + i][y + j] = EMPTY
            self.matrix[x + 2*i][y + 2*j] = EMPTY
            self.move_history.append(Move(EMPTY, (x + i, y + j)))
            self.move_history.append(Move(EMPTY, (x + 2*i, y + 2*j)))
        return len(capture_directions)

    def undo_move(self):
        last_move = next((i for i in reversed(self.move_history) if i.color != EMPTY), None)
        self.matrix[last_move.position] = EMPTY
        
        last = self.move_history.pop()
        while last.color == EMPTY:
            self.matrix[last.position] = last_move.get_opposite_color()
            last = self.move_history.pop()

    def get_possible_moves(self, color: int) -> list[Move]:
        possible_moves = set()
        full_cells_indices = np.transpose(self.matrix.nonzero())
        for full_cell_index in full_cells_indices:
            i, j = tuple(full_cell_index)
            for i_delta in range(-1, 2):
                for j_delta in range(-1, 2):
                    if i_delta == j_delta == 0 \
                            or i + i_delta < 0 or i + i_delta > 18 \
                            or j + j_delta < 0 or j + j_delta > 18 :
                        continue
                    if self.matrix[i + i_delta, j + j_delta] == EMPTY:
                        possible_moves.add((i + i_delta, j + j_delta))
        return list(map(lambda possible_move: Move(color, possible_move), possible_moves))
