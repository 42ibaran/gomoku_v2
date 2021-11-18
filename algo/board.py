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
    __slots__ = ['matrix', 'possible_moves', 'patterns',
                 'score', 'is_five_in_a_row',
                 'propagate_possible_moves',
                 'hash_value', 'move', 'captures', 'patterns_scores']

    def __init__(self, empty=True):
        if not empty:
            self.matrix = np.zeros((19, 19), dtype=int)
            self.move = None
            self.captures = EMPTY_CAPTURES_DICTIONARY
            self.patterns = [0] * ((19 + 37) * 2)
            self.patterns_scores = [(0, False)] * ((19 + 37) * 2)
            self.possible_moves = None
            self.score = 0
            self.is_five_in_a_row = None
            # self.__init_patterns()
        self.hash_value = None
        self.propagate_possible_moves = True

    # def __init_patterns(self):
    #     self.patterns = ['0' * pattern_size for pattern_size in PATTERN_SIZES]

    def __find_captures(self, move: Move) -> list[tuple[int]]:
        capture_directions = set()
        y, x = move.position
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (y + 3*i < 0 or x + 3*j < 0) or \
                    (y + 3*i >= 18 or x + 3*j >= 18): 
                    continue
                if self.matrix[y + i][x + j] == move.opposite_color and \
                   self.matrix[y + 2*i][x + 2*j] == move.opposite_color and \
                   self.matrix[y + 3*i][x + 3*j] == move.color:
                    capture_directions.add((i, j))
        return capture_directions

    def __update_patterns(self, move: Move) -> None:
        y, x = move.position

        undo = False
        if move.color == EMPTY:
            undo = True
            color = move.previous_color
        else:
            color = move.color
        color = -color if undo else color

        main_diagonal_power = 18 - max(x, y)
        secondary_diagonal_power = 18 - max(18 - y, x)

        row_i = PATTERN_ROW + y
        column_i = PATTERN_COLUMN + x
        main_diag_i = PATTERN_MAIN_DIAG + 18 + x - y
        secondary_diag_i = PATTERN_SECONDARY_DIAG + x + y

        self.score -= (self.patterns_scores[row_i][0] + \
                       self.patterns_scores[column_i][0] + \
                       self.patterns_scores[main_diag_i][0] + \
                       self.patterns_scores[secondary_diag_i][0])

        self.patterns[row_i] += color * (3 ** (18 - x))
        self.patterns[column_i] += color * (3 ** (18 - y))
        self.patterns[main_diag_i] += color * (3 ** main_diagonal_power)
        self.patterns[secondary_diag_i] += color * (3 ** secondary_diagonal_power)

        self.patterns_scores[row_i] = self.evaluate_pattern(row_i, self.patterns[row_i])
        self.patterns_scores[column_i] = self.evaluate_pattern(column_i, self.patterns[column_i])
        self.patterns_scores[main_diag_i] = self.evaluate_pattern(main_diag_i, self.patterns[main_diag_i])
        self.patterns_scores[secondary_diag_i] = self.evaluate_pattern(secondary_diag_i, self.patterns[secondary_diag_i])

        self.score += (self.patterns_scores[row_i][0] + \
                       self.patterns_scores[column_i][0] + \
                       self.patterns_scores[main_diag_i][0] + \
                       self.patterns_scores[secondary_diag_i][0])

    def evaluate(self) -> tuple[int, bool]:
        if self.get_hash() in board_evaluation_hashtable:
            _, self.is_five_in_a_row = board_evaluation_hashtable[self.get_hash()]
            return
        self.is_five_in_a_row = any([is_five_in_a_row for _, is_five_in_a_row in self.patterns_scores])
        self.save_evaluation_result()

    def get_captures_score(self):
        return PatternsValue[Patterns.CAPTURE] * \
            (self.captures[WHITE] - self.captures[BLACK])

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

    # def __update_patterns(self, move: Move) -> None:
    #     y, x = move.position
    #     color = move.color

    #     # if move.color == EMPTY:
    #         # undo = not undo
    #         # color = move.previous_color
    #     # else:
    #         # color = move.color
    #     # color = -color if undo else color

    #     main_diagonal_power = 18 - max(x, y)
    #     secondary_diagonal_power = 18 - max(18 - y, x)

    #     row_i = PATTERN_ROW + y
    #     column_i = PATTERN_COLUMN + x
    #     main_diag_i = PATTERN_MAIN_DIAG + 18 + x - y
    #     secondary_diag_i = PATTERN_SECONDARY_DIAG + x + y

    #     self.score -= (self.patterns_scores[row_i][0] + \
    #                     self.patterns_scores[column_i][0] + \
    #                     self.patterns_scores[main_diag_i][0] + \
    #                     self.patterns_scores[secondary_diag_i][0])

    #     self.patterns[row_i] = self.patterns[row_i][:18 - x] + str(color) + self.patterns[row_i][18 - x + 1:]
    #     self.patterns[column_i] = self.patterns[column_i][:18 - y] + str(color) + self.patterns[column_i][18 - y + 1:]
    #     self.patterns[main_diag_i] = self.patterns[main_diag_i][:main_diagonal_power] + str(color) + self.patterns[main_diag_i][main_diagonal_power + 1:]
    #     self.patterns[secondary_diag_i] = self.patterns[secondary_diag_i][:secondary_diagonal_power] + str(color) + self.patterns[secondary_diag_i][secondary_diagonal_power + 1:]

    #     self.patterns_scores[row_i] = self.evaluate_pattern(row_i, self.patterns[row_i])
    #     self.patterns_scores[column_i] = self.evaluate_pattern(column_i, self.patterns[column_i])
    #     self.patterns_scores[main_diag_i] = self.evaluate_pattern(main_diag_i, self.patterns[main_diag_i])
    #     self.patterns_scores[secondary_diag_i] = self.evaluate_pattern(secondary_diag_i, self.patterns[secondary_diag_i])

    #     self.score += (self.patterns_scores[row_i][0] + \
    #                     self.patterns_scores[column_i][0] + \
    #                     self.patterns_scores[main_diag_i][0] + \
    #                     self.patterns_scores[secondary_diag_i][0])

    # def evaluate_pattern(self, pattern_index, pattern):
    #     score = 0
    #     is_five_in_a_row = False
    #     hash_value = hash((pattern, PATTERN_SIZES[pattern_index]))
    #     if hash_value not in pattern_evaluation_hashtable:
    #         for (pattern_code, masks_white), masks_black in zip(MASKS_WHITE.items(), MASKS_BLACK.values()):
    #                 occurrences_white = sum(pattern.count(x) for x in masks_white)
    #                 occurrences_black = sum(pattern.count(x) for x in masks_black)
    #                 occurrences_diff = occurrences_white - occurrences_black
    #                 occurrences_sum = occurrences_white + occurrences_black
    #                 score += PatternsValue[pattern_code] * occurrences_diff
    #                 if pattern_code == Patterns.FIVE_IN_A_ROW and occurrences_sum != 0:
    #                     is_five_in_a_row = True
    #         pattern_evaluation_hashtable[hash_value] = (score, is_five_in_a_row)
    #     score, is_five_in_a_row = pattern_evaluation_hashtable[hash_value]
    #     return score, is_five_in_a_row

    def __record_captures(self, move: Move) -> int:
        capture_directions = self.__find_captures(move)
        y, x = move.position
        for i, j in capture_directions:
            capture_position_1 = (y + i, x + j)
            capture_position_2 = (y + 2*i, x + 2*j)
            move.captures.add(capture_position_1)
            move.captures.add(capture_position_2)
            self.matrix[capture_position_1] = EMPTY
            self.matrix[capture_position_2] = EMPTY
            self.__update_patterns(Move(EMPTY, capture_position_1, move.opposite_color))
            self.__update_patterns(Move(EMPTY, capture_position_2, move.opposite_color))
        self.captures[move.color] += len(capture_directions)

    def record_new_move(self, position, color) -> Board:
        global count, time_spent
        new_board_state = self.copy()

        if new_board_state.matrix[position] != EMPTY:
            raise YouAreDumbException("The cell is already taken you dum-dum.")
        new_board_state.matrix[position] = color
        new_board_state.move = Move(color, position)
        
        new_board_state.__update_patterns(new_board_state.move)
        a = time.time()
        new_board_state.__record_captures(new_board_state.move)
        b = time.time()
        count += 1
        time_spent += (b - a)

        new_board_state.__get_possible_moves(self.possible_moves if self.propagate_possible_moves else None)
        
        new_board_state.evaluate()

        return new_board_state

    def get_hash(self) -> str:
        if self.hash_value is not None:
            return self.hash_value

        self.hash_value = sha1(self.matrix).hexdigest()
        self.hash_value = self.hash_value + '-' + str(self.captures[WHITE])
        self.hash_value = self.hash_value + '-' + str(self.captures[BLACK])
        return self.hash_value

    def dump(self) -> None:
        global time_spent, count
        print("__record_captures time: %f, Calls: %d" % (time_spent, count))
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

    def __get_possible_moves(self, previous_possible_moves) -> None:
        if previous_possible_moves:
            i, j = self.move.position
            self.possible_moves = self.get_possible_moves_for_position(i, j)
            self.possible_moves = self.possible_moves.union(self.move.captures)
            self.possible_moves = self.possible_moves.union(previous_possible_moves)
            if self.move.position in self.possible_moves:
                self.possible_moves.remove(self.move.position)
        else:
            full_cells_indices = np.transpose(self.matrix.nonzero())
            list_of_sets_of_positions = [ self.get_possible_moves_for_position(i, j) for i, j in full_cells_indices ]
            self.possible_moves = set().union(*list_of_sets_of_positions)

    def order_children_by_score(self, maximizing):
        possible_move_scores = {}
        for possible_move in self.possible_moves:
            new_state = self.record_new_move(possible_move, self.move.opposite_color)
            possible_move_scores[possible_move] = new_state.score
        for key, _ in sorted(possible_move_scores.items(), key=lambda x: x[1], reverse=maximizing):
            yield key

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

    def check_if_over(self):
        if self.captures[WHITE] >= 10 or \
           self.captures[BLACK] >= 10:
            return True
        if not self.is_five_in_a_row:
            return False
        cant_be_undone = True
        real_possible_moves = set()
        for possible_move in self.possible_moves:
            new_state = self.record_new_move(possible_move, self.move.opposite_color)
            if not new_state.is_five_in_a_row:
                real_possible_moves.add(possible_move)
                cant_be_undone = False
        self.possible_moves = real_possible_moves
        self.propagate_possible_moves = False
        return cant_be_undone

    def copy(self):
        new_board = Board()
        new_board.matrix = self.matrix.copy()
        new_board.captures = self.captures.copy()
        new_board.score = self.score
        new_board.patterns = self.patterns.copy()
        new_board.patterns_scores = self.patterns_scores.copy()
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

