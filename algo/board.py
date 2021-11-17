from __future__ import annotations

import numpy as np
import pickle
import time
from hashlib import sha1
from .move import Move
from .constants import EMPTY, WHITE, BLACK, PATTERN_SIZES, \
                       EMPTY_CAPTURES_DICTIONARY
from .errors import YouAreDumbException
from .masks import MASKS_WHITE, Patterns, PatternsValue, MASKS_BLACK

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

pattern_evaluation_hashtable = {}
small_pattern_evaluation_hashtable = {}
board_evaluation_hashtable = {}
count = 0
time_spent = 0

class Board():
    __slots__ = ['matrix', 'move_history', 'possible_moves', 'patterns',
                 'score', 'is_five_in_a_row', 'captures_history', 'is_over',
                 'previous_possible_moves', 'propagate_possible_moves',
                 'hash_value']

    def __init__(self):
        self.matrix = np.zeros((19, 19), dtype=int)
        self.move_history = []
        self.captures_history = []
        self.patterns = [0] * ((19 + 37) * 2)
        self.possible_moves = None
        self.previous_possible_moves = None
        self.propagate_possible_moves = True
        self.score = None
        self.hash_value = None
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

    def __record_captures(self, move: Move) -> int:
        capture_directions = self.__find_captures(move)
        y, x = move.position
        for i, j in capture_directions:
            capture_move_1 = Move(EMPTY, (y + i, x + j), move.opposite_color)
            capture_move_2 = Move(EMPTY, (y + 2*i, x + 2*j), move.opposite_color)
            move.captures.append(capture_move_1)
            move.captures.append(capture_move_2)
            self.matrix[capture_move_1.position] = EMPTY
            self.matrix[capture_move_2.position] = EMPTY
            self.__update_patterns(capture_move_1)
            self.__update_patterns(capture_move_2)
        new_captures_state = self.captures_history[-1].copy() if len(self.captures_history) else EMPTY_CAPTURES_DICTIONARY
        new_captures_state[move.color] += len(capture_directions)
        self.captures_history.append(new_captures_state)

    def record_new_move(self, move: Move) -> Board:
        global count, time_spent
        a = time.time()
        new_board_state = self.copy()
        b = time.time()
        count += 1
        time_spent += (b - a)

        if new_board_state.matrix[move.position] != EMPTY:
            raise YouAreDumbException("The cell is already taken you dum-dum.")
        new_board_state.matrix[move.position] = move.color
        new_board_state.move_history.append(move)
        new_board_state.__update_patterns(move)
        new_board_state.__record_captures(move)
        new_board_state.evaluate()

        return new_board_state

    def get_hash(self) -> str:
        if self.hash_value is not None:
            return self.hash_value

        self.hash_value = sha1(self.matrix).hexdigest()
        self.hash_value = self.hash_value + '-' + str(self.captures_history[-1][WHITE])
        self.hash_value = self.hash_value + '-' + str(self.captures_history[-1][BLACK])
        return self.hash_value

    def dump(self) -> None:
        global time_spent, count
        print("Copy time: %f, Calls: %d" % (time_spent, count))
        time_spent = count = 0
        index_0_9 = range(10)
        index_10_18 = range(10, 19)
        print('   ' + '  '.join(map(str, index_0_9)) + ' ' + ' '.join(map(str, index_10_18)))
        for index, row in enumerate(self.matrix):
            print(index, end=' ' * (1 if index >= 10 else 2))
            for element in row:
                if element == EMPTY:
                    stone = '+'
                else:
                    stone = '○' if element == BLACK else '●'
                print(stone, end='  ')
            print()

    def get_possible_moves(self) -> list[Move]:
        if self.possible_moves is not None:
            return self.possible_moves
        color = self.move_history[-1].opposite_color
        if self.previous_possible_moves:
            self.previous_possible_moves.remove(self.move_history[-1])
            i, j = self.move_history[-1].position
            possible_moves = self.get_possible_moves_for_position(i, j)
            for old_possible_move in self.previous_possible_moves:
                possible_moves.add(old_possible_move.position)
            for capture in self.move_history[-1].captures:
                possible_moves.add(capture.position)
        else:
            possible_moves = set()
            full_cells_indices = np.transpose(self.matrix.nonzero())
            for full_cell_index in full_cells_indices:
                i, j = tuple(full_cell_index)
                possible_moves_for_position = self.get_possible_moves_for_position(i, j)
                possible_moves = possible_moves.union(possible_moves_for_position)
        self.possible_moves = list(map(lambda possible_move: Move(color, possible_move), possible_moves))
        return self.possible_moves

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

    def evaluate(self) -> tuple[int, bool]:
        if self.score is not None and self.is_five_in_a_row is not None:
            return self.score, self.is_five_in_a_row
        if self.get_hash() in board_evaluation_hashtable:
            self.score, self.is_five_in_a_row = board_evaluation_hashtable[self.get_hash()]
            return self.score, self.is_five_in_a_row

        self.score = self.get_captures_score()
        self.is_five_in_a_row = False
        for pattern_index, pattern in enumerate(self.patterns):
            score, is_five_in_a_row = self.evaluate_pattern(pattern_index, pattern)
            self.score += score
            self.is_five_in_a_row = self.is_five_in_a_row if not is_five_in_a_row else True
        self.save_evaluation_result()
        return self.score, self.is_five_in_a_row

    def get_captures_score(self):
        return PatternsValue[Patterns.CAPTURE] * \
            (self.captures_history[-1][WHITE] - self.captures_history[-1][BLACK])

    def evaluate_pattern(self, pattern_index, original_pattern):
        score = 0
        is_five_in_a_row = False
        hash_value = hash((original_pattern, PATTERN_SIZES[pattern_index]))
        if hash_value not in pattern_evaluation_hashtable:
            for mask_size in MASKS_WHITE.keys():
                pattern = original_pattern
                pattern_size = PATTERN_SIZES[pattern_index]
                while pattern != 0:
                    if pattern_size < mask_size:
                        break
                    small_pattern = pattern % 3**mask_size
                    small_score, small_is_five_in_a_row = self.evaluate_small_pattern(small_pattern, mask_size)
                    score += small_score
                    is_five_in_a_row = is_five_in_a_row if not small_is_five_in_a_row else True
                    pattern //= 3
                    pattern_size -= 1
            pattern_evaluation_hashtable[hash_value] = (score, is_five_in_a_row)
        score, is_five_in_a_row = pattern_evaluation_hashtable[hash_value]
        return score, is_five_in_a_row

    def evaluate_small_pattern(self, small_pattern, mask_size):
        small_hash_value = hash((small_pattern, mask_size))
        if small_hash_value in small_pattern_evaluation_hashtable:
            score, is_five_in_a_row = small_pattern_evaluation_hashtable[small_hash_value]
        else:
            score = 0
            is_five_in_a_row = False
            for pattern_code in MASKS_WHITE[mask_size].keys():
                total_occurrences = (small_pattern in MASKS_WHITE[mask_size][pattern_code]) - \
                                    (small_pattern in MASKS_BLACK[mask_size][pattern_code])
                score += PatternsValue[pattern_code] * total_occurrences
                if pattern_code == Patterns.FIVE_IN_A_ROW and total_occurrences != 0:
                    is_five_in_a_row = True
            small_pattern_evaluation_hashtable[small_hash_value] = (score, is_five_in_a_row)
        return score, is_five_in_a_row

    def save_evaluation_result(self):
        board_evaluation_hashtable[self.get_hash()] = (self.score, self.is_five_in_a_row)

    def check_if_over(self):
        if self.captures_history[-1][WHITE] >= 10 or \
           self.captures_history[-1][BLACK] >= 10:
            return True
        if not self.is_five_in_a_row:
            return False
        possible_moves = self.get_possible_moves()
        cant_be_undone = True
        real_possible_moves = []
        for possible_move in possible_moves:
            new_state = self.record_new_move(possible_move)
            if not new_state.is_five_in_a_row:
                real_possible_moves.append(possible_move)
                cant_be_undone = False
        self.possible_moves = real_possible_moves
        self.propagate_possible_moves = False
        return cant_be_undone

    def copy(self):
        new_board = Board()
        new_board.matrix = self.matrix.copy()
        new_board.move_history = self.move_history.copy()
        new_board.patterns = self.patterns.copy()
        new_board.captures_history = self.captures_history.copy()
        if self.possible_moves is not None and self.propagate_possible_moves:
            new_board.previous_possible_moves = self.possible_moves.copy()
        else:
            new_board.previous_possible_moves = None
        return new_board


def save_hashtables():
    pickle.dump(pattern_evaluation_hashtable, open("pattern_evaluation_hashtable.pickle", "wb"))
    pickle.dump(small_pattern_evaluation_hashtable, open("small_pattern_evaluation_hashtable.pickle", "wb"))
    pickle.dump(board_evaluation_hashtable, open("board_evaluation_hashtable.pickle", "wb"))

def load_hashtables():
    global pattern_evaluation_hashtable, small_pattern_evaluation_hashtable, board_evaluation_hashtable
    try:
        pattern_evaluation_hashtable = pickle.load(open("pattern_evaluation_hashtable.pickle", "rb"))
    except FileNotFoundError:
        print("Hmm, pattern_evaluation_hashtable pickle file not found?")
        pattern_evaluation_hashtable = {}
    try:
        board_evaluation_hashtable = pickle.load(open("board_evaluation_hashtable.pickle", "rb"))
    except FileNotFoundError:
        print("Hmm, board_evaluation_hashtable pickle file not found?")
        board_evaluation_hashtable = {}
    try:
        small_pattern_evaluation_hashtable = pickle.load(open("small_pattern_evaluation_hashtable.pickle", "rb"))
    except FileNotFoundError:
        print("Hmm, small_pattern_evaluation_hashtable pickle file not found?")
        small_pattern_evaluation_hashtable = {}

