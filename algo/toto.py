from __future__ import annotations

import numpy as np
import pickle
import time
from hashlib import new, sha1
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
            self.patterns_scores = [(0, False)] * ((19 + 37) * 2)
            self.possible_moves = None
            self.score = 0
            self.hash_value = None
            self.is_five_in_a_row = None
            self.__init_patterns()
        self.propagate_possible_moves = True

    def __init_patterns(self):
        self.patterns = ['0' * pattern_size for pattern_size in PATTERN_SIZES]
        print(self.patterns)
        input()

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

        color = move.color

        # if move.color == EMPTY:
            # undo = not undo
            # color = move.previous_color
        # else:
            # color = move.color
        # color = -color if undo else color

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

        self.patterns[row_i] = self.patterns[row_i][:18 - x] + str(color) + self.patterns[row_i][18 - x + 1:]
        self.patterns[column_i] = self.patterns[column_i][:18 - y] + str(color) + self.patterns[column_i][18 - y + 1:]
        self.patterns[main_diag_i] = self.patterns[main_diag_i][:main_diagonal_power] + str(color) + self.patterns[main_diag_i][main_diagonal_power + 1:]
        self.patterns[secondary_diag_i] = self.patterns[secondary_diag_i][:secondary_diagonal_power] + str(color) + self.patterns[secondary_diag_i][secondary_diagonal_power + 1:]

        self.patterns_scores[row_i] = self.evaluate_pattern(row_i, self.patterns[row_i])
        self.patterns_scores[column_i] = self.evaluate_pattern(column_i, self.patterns[column_i])
        self.patterns_scores[main_diag_i] = self.evaluate_pattern(main_diag_i, self.patterns[main_diag_i])
        self.patterns_scores[secondary_diag_i] = self.evaluate_pattern(secondary_diag_i, self.patterns[secondary_diag_i])

        self.score += (self.patterns_scores[row_i][0] + \
                       self.patterns_scores[column_i][0] + \
                       self.patterns_scores[main_diag_i][0] + \
                       self.patterns_scores[secondary_diag_i][0])


    def evaluate_pattern(self, pattern_index, pattern):
        score = 0
        is_five_in_a_row = False
        hash_value = hash((pattern, PATTERN_SIZES[pattern_index]))
        if hash_value not in pattern_evaluation_hashtable:
            for (pattern_code, masks_white), masks_black in zip(MASKS_WHITE.items(), MASKS_BLACK.values()):
                    occurrences_white = sum(pattern.count(x) for x in masks_white)
                    occurrences_black = sum(pattern.count(x) for x in masks_black)
                    occurrences_diff = occurrences_white - occurrences_black
                    occurrences_sum = occurrences_white + occurrences_black
                    score += PatternsValue[pattern_code] * occurrences_diff
                    if pattern_code == Patterns.FIVE_IN_A_ROW and occurrences_sum != 0:
                        is_five_in_a_row = True
                # pattern = original_pattern
                # pattern_size = PATTERN_SIZES[pattern_index]
                # while pattern != 0:
                #     if pattern_size < mask_size:
                #         break
                #     small_pattern = pattern % 3**mask_size
                #     small_score, small_is_five_in_a_row = self.evaluate_small_pattern(small_pattern, mask_size)
                #     score += small_score
                #     is_five_in_a_row = is_five_in_a_row if not small_is_five_in_a_row else True
                #     pattern //= 3
                #     pattern_size -= 1
            pattern_evaluation_hashtable[hash_value] = (score, is_five_in_a_row)
        score, is_five_in_a_row = pattern_evaluation_hashtable[hash_value]
        return score, is_five_in_a_row
