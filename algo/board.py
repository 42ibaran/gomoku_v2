import numpy as np
import pandas as pd
import time
import pickle
from hashlib import sha1
from .move import Move
from .constants import EMPTY, WHITE, BLACK, PATTERN_SIZES
from .errors import YouAreDumbException
from .masks import MASKS, Patterns, PatternsValue, masks_2

# Patterns list explanation:
#   First 19 numbers represent rows of the matrix
#   Next 19 numbers represent columns of the matrix
#   Next 37 numbers represent main diagonals of the matrix
# starting in the bottom left corner
#   Next 37 numbers represent secondary diagonals of the matrix
# starting in the top left corner

PATTERN_ROW            = 0
PATTERN_COLUMN         = 0 + 19
PATTERN_MAIN_DIAG      = 0 + 19 + 19
PATTERN_SECONDARY_DIAG = 0 + 19 + 19 + 37

pattern_score_hashtable = {}

class Board():
    __slots__ = ['matrix', 'move_history', 'possible_moves', 'patterns', 'score', 'is_five_in_a_row']

    def __init__(self):
        self.matrix = np.zeros((19, 19), dtype=int)
        self.move_history = [Move]
        self.patterns = [0] * ((19 + 37) * 2)
        self.possible_moves = None
        self.score = None
        self.is_five_in_a_row = None

    def __find_captures(self, move: Move) -> list[tuple[int]]:
        capture_directions = []
        y, x = move.position
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (y + 3*i < 0 or x + 3*j < 0) or \
                    (y + 3*i >= 18 or x + 3*j >= 18): 
                    continue
                if self.matrix[y + i][x + j] == move.opposite_color and \
                   self.matrix[y + 2*i][x + 2*j] == move.opposite_color and \
                   self.matrix[y + 3*i][x + 3*j] == move.color:
                    capture_directions.append((i, j))
        return capture_directions

    def __update_patterns(self, move: Move, undo: bool = False) -> None:
        y, x = move.position

        if move.color == EMPTY:
            undo = not undo
            color = move.previous_color
        else:
            color = move.color
        color = -color if undo else color

        main_diagonal_power = 18 - max(x, y)
        secondary_diagonal_power = 18 - max(18 - y, x)

        self.patterns[PATTERN_ROW + y] += color * (3 ** (18 - x))
        self.patterns[PATTERN_COLUMN + x] += color * (3 ** (18 - y))
        self.patterns[PATTERN_MAIN_DIAG + 18 + x - y] += color * (3 ** main_diagonal_power)
        self.patterns[PATTERN_SECONDARY_DIAG + x + y] += color * (3 ** secondary_diagonal_power)

    def get_hash(self) -> str:
        hash_value = sha1(self.matrix)
        return hash_value.hexdigest()

    def dump(self) -> None:
        index = range(19)
        df = pd.DataFrame(self.matrix, columns=index, index=index)
        print(df)

    def record_new_move(self, move: Move) -> int:
        if self.matrix[move.position] != EMPTY:
            raise YouAreDumbException("The cell is already taken you dum-dum.")
        self.matrix[move.position] = move.color
        self.move_history.append(move)
        self.__update_patterns(move)
        captures_count = self.record_captures(move)
        return captures_count

    def record_captures(self, move: Move) -> int:
        capture_directions = self.__find_captures(move)
        y, x = move.position
        for i, j in capture_directions:
            capture_move_1 = Move(EMPTY, (y + i, x + j), move.opposite_color)
            capture_move_2 = Move(EMPTY, (y + 2*i, x + 2*j), move.opposite_color)
            self.matrix[capture_move_1.position] = EMPTY
            self.matrix[capture_move_2.position] = EMPTY
            self.__update_patterns(capture_move_1)
            self.__update_patterns(capture_move_2)
            self.move_history.append(capture_move_1)
            self.move_history.append(capture_move_2)
        return len(capture_directions)

    def undo_move(self) -> None:
        while True:
            last = self.move_history.pop()
            self.matrix[last.position] = last.previous_color
            self.__update_patterns(last, undo=True)
            if last.color != EMPTY:
                break

    def get_possible_moves(self, previous_possible_moves: list, last_move: Move) -> list[Move]:
        color = last_move.opposite_color
        if previous_possible_moves:
            previous_possible_moves.remove(last_move)
            i, j = last_move.position
            possible_moves = self.get_possible_moves_for_position(i, j)
            for old_possible_move in previous_possible_moves:
                possible_moves.add(old_possible_move.position)
            for move in reversed(self.move_history):
                if move.color != EMPTY:
                    break
                possible_moves.add(move.position)
        else:
            possible_moves = set()
            full_cells_indices = np.transpose(self.matrix.nonzero())
            for full_cell_index in full_cells_indices:
                i, j = tuple(full_cell_index)
                possible_moves_for_position = self.get_possible_moves_for_position(i, j)
                possible_moves = possible_moves.union(possible_moves_for_position)
        return list(map(lambda possible_move: Move(color, possible_move), possible_moves))

    def get_possible_moves_for_position(self, i: int, j: int) -> set[tuple[int]]:
        possible_moves = set()
        for i_delta in range(-1, 2):
            for j_delta in range(-1, 2):
                if i_delta == j_delta == 0 \
                        or i + i_delta < 0 or i + i_delta > 18 \
                        or j + j_delta < 0 or j + j_delta > 18 :
                    continue
                if self.matrix[i + i_delta, j + j_delta] == EMPTY:
                    possible_moves.add((i + i_delta, j + j_delta))
        return possible_moves

    def get_list_of_patterns(self) -> list[int]:
        return self.patterns

    def evaluate(self) -> (int, bool):
        if self.score is not None and self.is_five_in_a_row is not None:
            return self.score, self.is_five_in_a_row
        # if self.captures[WHITE] >= 10 or self.captures[BLACK] >= 10:
            # self.game_over = True
        self.score = 0
        self.is_five_in_a_row = False
        for pattern, pattern_size in zip(self.patterns, PATTERN_SIZES):
            hash_value = hash((pattern_size, pattern))
            if hash_value in pattern_score_hashtable:
                result = pattern_score_hashtable[hash_value]
                self.score += result[0]
                self.is_five_in_a_row = self.is_five_in_a_row if not result[1] else True
            else:
                pattern_score = 0
                for mask_size, mask_dictionary in MASKS.items():
                    result = self.get_score_per_pattern(mask_dictionary, mask_size, pattern, pattern_size)
                    pattern_score += result[0]
                    self.is_five_in_a_row = self.is_five_in_a_row if not result[1] else True
                self.score += pattern_score
                pattern_score_hashtable[hash_value] = (pattern_score, self.is_five_in_a_row)
        return self.score, self.is_five_in_a_row

    def get_score_per_pattern(self, mask_dictionary, mask_size, pattern, pattern_size) -> (int, bool):
        score = 0
        is_five_in_a_row = False
        while pattern != 0 and pattern_size >= mask_size:
            small_pattern = pattern % 3**mask_size
            pattern //= 3
            pattern_size -= 1
            for pattern_code, masks in mask_dictionary.items():
                mask_occurrences = masks.count(small_pattern)
                mask_occurrences_2 = masks_2[mask_size][pattern_code].count(small_pattern)
                if pattern_code == Patterns.FIVE_IN_A_ROW and (mask_occurrences > 0 or mask_occurrences_2 > 0):
                    print("IT'S BRITNEY BITCH")
                    is_five_in_a_row = True
                score += PatternsValue[pattern_code] * (mask_occurrences - mask_occurrences_2)
        return score, is_five_in_a_row

    def check_if_over(self, last_move):
        # if self.captures[WHITE] >= 10 or self.captures[BLACK] >= 10:
            # self.is_over = True
            # return
        _, is_five_in_a_row = self.evaluate()
        if not is_five_in_a_row:
            return False
        possible_moves = self.get_possible_moves(None, last_move)
        for possible_move in possible_moves:
            tmp_board = self.copy()
            print(possible_move.position)
            tmp_board.record_new_move(possible_move)
            _, is_five_in_a_row = tmp_board.evaluate()
            # self.undo_move()
            if not is_five_in_a_row:
                return False
        return True

    def copy(self):
        new_board = Board()
        new_board.matrix = self.matrix.copy()
        new_board.move_history = self.move_history.copy()
        new_board.patterns = self.patterns.copy()
        new_board.possible_moves = self.possible_moves.copy() if self.possible_moves is not None else None
        return new_board


def print_board_performance():
    global calls
    print(calls)

def save_hashtables():
    pickle.dump(pattern_score_hashtable, open("pattern_score_hashtable.pickle", "wb"))

def load_hashtables():
    global pattern_score_hashtable
    try:
        pattern_score_hashtable = pickle.load(open("pattern_score_hashtable.pickle", "rb"))
    except FileNotFoundError:
        print("Hmm, pattern_score_hashtable pickle file not found?")
        pattern_score_hashtable = {}

