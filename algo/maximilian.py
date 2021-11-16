from __future__ import annotations

from .move import Move
from .board import Board
from .constants import WHITE
import time
import numpy as np

f_b = np.array([
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  2,  2,  2,  2,  2,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0]
])

class Maximilian():
    def prune(self, maximizing, best_score, child_score, best_child, child, alpha, beta):
        prune = False

        if maximizing:
            if child_score > best_score:
                best_child = child
            best_score = max(best_score, child_score)
            alpha = max(alpha, child_score)
            if beta <= alpha:
                prune = True
        else:
            if child_score < best_score:
                best_child = child
            best_score = min(best_score, child_score)
            beta = min(beta, child_score)
            if beta <= alpha:
                prune = True
        return prune, best_score, best_child, alpha, beta
                

    def perform_minmax(self, board: Board, alpha, beta,
                       remaining_depth):
        maximizing = not board.move_history[-1].color == WHITE
        
        if remaining_depth == 0 or board.check_if_over():
            return None, board.score
        
        possible_moves = board.get_possible_moves()
        # self.order_children_by_score()
        best_child = None
        best_score = float('-inf') if maximizing else float('inf')
        for possible_move in possible_moves:
            next_board = board.record_new_move(possible_move)
            _, child_score = self.perform_minmax(next_board, alpha, beta, 
                                                 remaining_depth - 1)
            prune, best_score, best_child, alpha, beta = self.prune(maximizing, best_score,
                                                                    child_score, best_child,
                                                                    possible_move, alpha, beta)
            if prune:
                break

        return best_child, best_score

    def get_next_move(self, board: Board) -> Move:
        best_child, _ = self.perform_minmax(
            board,
            float('-inf'),
            float('inf'),
            3
        )
        return best_child
