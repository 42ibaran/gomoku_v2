from __future__ import annotations

from .minmax_node import MinMaxNode, retrieve_node_from_hashtable, \
                         minmax_nodes_hashtable
from .move import Move
from .board import Board, print_board_performance
from .masks import MASKS, Patterns, PatternsValue, masks_2
from .constants import WHITE, BLACK
import time

class Maximilian():
    def perform_minmax(self, board: Board, last_move, captures, alpha, beta,
                       maximizing, previous_possible_moves, remaining_depth):
        score = PatternsValue[Patterns.CAPTURE] * (captures[WHITE] - captures[BLACK])
        evaluation_result = board.evaluate()
        score += evaluation_result[0]
        # game_over = evaluation_result[1]
        if remaining_depth == 0 or \
                captures[WHITE] >= 10 or \
                captures[BLACK] >= 10 or \
                board.check_if_over(last_move):
            return None, score
        
        score = float('-inf') if maximizing else float('inf')
        possible_moves = board.get_possible_moves(previous_possible_moves, last_move)
        # self.order_children_by_score()
        best_child = None
        for possible_move in possible_moves:
            captures_count = board.record_new_move(possible_move)
            child_captures = captures.copy()
            child_captures[possible_move.color] += captures_count

            _, child_score = self.perform_minmax(board.copy(), possible_move, child_captures, 
                                                 alpha, beta, not maximizing, possible_moves.copy(),
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

    def get_next_move(self, board: Board, last_move: Move, captures: dict) -> Move:
        best_child, _ = self.perform_minmax(
            board.copy(),
            last_move,
            captures.copy(),
            float('-inf'),
            float('inf'),
            False if last_move.color == WHITE else True,
            None,
            3
        )
        return best_child
