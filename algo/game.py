from .move import Move
from .board import Board
from .constants import EMPTY_CAPTURES_DICTIONARY, WHITE, BLACK

class Game():
    def __init__(self):
        self.board = Board()
        self.captures = EMPTY_CAPTURES_DICTIONARY
    
    def record_new_move(self, move: Move) -> None:
        captures_count = self.board.record_new_move(move)
        self.captures[move.color] += captures_count

    def dump(self):
        self.board.dump()
        print("White captures: %d" % (self.captures[WHITE]))
        print("Black captures: %d" % (self.captures[BLACK]))
