import re
from typing import Union
from .constants import WHITE, BLACK, EMPTY
from .errors import YouAreDumbException

REGEX_MOVE_STRING = r'^([0-9]|1[0-8]) ([0-9]|1[0-8])$'

class Move():
    __slots__ = ['position', 'color', 'previous_color', 'opposite_color']
    def __init__(self, color: int, position: Union[tuple[int], str],
                 previous_color: int = EMPTY):
        if type(position) == str:
            regex_result = re.search(REGEX_MOVE_STRING, position)
            if regex_result is None:
                raise YouAreDumbException("You are dumb, but we love you...")
            position = tuple([int(regex_result.group(1)), int(regex_result.group(2))])
        self.color = color
        self.position = position
        self.previous_color = previous_color
        self.opposite_color = self.__get_opposite_color()

    def __get_opposite_color(self):
        if self.color == EMPTY:
            return EMPTY
        return BLACK if self.color == WHITE else WHITE

