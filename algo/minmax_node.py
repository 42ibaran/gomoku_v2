from __future__ import annotations

import time
import numpy as np
import pickle
import json

from math import ceil
from typing import Union
from functools import partial
from .move import Move
from .board import Board
from .constants import WHITE, BLACK, PATTERN_SIZES
from .masks import MASKS, Patterns, PatternsValue, masks_2

minmax_nodes_hashtable = {}
pattern_score_hashtable = {}

calls = [0, 0]

PATTERNS_PER_THREAD = 28

def retrieve_node_from_hashtable(board: Board, captures: dict) -> tuple[Union[MinMaxNode, None], str]:
    hash_value = board.get_hash()
    hash_value = hash_value + '-' + str(captures[WHITE]) + '-' + str(captures[BLACK])
    if hash_value in minmax_nodes_hashtable.keys():
        return minmax_nodes_hashtable[hash_value], hash_value
    return None, hash_value

class MinMaxNode():
    __slots__ = ['board', 'move', 'captures', 'score', 'patterns', 'children', 
                 'alpha', 'beta', 'maximizing', 'remaining_depth', 'possible_moves',
                 'parent', 'game_over', 'children_order']

    def __init__(self, board: Board, move: Move, captures: dict,
                 alpha: Union[int, float], beta: Union[int, float],
                 maximizing: bool, parent: MinMaxNode = None, remaining_depth: int = 5):
        self.board = board
        self.move = move
        self.captures = captures
        # self.score = float('-inf') if maximizing else float('inf')
        self.patterns = self.board.get_list_of_patterns()
        self.alpha = alpha
        self.beta = beta
        self.maximizing = maximizing
        self.remaining_depth = remaining_depth
        self.game_over = False
        # self.game_over = self.is_game_over()
        self.possible_moves = None
        self.parent = parent
        self.children = {}
        self.children_order = []
        self.evaluate()

    
    def order_children_by_score(self):
        self.children_order = sorted(self.children, key=lambda x: self.children[x].score, reverse=not self.maximizing)

    def add_child(self, move) -> MinMaxNode:
        captures_count = self.board.record_new_move(move)
        child_captures = self.captures.copy()
        child_captures[move.color] += captures_count

        child, hash_value = retrieve_node_from_hashtable(self.board, child_captures)
        if child is None:
            child = MinMaxNode(self.board.copy(), move, child_captures,
                               self.alpha, self.beta, not self.maximizing,
                               self, self.remaining_depth - 1)
            minmax_nodes_hashtable[hash_value] = child
        else:
            child.move = move
            child.update_with_depth(self.alpha, self.beta,
                                    not self.maximizing, self,
                                    self.remaining_depth - 1)
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

    def update_with_depth(self, alpha, beta, maximizing, parent, remaining_depth):
        if remaining_depth == self.remaining_depth or self.game_over:
            return
        self.alpha = alpha
        self.beta = beta
        self.maximizing = maximizing
        self.score = float('-inf') if self.maximizing else float('inf')
        self.parent = parent
        self.remaining_depth = remaining_depth

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


    def get_best_move(self) -> Move:
        best_child = None
        best_score = float('-inf') if self.maximizing else float('inf')
        for child in self.children.values():
            if (self.maximizing and child.score > best_score) \
                    or (not self.maximizing and child.score < best_score):
                best_child = child
                best_score = child.score
        return best_child.move

    def convert_patterns_to_blocking(self, patterns):
        blocking_patterns = []
        for pattern, index in patterns:
            pattern = -pattern
            pattern[index] = 1
            blocking_patterns.append((pattern, index))
        return blocking_patterns

def print_evaluate_performance():
    print(calls)

def save_hashtables():
    # with open("minmax_nodes_hashtable.json", "w") as outfile:
    #     json.dump(minmax_nodes_hashtable, outfile)
    # with open("pattern_score_hashtable.json", "w") as outfile:
    #     json.dump(pattern_score_hashtable, outfile)
    pickle.dump(minmax_nodes_hashtable, open("minmax_nodes_hashtable.pickle", "wb"))
    pickle.dump(pattern_score_hashtable, open("pattern_score_hashtable.pickle", "wb"))

def load_hashtables():
    global pattern_score_hashtable #, minmax_nodes_hashtable
    # try:
    #     with open("minmax_nodes_hashtable.json", "r") as json_file:
    #         minmax_nodes_hashtable = json.load(json_file)
    # except FileNotFoundError:
    #     print("Hmm, minmax_nodes_hashtable pickle file not found?")
    #     minmax_nodes_hashtable = {}
    # try:
    #     with open("pattern_score_hashtable.json", "r") as json_file:
    #        pattern_score_hashtable = json.load(json_file)
    # except FileNotFoundError:
    #     print("Hmm, pattern_score_hashtable pickle file not found?")
    #     pattern_score_hashtable = {}

    try:
        minmax_nodes_hashtable = pickle.load(open("minmax_nodes_hashtable.pickle", "rb"))
    except FileNotFoundError:
        print("Hmm, minmax_nodes_hashtable pickle file not found?")
        minmax_nodes_hashtable = {}
    try:
        pattern_score_hashtable = pickle.load(open("pattern_score_hashtable.pickle", "rb"))
    except FileNotFoundError:
        print("Hmm, pattern_score_hashtable pickle file not found?")
        pattern_score_hashtable = {}
