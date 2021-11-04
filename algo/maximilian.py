from __future__ import annotations

from .minmax_node import MinMaxNode, retrieve_node_from_hashtable, \
                         minmax_nodes_hashtable, print_evaluate_performance
from .move import Move
from .board import Board, print_board_performance
from .globals import evaluate_calls
import time

class Maximilian():
    @staticmethod
    def get_next_move(board: Board, last_move: Move, captures: dict) -> Move:
        a = time.time()
        root, hash_value = retrieve_node_from_hashtable(board, captures)
        if root is None:
            print("Creating new node.")
            root = MinMaxNode(board.copy(), last_move, captures.copy(),
                              float('-inf'), float('inf'), False,
                              None, remaining_depth=3)
            minmax_nodes_hashtable[hash_value] = root
        else:
            print("Got node from hashtable. Updating.")
            root.update_as_root(remaining_depth=3)
        root.perform_minmax()
        move = root.get_best_move()
        b = time.time()
        print("Time: %f" % (b - a))
        print(evaluate_calls)
        print_board_performance()
        print_evaluate_performance()
        return move
