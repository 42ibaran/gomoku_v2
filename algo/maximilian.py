import numpy
import time
from algo.move import Move
from algo.board import Board

class MinMaxNode():
    def __init__(self, board: Board, move: Move, remaining_depth: int = 5):
        self.board = board
        self.move = move

        if remaining_depth == 0:
            # self.evaluate()
            return

        self.children = []
        possible_moves = self.board.get_possible_moves(self.move.get_opposite_color())
        for possible_move in possible_moves:
            self.board.record_new_move(possible_move)
            self.children.append(MinMaxNode(self.board, possible_move, remaining_depth - 1))
            self.board.undo_move()

    def evaluate(self):
        self.board.dump()
        print(self.move.position)


class Maximilian():
    @staticmethod
    def get_next_move(board: Board, last_move: Move) -> Move:
        a = time.time()
        root = MinMaxNode(board, last_move)
        b = time.time()
        print(b - a)
        print("finished building tree")
        return next_move
