import numpy as np
import pandas as pd
from hashlib import sha1
from algo.move import Move
from algo.constants import EMPTY
from algo.errors import YouAreDumbException

class Board():
    __slots__ = ['matrix', 'move_history', 'pattern_dict', 'possible_moves']

    def __init__(self):
        self.matrix = np.zeros((19, 19), dtype=int)
        self.move_history = []
        self.pattern_dict = {}
        self.possible_moves = None

    def __find_captures(self, move: Move):
        capture_directions = []
        y, x = move.position
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (y + 3*i < 0 or x + 3*j < 0) or \
                    (y + 3*i >= 18 or x + 3*j >= 18): 
                    continue
                if self.matrix[y + i][x + j] == move.get_opposite_color() and \
                   self.matrix[y + 2*i][x + 2*j] == move.get_opposite_color() and \
                   self.matrix[y + 3*i][x + 3*j] == move.color:
                        capture_directions.append((i, j))
        return capture_directions

    def get_hash(self) -> str:
        hash_value = sha1(self.matrix)
        return hash_value.hexdigest()

    def dump(self):
        index = range(19)
        df = pd.DataFrame(self.matrix, columns=index, index=index)
        print(df)

    def record_new_move(self, move: Move) -> int:
        if self.matrix[move.position] != EMPTY:
            print(move.position)
            print("I am about to throw an exception!")
            self.dump()
            input()
            raise YouAreDumbException("The cell is already taken you dum-dum.")
        self.matrix[move.position] = move.color
        self.move_history.append(move)
        captures_count = self.record_captures(move)
        return captures_count

    def record_captures(self, move: Move) -> int:
        capture_directions = self.__find_captures(move)
        y, x = move.position
        for i, j in capture_directions:
            self.matrix[y + i][x + j] = EMPTY
            self.matrix[y + 2*i][x + 2*j] = EMPTY
            self.move_history.append(Move(EMPTY, (y + i, x + j)))
            self.move_history.append(Move(EMPTY, (y + 2*i, x + 2*j)))
        return len(capture_directions)

    def undo_move(self):
        last_move = next((i for i in reversed(self.move_history) if i.color != EMPTY), None)
        self.matrix[last_move.position] = EMPTY

        last = self.move_history.pop()
        while last.color == EMPTY:
            self.matrix[last.position] = last_move.get_opposite_color()
            last = self.move_history.pop()
        # last_real_move = next((move for move in reversed(self.move_history) if move.color != EMPTY))
        # last_move = self.move_history.pop()
        # while last_move.color == EMPTY:
        #     self.matrix[last_move.position] = last_real_move.get_opposite_color()
        #     last_move = self.move_history.pop()
        # self.matrix[last_move.position] = EMPTY

    def get_possible_moves(self, color: int) -> list[Move]:
        # if self.possible_moves is not None:
        #     return list(map(lambda possible_move: Move(color, possible_move), self.possible_moves))
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
                #replace with if not [i + i_delta, j + j_delta] in full_cells_indices
                    if self.matrix[i + i_delta, j + j_delta] == EMPTY:
                        possible_moves.add((i + i_delta, j + j_delta))
        return list(map(lambda possible_move: Move(color, possible_move), possible_moves))

    def get_list_of_patterns(self, move: Move) -> list[np.ndarray]:
        if move in self.pattern_dict:
            return self.pattern_dict[move]

        y, x = move.position

        matrix_tmp = self.matrix * move.color

        horizontal_axe = matrix_tmp[y,:]
        vertical_axe = matrix_tmp[:,x]
        main_diagonal = matrix_tmp.diagonal(x - y)
        secondary_diagonal = np.fliplr(matrix_tmp).diagonal(18 - x - y)

        self.pattern_dict[move] = [
            (horizontal_axe, x),
            (vertical_axe, y),
            (main_diagonal, min(x, y)),
            (secondary_diagonal, min(18 - x, y)),
        ]

        return self.pattern_dict[move]

    def copy(self):
        new_board = Board()
        new_board.matrix = self.matrix.copy()
        new_board.move_history = self.move_history.copy()
        new_board.pattern_dict = self.pattern_dict.copy()
        
        return new_board