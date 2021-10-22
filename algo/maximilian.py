from __future__ import annotations

import numpy as np
import time
from typing import Union
from collections import Counter
from algo.move import Move
from algo.board import Board
from algo.constants import WHITE, BLACK, EMPTY_CAPTURES_DICTIONARY
from algo.masks import MASKS, BLOCKING_PATTERN_CODE_CONVERTION, Patterns, PatternsValue, masks_2

hash_dictionary = {}

class MinMaxNode():
    __slots__ = ['board', 'move', 'captures', 'score', 'patterns', 'children', 
                 'alpha', 'beta', 'maximizing', 'remaining_depth', 'possible_moves',
                 'game_over']

    def __init__(self, board: Board, move: Move, captures: dict,
                 alpha: Union[int, float], beta: Union[int, float],
                 maximizing: bool, remaining_depth: int = 5):
        self.board = board
        self.move = move
        self.captures = captures
        self.score = float('-inf') if maximizing else float('inf')
        self.patterns = self.board.get_list_of_patterns(self.move)
        self.alpha = alpha
        self.beta = beta
        self.maximizing = maximizing
        self.remaining_depth = remaining_depth
        self.game_over = self.is_game_over()
        self.possible_moves = None
        self.children = {}
        
        if remaining_depth == 0 or self.game_over:
            # self.board.dump()
            # input()
            self.evaluate()
            return

        self.perform_minmax()

    def perform_minmax(self):
        if self.possible_moves is None:
            self.possible_moves = self.board.get_possible_moves(self.move.get_opposite_color())
        for possible_move in self.possible_moves:
            if possible_move.position in self.children.keys():
                child = self.children[possible_move]
                child.move = possible_move
                child.update_with_depth(self.alpha, self.beta,
                                        not self.maximizing, self.remaining_depth - 1)
            else:
                child = self.add_child(possible_move)
            if self.maximizing:
                self.score = max(self.score, child.score)
                self.alpha = max(self.alpha, child.score)
                if self.beta <= self.alpha:
                    break
            else:
                self.score = min(self.score, child.score)
                self.beta = min(self.beta, child.score)
                if self.beta <= self.alpha:
                    break

    def add_child(self, move) -> MinMaxNode:
        captures_count = self.board.record_new_move(move)
        child_captures = self.captures.copy()
        child_captures[move.color] += captures_count

        child, hash_value = retrieve_node_from_hashtable(self.board, move, child_captures)
        if child is None:
            child = MinMaxNode(self.board, move, child_captures,
                               self.alpha, self.beta, not self.maximizing,
                               self.remaining_depth - 1)
            hash_dictionary[hash_value] = child
        else:
            child.move = move
            child.update_with_depth(self.alpha, self.beta,
                                    not self.maximizing, self.remaining_depth - 1)
        self.children[move] = child
        self.board.undo_move()

        return child

    def update_as_root(self, remaining_depth: int = 5):
        if self.game_over:
            return
        self.alpha = float('-inf')
        self.beta = float('inf')
        self.maximizing = False
        self.score = float('-inf') if self.maximizing else float('inf')
        self.remaining_depth = remaining_depth
        self.perform_minmax()

    def update_with_depth(self, alpha, beta, maximizing, remaining_depth):
        if remaining_depth == self.remaining_depth or self.game_over:
            return
        self.alpha = alpha
        self.beta = beta
        self.maximizing = maximizing
        self.score = float('-inf') if self.maximizing else float('inf')
        self.remaining_depth = remaining_depth
        self.perform_minmax()

    def is_game_over(self):
        if 10 in self.captures.values():
            return True
        for pattern in self.patterns:
            while pattern != 0:
                small_pattern = pattern % 3**5
                pattern //= 3
                if small_pattern == 0x79 or small_pattern == 0xf2:
                    return True
        return False

    def dump(self):
        self.board.dump()
        print("Color: ", self.move.color, sep="")
        print("Position: ", self.move.position, sep="")
        print("Score: ", self.score, sep="")
        print("Children:")
        for child in self.children.values():
            child.board.dump()
            print("\tColor: ", child.move.color, sep="")
            print("\tPosition: ", child.move.position, sep="")
            print("\tScore: ", child.score, sep="", end="\n\n")
        print("=========")

    def evaluate(self) -> None:
        self.score = 0
        # patterns = self.board.get_list_of_patterns(self.move)
        # self.score = PatternsValue[Patterns.CAPTURE] \
            # * (self.captures[self.move.color] \
            # - self.captures[self.move.get_opposite_color()])
        # print(self.patterns)
        # input()
        for mask_length, mask_dictionary in MASKS.items():
            for pattern in self.patterns:
                while pattern != 0:
                    small_pattern = pattern % 3**mask_length
                    pattern //= 3
                    for pattern_code, masks in mask_dictionary.items():
                        mask_occurrences = masks.count(small_pattern)
                        mask_occurrences_2 = masks_2[mask_length][pattern_code].count(small_pattern)
                        # print(small_pattern)
                        # print(pattern_code)
                        # print(mask_occurrences)
                        # input()
                        self.score += PatternsValue[pattern_code] * (mask_occurrences - mask_occurrences_2)
        # self.board.dump()
        # print(self.score)
        # input()

        # blocking_patterns = self.convert_patterns_to_blocking(self.patterns)
        # for size, mask_dictionary in MASKS.items():
        #     small_patterns = self.divide_patterns_by_size(self.patterns, size)
        #     small_blocking_patterns = self.divide_patterns_by_size(blocking_patterns, size)
        #     for pattern_code, masks in mask_dictionary.items():
        #         matches = small_patterns.intersection(masks)
        #         count_matches = len(matches)
        #         self.score += PatternsValue[pattern_code] * count_matches
                
        #         blocking_matches = small_blocking_patterns.intersection(masks)
        #         count_blocking_matches = len(blocking_matches)
        #         blocking_pattern_code = BLOCKING_PATTERN_CODE_CONVERTION[pattern_code]
        #         self.score += PatternsValue[blocking_pattern_code] * count_blocking_matches
    
    def get_best_move(self) -> Move:
        best_child = None
        best_score = float('-inf') if self.maximizing else float('inf')
        for child in self.children.values():
            if (self.maximizing and child.score > best_score) \
                    or (not self.maximizing and child.score < best_score):
                best_child = child
                best_score = child.score
        return best_child.move, best_score

    def convert_patterns_to_blocking(self, patterns):
        blocking_patterns = []
        for pattern, index in patterns:
            pattern = -pattern
            pattern[index] = 1
            blocking_patterns.append((pattern, index))
        return blocking_patterns

    @staticmethod
    def divide_patterns_by_size(patterns, size):
        small_patterns = set()

        for pattern, index in patterns:
            opponent_indices = np.where(pattern == -1)[0]
            left_boundary = max(
                0,
                max(opponent_indices[opponent_indices < index]) + 1 if any(opponent_indices < index) else 0,
                index - (size - 1)
            )
            right_boundary = min(
                len(pattern) - 1,
                min(opponent_indices[opponent_indices > index]) - 1 if any(opponent_indices > index) else len(pattern) - 1,
                index + (size - 1)
            )
            new_pattern = pattern[left_boundary:right_boundary + 1].tolist()

            for i in range(len(new_pattern) - size + 1):
                binary = int(''.join(map(str, new_pattern[i:i + size])), 2)
                small_patterns.add(binary)

        return small_patterns


def retrieve_node_from_hashtable(board: Board, last_move: Move, captures: dict) -> (Union[MinMaxNode, None], str):
    hash_value = board.get_hash()
    hash_value = hash_value + '-' + str(captures[WHITE]) + '-' + str(captures[BLACK])
    if hash_value in hash_dictionary.keys():
        return hash_dictionary[hash_value], hash_value
    return None, hash_value


class Maximilian():
    @staticmethod
    def get_next_move(board: Board, last_move: Move, captures: dict) -> Move:
        root, hash_value = retrieve_node_from_hashtable(board, last_move, captures.copy())
        if root is None:
            print("Creating new node.")
            root = MinMaxNode(board, last_move, captures.copy(), float('-inf'), float('inf'), False)
            hash_dictionary[hash_value] = root
        else:
            print("Got node from hashtable. Updating.")
            root.update_as_root()
        move, score = root.get_best_move()
        print(score)
        root.dump()
        return move
