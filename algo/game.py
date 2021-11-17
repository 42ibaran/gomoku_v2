from .move import Move
from .board import Board
from .constants import EMPTY_CAPTURES_DICTIONARY, WHITE, BLACK

class Game():
    def __init__(self):
        self.board = Board()
        self.captures = EMPTY_CAPTURES_DICTIONARY
        self.is_over = False

    def record_new_move(self, move: Move) -> None:
        self.board = self.board.record_new_move(move)
        self.is_over = self.board.check_if_over()

    def dump(self):
        self.board.dump()
        # print(self.board.patterns)
        print("White captures: %d" % (self.board.captures_history[-1][WHITE]))
        print("Black captures: %d" % (self.board.captures_history[-1][BLACK]))
