import numpy
from algo.move import Move
from algo.board import Board

class Maximilian():
    @staticmethod
    def get_next_move(board: Board, last_move: Move) -> Move:
        """
        Bla bla
        """
        next_move = Move(last_move.get_opposite_color(), (12, 12))
        return next_move
