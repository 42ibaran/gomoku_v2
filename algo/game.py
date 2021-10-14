from algo.move import Move
from algo.board import Board
from algo.constants import EMPTY
from algo.errors import YouAreDumbException

class Game():
    def __init__(self):
        self.board = Board()
    
    def record_new_move(self, move: Move) -> None:
        self.board.record_new_move(move)
        


