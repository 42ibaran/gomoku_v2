from __future__ import annotations

import threading
from typing import Union
from .move import Move
from .board import Board
from .constants import WHITE, BLACK, PATTERN_SIZES
from .masks import MASKS, Patterns, PatternsValue, masks_2

minmax_nodes_hashtable = {}

def retrieve_node_from_hashtable(board: Board, captures: dict) -> tuple[Union[MinMaxNode, None], str]:
    hash_value = board.get_hash()
    hash_value = hash_value + '-' + str(captures[WHITE]) + '-' + str(captures[BLACK])
    if hash_value in minmax_nodes_hashtable.keys():
        return minmax_nodes_hashtable[hash_value], hash_value
    return None, hash_value

class MinMaxNode():
    __slots__ = ['board', 'move', 'captures', 'score', 'patterns', 'children', 
                 'alpha', 'beta', 'maximizing', 'remaining_depth', 'possible_moves',
                 'parent', 'game_over', '_score_lock']

    def __init__(self, board: Board, move: Move, captures: dict,
                 alpha: Union[int, float], beta: Union[int, float],
                 maximizing: bool, parent: MinMaxNode = None, remaining_depth: int = 5):
        self.board = board
        self.move = move
        self.captures = captures
        self.score = float('-inf') if maximizing else float('inf')
        self.patterns = self.board.get_list_of_patterns()
        self.alpha = alpha
        self.beta = beta
        self.maximizing = maximizing
        self.remaining_depth = remaining_depth
        self.game_over = self.is_game_over()
        self.possible_moves = None
        self.parent = parent
        self.children = {}
        self._score_lock = threading.Lock()

        if remaining_depth == 0 or self.game_over:
            self.evaluate()
            return

        self.perform_minmax()

    def perform_minmax(self):
        if self.possible_moves is None:
            parent_possible_moves = self.parent.possible_moves.copy() if self.parent else None
            self.possible_moves = self.board.get_possible_moves(parent_possible_moves, self.move)
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

        child, hash_value = retrieve_node_from_hashtable(self.board, child_captures)
        if child is None:
            child = MinMaxNode(self.board, move, child_captures,
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
        for pattern_index, pattern in enumerate(self.patterns):
            pattern_size = PATTERN_SIZES[pattern_index]
            while pattern != 0 and pattern_size >= 5:
                small_pattern = pattern % 3**5
                pattern //= 3
                pattern_size -= 1
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
        with self._score_lock:
            self.score = PatternsValue[Patterns.CAPTURE] \
                * (self.captures[WHITE] - self.captures[BLACK])
        threads = list()
        for mask_size, mask_dictionary in MASKS.items():
            for pattern_index, pattern in enumerate(self.patterns):
                pattern_size = PATTERN_SIZES[pattern_index]
                while pattern != 0 and pattern_size >= mask_size:
                    new_thread = threading.Thread(target=self.meow, 
                                                  args=(pattern, pattern_size,
                                                        mask_dictionary, mask_size,))
                    threads.append(new_thread)
                    new_thread.start()
                    print("Starting thread %d" % (len(threads)))
        for thread in enumerate(threads):
            print("Joining thread %d" % (len(threads)))
            thread.join()

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

    def meow(self, pattern, pattern_size, mask_dictionary, mask_size):
        score = 0
        small_pattern = pattern % 3**mask_size
        pattern //= 3
        pattern_size -= 1
        for pattern_code, masks in mask_dictionary.items():
            mask_occurrences = masks.count(small_pattern)
            mask_occurrences_2 = masks_2[mask_size][pattern_code].count(small_pattern)
            score += PatternsValue[pattern_code] * (mask_occurrences - mask_occurrences_2)
        with self._score_lock:
            self.score += score
