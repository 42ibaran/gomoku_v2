from __future__ import annotations

import numpy as np
import pickle
import time
from hashlib import sha1
from .move import Move
from .constants import EMPTY, WHITE, BLACK, PATTERN_SIZES, \
                       EMPTY_CAPTURES_DICTIONARY
from .errors import ForbiddenMoveError, ForbiddenMoveError
from .masks import MASKS_WHITE, MASKS_BLACK, Patterns, PatternsValue

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
total_time = 0
copy_time = 0
matrix_time = 0
patterns_time = 0
possible_moves_time = 0
evaluate_time = 0
get_pos_for_pos = 0

class Board():
    __slots__ = ['matrix', 'possible_moves', 'patterns',
                 'score', 'is_five_in_a_row',
                 'propagate_possible_moves',
                 'hash_value', 'move', 'captures', 'patterns_scores', 'patterns_fir']

    def __init__(self, empty=True):
        if not empty:
            self.matrix = np.zeros((19, 19), dtype=int)
            self.move = None
            self.captures = EMPTY_CAPTURES_DICTIONARY
            self.patterns = [0] * ((19 + 37) * 2)
            self.patterns_scores = [0] * ((19 + 37) * 2)
            self.patterns_fir = [False] * ((19 + 37) * 2)
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

    @staticmethod
    def __get_pattern_indices_and_places_for_position(y, x):
        main_diagonal_power = 18 - max(x, y)
        secondary_diagonal_power = 18 - max(18 - y, x)

        return [
            (PATTERN_ROW + y, 18 - x),
            (PATTERN_COLUMN + x, 18 - y),
            (PATTERN_MAIN_DIAG + 18 + x - y, main_diagonal_power),
            (PATTERN_SECONDARY_DIAG + x + y, secondary_diagonal_power),
        ]

    def __update_patterns(self, move: Move) -> None:
        y, x = move.position

        undo = False
        if move.color == EMPTY:
            undo = True
            color = move.previous_color
        else:
            color = move.color
        color = -color if undo else color

        count_free_threes = 0
        for index, place in self.__get_pattern_indices_and_places_for_position(y, x):
            self.patterns[index] += color * (3 ** place)
            self.patterns_scores[index], self.patterns_fir[index], pattern_free_three = self.evaluate_pattern(index)
            count_free_threes += pattern_free_three

        if move.color != EMPTY:
            if count_free_threes > 1:
                raise ForbiddenMoveError("Double free three.")
        
        self.score = sum(self.patterns_scores)

    def evaluate(self) -> tuple[int, bool]:
        # if self.get_hash() in board_evaluation_hashtable:
        #     _, self.is_five_in_a_row = board_evaluation_hashtable[self.get_hash()]
        #     return
        self.is_five_in_a_row = any(self.patterns_fir)
        # self.save_evaluation_result()

    def get_captures_score(self):
        return PatternsValue[Patterns.CAPTURE] * \
            (self.captures[WHITE] - self.captures[BLACK])

    def evaluate_pattern(self, pattern_index):
        original_pattern = self.patterns[pattern_index]
        score = 0
        is_five_in_a_row = False
        hash_value = (original_pattern, PATTERN_SIZES[pattern_index])
        all_free_threes = False
        if hash_value in pattern_evaluation_hashtable:
            score, is_five_in_a_row, all_free_threes = pattern_evaluation_hashtable[hash_value]
        else:
            for (mask_size, patterns_white), patterns_black in zip(MASKS_WHITE.items(), MASKS_BLACK.values()):
                pattern = original_pattern
                pattern_size = PATTERN_SIZES[pattern_index]
                while pattern != 0:
                    if pattern_size < mask_size:
                        break
                    small_pattern = pattern % 3**mask_size
                    small_score, small_is_five_in_a_row, small_is_free_three = self.evaluate_small_pattern(small_pattern, mask_size, patterns_white, patterns_black)
                    score += small_score
                    is_five_in_a_row += small_is_five_in_a_row
                    all_free_threes += small_is_free_three
                    pattern //= 3
                    pattern_size -= 1
            pattern_evaluation_hashtable[hash_value] = (score, bool(is_five_in_a_row), bool(all_free_threes))
        return score, bool(is_five_in_a_row), bool(all_free_threes)

    def evaluate_small_pattern(self, small_pattern, mask_size, patterns_white, patterns_black):
        small_hash_value = (small_pattern, mask_size)
        if small_hash_value in small_pattern_evaluation_hashtable:
            score, is_five_in_a_row, is_free_three = small_pattern_evaluation_hashtable[small_hash_value]
        else:
            score = 0
            is_five_in_a_row = False
            is_free_three = False
            for (pattern_code, masks_white), masks_black in zip(patterns_white.items(), patterns_black.values()):
                total_occurrences = (small_pattern in masks_white) - \
                                    (small_pattern in masks_black)
                score += PatternsValue[pattern_code] * total_occurrences
                if pattern_code == Patterns.FIVE_IN_A_ROW and total_occurrences != 0:
                    is_five_in_a_row = True
                if pattern_code == Patterns.AX_DEVELOPING_TO_3 and total_occurrences != 0:
                    is_free_three = True
            small_pattern_evaluation_hashtable[small_hash_value] = (score, is_five_in_a_row, is_free_three)
        return score, is_five_in_a_row, is_free_three

    def save_evaluation_result(self):
        board_evaluation_hashtable[self.get_hash()] = (self.score, self.is_five_in_a_row)

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
        global count, total_time, copy_time, matrix_time, patterns_time, possible_moves_time, evaluate_time
        a = time.time()
        new_board_state = self.copy()
        c = time.time()

        try:
            if new_board_state.matrix[position] != EMPTY:
                raise ForbiddenMoveError("The cell is already taken you dum-dum.")
        except ValueError:
            print(position)
            input()

        new_board_state.matrix[position] = color
        d = time.time()

        new_board_state.move = Move(color, position)
        
        new_board_state.__update_patterns(new_board_state.move)
        new_board_state.__record_captures(new_board_state.move)
        e = time.time()

        new_board_state.__get_possible_moves(self.possible_moves if self.propagate_possible_moves else None)
        f = time.time()
        
        new_board_state.evaluate()
        g = time.time()

        h = time.time()
        total_time += (h - a)
        copy_time += (c - a)
        matrix_time += (d - c)
        patterns_time += (e - d)
        possible_moves_time += (f - e)
        evaluate_time += (g - f)
        count += 1
        return new_board_state

    def get_hash(self) -> str:
        if self.hash_value is not None:
            return self.hash_value

        self.hash_value = sha1(self.matrix).hexdigest()
        self.hash_value = self.hash_value + '-' + str(self.captures[WHITE])
        self.hash_value = self.hash_value + '-' + str(self.captures[BLACK])
        return self.hash_value

    def dump(self) -> None:
        global count, total_time, copy_time, matrix_time, patterns_time, possible_moves_time, evaluate_time, get_pos_for_pos
        print("New move time: %f, calls: %d" % (total_time, count))
        print("Copy time: %f" % (copy_time))
        print("Matrix time: %f" % (matrix_time))
        print("Patterns time: %f" % (patterns_time))
        print("Possible moves time: %f" % (possible_moves_time))
        print("Evaluate time: %f" % (evaluate_time))
        print("PosPos time: %f" % (get_pos_for_pos))
        total_time = copy_time = matrix_time = patterns_time = possible_moves_time = evaluate_time = count = get_pos_for_pos = 0
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

    def order_children_by_score(self, maximizing):
        possible_move_scores = {}
        forbidden_moves = set()
        for possible_move in self.possible_moves:
            try:
                new_state = self.record_new_move(possible_move, self.move.opposite_color)
            except ForbiddenMoveError:
                forbidden_moves.add(possible_move)
                continue
            possible_move_scores[possible_move] = new_state.score
        self.possible_moves -= forbidden_moves
        for key, _ in sorted(possible_move_scores.items(), key=lambda x: x[1], reverse=maximizing):
            yield key

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

    def get_possible_moves_for_position(self, i: int, j: int) -> set[tuple[int]]:
        global get_pos_for_pos
        a = time.time()
        possible_moves = set()
        for i_delta in range(-1, 2):
            for j_delta in range(-1, 2):
                if i_delta == j_delta == 0 \
                        or i + i_delta < 0 or i + i_delta > 18 \
                        or j + j_delta < 0 or j + j_delta > 18 :
                    continue
                if self.matrix[i + i_delta, j + j_delta] == EMPTY:
                    possible_moves.add((i + i_delta, j + j_delta))
        b = time.time()
        get_pos_for_pos += (b - a)
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
            try:
                new_state = self.record_new_move(possible_move, self.move.opposite_color)
            except ForbiddenMoveError:
                continue
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
        new_board.patterns_fir = self.patterns_fir.copy()
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

