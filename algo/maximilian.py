import numpy
import time
from typing import Union
from algo.move import Move
from algo.board import Board
from algo.constants import WHITE, BLACK, EMPTY_CAPTURES_DICTIONARY

# hash_list = []
hash_dictionary = {}

class MinMaxNode():
    def __init__(self, board: Board, move: Move, captures: dict, remaining_depth: int = 5):
        self.board = board
        self.move = move
        self.captures = captures

        if remaining_depth == 0:
            # self.evaluate()
            return

        self.children = []
        possible_moves = self.board.get_possible_moves(self.move.get_opposite_color())
        for possible_move in possible_moves:
            captures_count = self.board.record_new_move(possible_move)
            child_captures = self.captures.copy()
            child_captures[possible_move.color] += captures_count

            child, hash_value = retrieve_node_from_hashtable(self.board, child_captures)
            if child is not None:
                self.children.append(child)
            else:
                child = MinMaxNode(self.board, possible_move, 
                                   child_captures, remaining_depth - 1)
                self.children.append(child)
                hash_dictionary[hash_value] = child

            self.board.undo_move()

    def evaluate(self):
        self.board.dump()
        print(self.move.position)


def retrieve_node_from_hashtable(board: Board, captures: dict) -> (Union[MinMaxNode, None], str):
    hash_value = board.get_hash()
    hash_value = hash_value + '-' + str(captures[WHITE]) + '-' + str(captures[BLACK])
    if hash_value in hash_dictionary.keys():
        return hash_dictionary[hash_value], hash_value
    return None, hash_value


class Maximilian():
    @staticmethod
    def get_next_move(board: Board, last_move: Move, captures: dict) -> Move:
        a = time.time()
        root, hash_value = retrieve_node_from_hashtable(board, captures.copy())
        if root is None:
            root = MinMaxNode(board, last_move, captures.copy())
            hash_dictionary[hash_value] = root
        # hash_set = set(hash_list)
        # print(len(hash_list))
        # print(len(hash_set))
        b = time.time()
        print(b - a)
        print("finished building tree")
        # return next_move
