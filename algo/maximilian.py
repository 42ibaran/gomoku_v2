from __future__ import annotations
import time
from .move import Move
from .board import Board
from .constants import WHITE, BLACK

start_time = None
intelligence = None
TIME_LIMIT = 0.49

def prune(maximizing, best_score, child_score, best_child, child, alpha, beta):
    is_prune = False
    if maximizing:
        if child_score > best_score:
            best_child = child
        best_score = max(best_score, child_score)
        alpha = max(alpha, child_score)
        if beta <= alpha:
            is_prune = True
    else:
        if child_score < best_score:
            best_child = child
        best_score = min(best_score, child_score)
        beta = min(beta, child_score)
        if beta <= alpha:
            is_prune = True
    return is_prune, best_score, best_child, alpha, beta

def perform_minmax(board: Board, alpha, beta,
                    remaining_depth):
    maximizing = not board.move.color == WHITE

    if remaining_depth == 1:
        return None, board.score

    if len(board.children) == 0:
        board.build_children()
    if board.check_if_over():
        return None, board.score

    best_child = None
    best_score = float('-inf') if maximizing else float('inf')
    for possible_move, next_board in board.order_children_by_score(maximizing):
        if time.time() - start_time < TIME_LIMIT or intelligence:
            _, child_score = perform_minmax(next_board, alpha, beta,
                                            remaining_depth - 1)
        else:
            child_score = next_board.score
        is_prune, best_score, best_child, alpha, beta = prune(maximizing, best_score,
                                                              child_score, best_child,
                                                              possible_move, alpha, beta)
        if is_prune:
            break

    return Move(board.move.opposite_color, best_child), best_score

def get_next_move(board: Board, depth=4) -> tuple[Move, float]:
    global start_time, intelligence
    start_time = time.time()
    intelligence = True
    if not board.move:
        return Move(BLACK, "9 9"), 0.0
    best_child, _ = perform_minmax(
        board,
        float('-inf'),
        float('inf'),
        depth
    )
    b = time.time()
    return best_child, (b - start_time)
