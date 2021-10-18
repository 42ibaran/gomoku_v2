from __future__ import annotations

import numpy as np
import time
from typing import Union
from algo.move import Move
from algo.board import Board
from algo.constants import WHITE, BLACK, EMPTY_CAPTURES_DICTIONARY
from algo.masks import MASKS, PatternsValue

hash_dictionary = {}

class MinMaxNode():
    def __init__(self, board: Board, move: Move, captures: dict,
                 alpha: Union[int, float], beta: Union[int, float],
                 maximizing: bool, remaining_depth: int = 5):
        self.board = board
        self.move = move
        self.captures = captures
        self.score = float('-inf') if maximizing else float('inf')

        if remaining_depth == 0:
            self.score = 0
            self.evaluate()
            return

        self.children = []
        possible_moves = self.board.get_possible_moves(self.move.get_opposite_color())
        for possible_move in possible_moves:
            child = self.add_child(possible_move, alpha, beta,
                                   not maximizing, remaining_depth - 1)
            if maximizing:
                self.score = max(self.score, child.score)
                alpha = max(alpha, child.score)
                if beta <= alpha:
                    break
            else:
                self.score = min(self.score, child.score)
                beta = min(beta, child.score)
                if beta <= alpha:
                    break

    def add_child(self, move, alpha, beta, maximizing, remaining_depth) -> MinMaxNode:
        captures_count = self.board.record_new_move(move)
        child_captures = self.captures.copy()
        child_captures[move.color] += captures_count

        child, hash_value = retrieve_node_from_hashtable(self.board, child_captures)
        if child is None:
            child = MinMaxNode(self.board, move, 
                                child_captures, alpha, beta, maximizing,
                                remaining_depth)
            hash_dictionary[hash_value] = child
        self.children.append(child)
        self.board.undo_move()

        return child

    # def dump(self):
        # self.board.dump()
        # print("Color: ", self.move.color, sep="")
        # print("Position: ", self.move.position, sep="")
        # print("Score: ", self.score, sep="")
        # print("Alpha: ", alpha, sep="")
        # print("Beta: ", beta, sep="")
        # print("Maximizing: ", maximizing, sep="")
        # print("Children:")
        # for child in self.children:
        #     print("\tColor: ", child.move.color, sep="")
        #     print("\tPosition: ", child.move.position, sep="")
        #     print("\tScore: ", child.score, sep="")
        # print("=========")
        # input()

    def evaluate(self) -> None:
        patterns = self.board.get_list_of_patterns(self.move)
        blocking_patterns = self.convert_patterns_to_blocking(patterns)
        for size, mask_dictionary in MASKS.items():
            small_patterns = self.divide_patterns_by_size(patterns, size)
            small_blocking_patterns = self.divide_patterns_by_size(blocking_patterns, size)
            for pattern_code, masks in mask_dictionary.items():
                matches = small_patterns.intersection(masks)
                count_matches = len(matches)
                self.score += PatternsValue[pattern_code] * count_matches
                
                blocking_matches = small_blocking_patterns.intersection(masks)
                count_blocking_matches = len(blocking_matches)
                self.score += PatternsValue[pattern_code + 1] * count_blocking_matches
        # self.score *= self.move.color
    
    def get_best_move(self) -> Move:
        best_child = None
        best_score = float('-inf')
        for child in self.children:
            if child.score > best_score:
                best_child = child
                best_score = child.score
        return best_child.move

    def convert_patterns_to_blocking(self, patterns):
        blocking_patterns = []
        for pattern, index in patterns:
            pattern *= -1
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


def retrieve_node_from_hashtable(board: Board, captures: dict) -> (Union[MinMaxNode, None], str):
    hash_value = board.get_hash()
    hash_value = hash_value + '-' + str(captures[WHITE]) + '-' + str(captures[BLACK])
    if hash_value in hash_dictionary.keys():
        return hash_dictionary[hash_value], hash_value
    return None, hash_value


class Maximilian():
    @staticmethod
    def get_next_move(board: Board, last_move: Move, captures: dict) -> Move:
        # a = time.time()
        root, hash_value = retrieve_node_from_hashtable(board, captures.copy())
        if root is None:
            root = MinMaxNode(board, last_move, captures.copy(), float('-inf'), float('inf'), True)
            print(root.score)
            hash_dictionary[hash_value] = root
        return root.get_best_move()
        # b = time.time()
        # print(b - a)
        # print("finished building tree")
