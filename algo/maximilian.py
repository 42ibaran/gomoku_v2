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

time_possible_moves = 0
count_possible_moves = 0

time_evaluate = 0
count_evaluate = 0

time_constructor = 0
count_constructor = 0

time_get_patterns = 0
count_get_patterns = 0

time_game_over = 0
count_game_over = 0

time_hash = 0
count_hash = 0


class MinMaxNode():
    __slots__ = ['board', 'move', 'captures', 'score', 'patterns', 'children', 
                 'alpha', 'beta', 'maximizing', 'remaining_depth', 'possible_moves',
                 'parent', 'game_over']

    def __init__(self, board: Board, move: Move, captures: dict,
                 alpha: Union[int, float], beta: Union[int, float],
                 maximizing: bool, parent: MinMaxNode = None, remaining_depth: int = 5):
        ### PERFORMANCE EVAL
        global time_constructor, count_constructor, time_get_patterns, count_get_patterns, time_game_over, count_game_over
        a = time.time()

        self.board = board
        self.move = move
        self.captures = captures
        self.score = float('-inf') if maximizing else float('inf')

        c = time.time()
        self.patterns = self.board.get_list_of_patterns()
        d = time.time()
        time_get_patterns += (d - c)
        count_get_patterns += 1
        self.alpha = alpha
        self.beta = beta
        self.maximizing = maximizing
        self.remaining_depth = remaining_depth
        c = time.time()
        self.game_over = self.is_game_over()
        d = time.time()
        time_game_over += (d - c)
        count_game_over += 1

        self.possible_moves = None
        self.parent = parent
        self.children = {}
        
        b = time.time()
        time_constructor += (b - a)
        count_constructor += 1
        ### PERFORMANCE EVAL

        if remaining_depth == 0 or self.game_over:
            self.evaluate()
            return

        self.perform_minmax()

    def perform_minmax(self):
        global time_possible_moves, count_possible_moves
        if self.possible_moves is None:
            parent_possible_moves = self.parent.possible_moves.copy() if self.parent else None
            ### PERFORMANCE EVAL
            a = time.time()
            self.possible_moves = self.board.get_possible_moves(parent_possible_moves, self.move)
            b = time.time()
            time_possible_moves += (b - a)
            count_possible_moves += 1
            ### PERFORMANCE EVAL
        for possible_move in self.possible_moves:
            if possible_move.position in self.children.keys():
                child = self.children[possible_move]
                child.move = possible_move
                child.update_with_depth(self.alpha, self.beta,
                                        not self.maximizing, self, self.remaining_depth - 1)
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
                               self, self.remaining_depth - 1)
            hash_dictionary[hash_value] = child
        else:
            child.move = move
            child.update_with_depth(self.alpha, self.beta,
                                    not self.maximizing, self, self.remaining_depth - 1)
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

    def update_with_depth(self, alpha, beta, maximizing, parent, remaining_depth):
        if remaining_depth == self.remaining_depth or self.game_over:
            return
        self.alpha = alpha
        self.beta = beta
        self.maximizing = maximizing
        self.score = float('-inf') if self.maximizing else float('inf')
        self.parent = parent
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
        print("Maximizing: ", self.maximizing, sep="")
        print("Children:")
        for child in self.children.values():
            print("\tColor: ", child.move.color, sep="")
            print("\tPosition: ", child.move.position, sep="")
            print("\tScore: ", child.score, sep="")
            print("\tMaximizing: ", child.maximizing, sep="", end="\n\n")
        print("=========")

    def evaluate(self) -> None:
        ### PERFORMANCE EVAL
        global time_evaluate, count_evaluate
        a = time.time()

        self.score = 0
        self.score = PatternsValue[Patterns.CAPTURE] \
            * (self.captures[WHITE] - self.captures[BLACK])
        for mask_length, mask_dictionary in MASKS.items():
            for pattern in self.patterns:
                while pattern != 0:
                    small_pattern = pattern % 3**mask_length
                    pattern //= 3
                    for pattern_code, masks in mask_dictionary.items():
                        mask_occurrences = masks.count(small_pattern)
                        mask_occurrences_2 = masks_2[mask_length][pattern_code].count(small_pattern)
                        self.score += PatternsValue[pattern_code] * (mask_occurrences - mask_occurrences_2)
        b = time.time()
        time_evaluate += (b - a)
        count_evaluate += 1
        ### PERFORMANCE EVAL
    
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
    ### PERFORMANCE EVAL
    global time_hash, count_hash
    a = time.time()

    hash_value = board.get_hash()
    hash_value = hash_value + '-' + str(captures[WHITE]) + '-' + str(captures[BLACK])
    b = time.time()
    time_hash += (b - a)
    count_hash += 1
    ### PERFORMANCE EVAL
    if hash_value in hash_dictionary.keys():
        return hash_dictionary[hash_value], hash_value
    return None, hash_value


class Maximilian():
    @staticmethod
    def get_next_move(board: Board, last_move: Move, captures: dict) -> Move:
        root, hash_value = retrieve_node_from_hashtable(board, last_move, captures.copy())
        a = time.time()
        if root is None:
            print("Creating new node.")
            root = MinMaxNode(board, last_move, captures.copy(), float('-inf'), float('inf'), False, None, remaining_depth=3)
            hash_dictionary[hash_value] = root
        else:
            print("Got node from hashtable. Updating.")
            root.update_as_root(remaining_depth=3)
        print("Average constructor time:", (time_constructor / count_constructor), count_constructor, time_constructor, sep=" ")
        print("Average patterns    time:", (time_get_patterns / count_get_patterns), count_get_patterns, time_get_patterns, sep=" ")
        print("Average game over   time:", (time_game_over / count_game_over), count_game_over, time_game_over, sep=" ")
        print("Average poss moves  time:", (time_possible_moves / count_possible_moves), count_possible_moves, time_possible_moves, sep=" ")
        print("Average hash        time:", (time_hash / count_hash), count_hash, time_hash, sep=" ")
        print("Average evaluate    time:", (time_evaluate / count_evaluate), count_evaluate, time_evaluate, sep=" ")
        move, score = root.get_best_move()
        b = time.time()
        print(b-a)
        print(move.position)
        root.dump()
        return move
