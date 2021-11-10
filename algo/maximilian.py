from __future__ import annotations

from .minmax_node import MinMaxNode, retrieve_node_from_hashtable, \
                         minmax_nodes_hashtable
from .move import Move
from .board import Board, print_board_performance
from .masks import MASKS, Patterns, PatternsValue, masks_2
from .constants import WHITE, BLACK
import time

class Maximilian():
    def perform_minmax(self, board: Board, alpha, beta,
                       previous_possible_moves, remaining_depth):
        maximizing = not board.move_history[-1].color == WHITE
        is_over = board.check_if_over(previous_possible_moves)
        if remaining_depth == 0 or is_over:
            score, _ = board.evaluate()
            return None, score
        
        score = float('-inf') if maximizing else float('inf')
        possible_moves = board.get_possible_moves(previous_possible_moves)
        # self.order_children_by_score()
        best_child = None
        for possible_move in possible_moves:
            board.record_new_move(possible_move)
            _, child_score = self.perform_minmax(board.copy(), alpha, beta, 
                                                 possible_moves.copy(),
                                                 remaining_depth - 1)
            board.undo_move()
            if maximizing:
                if child_score > score:
                    best_child = possible_move
                score = max(score, child_score)
                alpha = max(alpha, child_score)
                if beta <= alpha:
                    break
            else:
                if child_score < score:
                    best_child = possible_move
                score = min(score, child_score)
                beta = min(beta, child_score)
                if beta <= alpha:
                    break
        return best_child, score

    def get_next_move(self, board: Board) -> Move:
        # board.dump()
        # input()
        best_child, _ = self.perform_minmax(
            board.copy(),
            float('-inf'),
            float('inf'),
            None,
            3
        )
        return best_child
