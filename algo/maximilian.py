from __future__ import annotations
import time
from .move import Move
from .board import Board
from .constants import WHITE, BLACK
from multiprocessing import Process, Event

stop_event = Event()

def prune(maximizing, best_score, child_score, best_child,
          child, alpha, beta) -> tuple[bool, int, Move, int, int]:
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

def perform_minmax(board: Board, alpha, beta, remaining_depth: int,
                   stop_event: Event=None) -> tuple[Move, int]:
    maximizing = not board.move.color == WHITE

    if remaining_depth == 1:
        board.depth = remaining_depth
        return None, board.score

    if len(board.children) == 0:
        board.build_children()
    if board.check_if_over():
        board.depth = remaining_depth
        return None, board.score

    best_child = None
    best_score = float('-inf') if maximizing else float('inf')
    stop = False
    for possible_move, next_board in board.order_children_by_score(maximizing):
        stop = stop_event is not None and stop_event.is_set()
        if not stop:
            if next_board.depth < remaining_depth - 1:
                _, child_score = perform_minmax(next_board, alpha, beta,
                                                remaining_depth - 1, stop_event)
                next_board.minmax_score = child_score
            else:
                child_score = next_board.minmax_score
        else:
            child_score = next_board.score
        is_prune, best_score, best_child, alpha, beta = prune(maximizing, best_score,
                                                              child_score, best_child,
                                                              possible_move, alpha, beta)
        if is_prune:
            break

    if not stop:
        board.depth = remaining_depth

    return Move(board.move.opposite_color, best_child), best_score

def get_next_move(board: Board, depth=3) -> tuple[Move, float, int]:
    start_time = time.time()
    if not board.move:
        return Move(BLACK, "9 9"), time.time() - start_time
    best_child, _ = perform_minmax(
        board,
        float('-inf'),
        float('inf'),
        depth
    )
    b = time.time()
    return best_child, (b - start_time), depth

def run_in_background(board: Board, stop_event: Event, depth=4) -> None:
    perform_minmax(
        board,
        float('-inf'),
        float('inf'),
        depth,
        stop_event
    )

def start_background_search(board: Board) -> Process:
    if not board.move:
        return
    background_process = Process(target=run_in_background, args=(board, stop_event))
    background_process.start()
    return background_process

def end_background_search(background_process) -> None:
    stop_event.set()
    if background_process is None:
        return
    while True:
        if not background_process.is_alive():
            break
    background_process.join()
    stop_event.clear()
