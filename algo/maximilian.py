from __future__ import annotations

from .minmax_node import MinMaxNode, retrieve_node_from_hashtable, \
                         minmax_nodes_hashtable
from .move import Move
from .board import Board

class Maximilian():
    @staticmethod
    def get_next_move(board: Board, last_move: Move, captures: dict) -> Move:
        root, hash_value = retrieve_node_from_hashtable(board, captures)
        if root is None:
            print("Creating new node.")
            root = MinMaxNode(board, last_move, captures.copy(),
                              float('-inf'), float('inf'), False,
                              None, remaining_depth=3)
            minmax_nodes_hashtable[hash_value] = root
        else:
            print("Got node from hashtable. Updating.")
            root.update_as_root(remaining_depth=3)
        move = root.get_best_move()
        return move
