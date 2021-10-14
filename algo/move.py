import re
from typing import Union
from algo.constants import WHITE, BLACK
from algo.errors import YouAreDumbException

REGEX_MOVE_STRING = r'^([0-9]|1[0-8]) ([0-9]|1[0-8])$'

class Move():
    def __init__(self, color: int, position: Union[tuple[int], str]):
        if type(position) == str:
            regex_result = re.search(REGEX_MOVE_STRING, position)
            if regex_result is None:
                raise YouAreDumbException("You are dumb, but we love you...")
            position = tuple([int(regex_result.group(1)), int(regex_result.group(2))])
        self.color = color
        self.position = position

    def get_opposite_color(self):
        if self.color == BLACK:
            return WHITE
        return BLACK

