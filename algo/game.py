from algo.move import Move
from algo.board import Board
from algo.constants import EMPTY
from algo.errors import YouAreDumbException

class Game():
    def __init__(self):
        self.board = Board()
        self.move_history = []
    
    def record_new_move(self, move: Move) -> None:
        if self.board.matrix[move.position] != EMPTY:
            raise YouAreDumbException("The cell is already taken you dum-dum.")
        self.board.matrix[move.position] = move.color
        self.move_history.append(move)
        


