from __future__ import annotations
from multiprocessing.queues import Queue

import numpy as np
import pickle
import time
from multiprocessing import Process, Queue
from hashlib import sha1
from .move import Move
from .constants import EMPTY, WHITE, BLACK, PATTERN_SIZES, \
                       EMPTY_CAPTURES_DICTIONARY
from .errors import ForbiddenMoveError, ForbiddenMoveError
from .masks import Patterns, PatternsValue, MASKS_WHITE, MASKS_BLACK
# import functools

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
union_manipulation_time = 0

class Board():
    __slots__ = ['matrix', 'possible_moves', 'patterns',
                 'score', 'is_five_in_a_row', 'propagate_possible_moves',
                 'hash_value', 'move', 'captures', 'stats']

    def __init__(self, empty=True):
        if not empty:
            self.matrix = np.zeros((19, 19), dtype=int)
            self.move = None
            self.captures = EMPTY_CAPTURES_DICTIONARY
            self.patterns = [0] * ((19 + 37) * 2)
            self.stats = {
                WHITE: {
                    'scores': [0] * ((19 + 37) * 2),
                    'five_in_a_rows': [False] * ((19 + 37) * 2),
                    'free_threes': [False] * ((19 + 37) * 2),
                },
                BLACK: {
                    'scores': [0] * ((19 + 37) * 2),
                    'five_in_a_rows': [False] * ((19 + 37) * 2),
                    'free_threes': [False] * ((19 + 37) * 2),
                }
            }
            self.possible_moves = None
            self.score = 0
            self.is_five_in_a_row = None
            # self.__init_patterns()
        self.hash_value = None
        self.propagate_possible_moves = True

    # def __init_patterns(self):
    #     self.patterns = ['0' * pattern_size for pattern_size in PATTERN_SIZES]

    def __find_captures(self, move: Move):
        y, x = move.position
        for i in range(-1, 2):
            if y + 3*i < 0 or y + 3*i >= 18:
                continue
            for j in range(-1, 2, 1 if i != 0 else 2):
                if x + 3*j < 0 or x + 3*j >= 18:
                    continue
                if self.matrix[y + i, x + j] == move.opposite_color and \
                   self.matrix[y + 2*i, x + 2*j] == move.opposite_color and \
                   self.matrix[y + 3*i, x + 3*j] == move.color:
                    yield (i, j)

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

        color = move.color if move.color != EMPTY else -move.previous_color

        for index, place in self.__get_pattern_indices_and_places_for_position(y, x):
            self.patterns[index] += color * (3 ** place)
            self.evaluate_pattern(index)

    def evaluate_pattern(self, index):
        self.stats[WHITE]['scores'][index] = self.stats[BLACK]['scores'][index] = 0
        if self.retreive_hashed_pattern_evaluation(index):
            return
        self.actually_evaluate_pattern(index)
        self.save_pattern_evaluation(index)

    def actually_evaluate_pattern(self, index):
        for (mask_size, masks_w), masks_b in zip(MASKS_WHITE.items(), MASKS_BLACK.values()):
            pattern = self.patterns[index]
            pattern_size = PATTERN_SIZES[index]
            while pattern != 0 and pattern_size >= mask_size:
                small_pattern = pattern % (3 ** mask_size)
                if small_pattern != 0:
                    for (pattern_code, masks_list_w), masks_list_b in zip(masks_w.items(), masks_b.values()):
                        total_occ = (small_pattern in masks_list_w) - \
                                    (small_pattern in masks_list_b)
                        if total_occ:
                            color = BLACK if total_occ < 0 else WHITE
                            self.stats[color]['scores'][index] += total_occ * PatternsValue[pattern_code]
                            if pattern_code == Patterns.FIVE_IN_A_ROW:
                                self.stats[color]['five_in_a_rows'][index] = True
                            if pattern_code == Patterns.AX_DEVELOPING_TO_3:
                                self.stats[color]['free_threes'][index] = True
                pattern //= 3
                pattern_size -= 1


    def retreive_hashed_pattern_evaluation(self, index):
        hashval = self.patterns[index], PATTERN_SIZES[index]
        if hashval in pattern_evaluation_hashtable:
            self.stats[WHITE]['scores'][index], \
            self.stats[BLACK]['scores'][index], \
            self.stats[WHITE]['five_in_a_rows'][index], \
            self.stats[BLACK]['five_in_a_rows'][index], \
            self.stats[WHITE]['free_threes'][index], \
            self.stats[BLACK]['free_threes'][index] = pattern_evaluation_hashtable[hashval]
            return True
        return False

    def save_pattern_evaluation(self, index):
        hashval = self.patterns[index], PATTERN_SIZES[index]
        pattern_evaluation_hashtable[hashval] = self.stats[WHITE]['scores'][index], \
            self.stats[BLACK]['scores'][index], \
            self.stats[WHITE]['five_in_a_rows'][index], \
            self.stats[BLACK]['five_in_a_rows'][index], \
            self.stats[WHITE]['free_threes'][index], \
            self.stats[BLACK]['free_threes'][index]

    def __evaluate(self) -> tuple[int, bool]:
        # if self.get_hash() in board_evaluation_hashtable:
        #     _, self.is_five_in_a_row = board_evaluation_hashtable[self.get_hash()]
        #     return
        self.score = sum(self.stats[WHITE]['scores'] + self.stats[BLACK]['scores'])
        self.is_five_in_a_row = any(self.stats[WHITE]['five_in_a_rows'] + self.stats[BLACK]['five_in_a_rows'])
        
        # self.save_evaluation_result()

    def get_captures_score(self):
        return PatternsValue[Patterns.CAPTURE] * \
            (self.captures[WHITE] - self.captures[BLACK])

    def save_evaluation_result(self):
        board_evaluation_hashtable[self.get_hash()] = (self.score, self.is_five_in_a_row)

    def __record_captures(self, move: Move) -> int:
        y, x = move.position
        for i, j in self.__find_captures(move):
            self.captures[move.color] += 1
            capture_position_1 = (y + i, x + j)
            capture_position_2 = (y + 2*i, x + 2*j)
            move.captures.add(capture_position_1)
            move.captures.add(capture_position_2)
            self.matrix[capture_position_1] = EMPTY
            self.matrix[capture_position_2] = EMPTY
            self.__update_patterns(Move(EMPTY, capture_position_1, move.opposite_color))
            self.__update_patterns(Move(EMPTY, capture_position_2, move.opposite_color))

    def record_new_move(self, position, color) -> Board:
        if self.matrix[position] != EMPTY:
            raise ForbiddenMoveError("The cell is already taken you dum-dum.")

        new_board_state = self.__copy()
        new_board_state.matrix[position] = color
        new_board_state.move = Move(color, position)
        new_board_state.__update_patterns(new_board_state.move)
        new_board_state.__record_captures(new_board_state.move)
        new_board_state.__get_possible_moves(self.possible_moves if self.propagate_possible_moves else None)
        new_board_state.__evaluate()

        return new_board_state

    def get_hash(self) -> str:
        if self.hash_value is not None:
            return self.hash_value

        self.hash_value = sha1(self.matrix).hexdigest()
        self.hash_value = self.hash_value + '-' + str(self.captures[WHITE])
        self.hash_value = self.hash_value + '-' + str(self.captures[BLACK])
        return self.hash_value

    def dump(self) -> None:
        global count, total_time, copy_time, matrix_time, \
            patterns_time, possible_moves_time, evaluate_time, \
            get_pos_for_pos, union_manipulation_time
        total_time = copy_time = matrix_time = patterns_time = \
            possible_moves_time = evaluate_time = count = \
            get_pos_for_pos = union_manipulation_time = 0
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
        children = {}
        forbidden_moves = set()
        for possible_move in self.possible_moves:
            try:
                child = self.record_new_move(possible_move, self.move.opposite_color)
                children[possible_move] = child
            except ForbiddenMoveError:
                forbidden_moves.add(possible_move)
        self.possible_moves -= forbidden_moves

        for move, child in sorted(children.items(), key=lambda item: item[1].score, reverse=maximizing):
            yield move, child

    def __get_possible_moves(self, previous_possible_moves) -> None:
        global union_manipulation_time
        if previous_possible_moves:
            y, x = self.move.position
            a = time.time()
            self.possible_moves = {
                (i, j) for i, j in self.get_possible_moves_for_position(y, x)
            }
            b = time.time()
            self.possible_moves = self.possible_moves.union(self.move.captures)
            self.possible_moves = self.possible_moves.union(previous_possible_moves)
            if self.move.position in self.possible_moves:
                self.possible_moves.remove(self.move.position)
        else:
            full_cells_indices = np.transpose(np.array(self.matrix).nonzero())
            a = time.time()
            list_of_sets_of_positions = [ self.get_possible_moves_for_position(i, j) for i, j in full_cells_indices ]
            b = time.time()
            self.possible_moves = set().union(*list_of_sets_of_positions)
        # self.dump()
        # print(self.possible_moves)
        # input()
        union_manipulation_time += (b - a)

    def get_possible_moves_for_position(self, y: int, x: int) -> set[tuple[int]]:
        for i in range(y - 1, y + 2):
            if i < 0 or i > 18:
                continue
            for j in range(x - 1, x + 2, 1 if i != y else 2):
                if j < 0 or j > 18:
                    continue
                if self.matrix[i][j] == EMPTY:
                    yield i, j

    def check_if_over(self):
        if self.captures[WHITE] >= 10 or \
           self.captures[BLACK] >= 10:
            return True
        return self.is_five_in_a_row
        # cant_be_undone = True
        # real_possible_moves = set()
        # for possible_move in self.possible_moves:
        #     try:
        #         new_state = self.record_new_move(possible_move, self.move.opposite_color)
        #     except ForbiddenMoveError:
        #         continue
        #     if not new_state.is_five_in_a_row:
        #         real_possible_moves.add(possible_move)
        #         cant_be_undone = False
        # self.possible_moves = real_possible_moves
        # self.propagate_possible_moves = False
        # return cant_be_undone

    def __copy(self):
        new_board = Board()
        new_board.matrix = self.matrix.copy()
        new_board.captures = self.captures.copy()
        new_board.score = self.score
        new_board.patterns = self.patterns.copy()
        new_board.stats = {
            WHITE: {
                'scores': self.stats[WHITE]['scores'].copy(),
                'five_in_a_rows': self.stats[WHITE]['five_in_a_rows'].copy(),
                'free_threes': self.stats[WHITE]['free_threes'].copy(),
            },
            BLACK: {
                'scores': self.stats[BLACK]['scores'].copy(),
                'five_in_a_rows': self.stats[BLACK]['five_in_a_rows'].copy(),
                'free_threes': self.stats[BLACK]['free_threes'].copy(),
            }
        }
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

