import re
from typing import Union
from .constants import WHITE, BLACK, EMPTY

REGEX_MOVE_STRING = r'^([0-9]|1[0-8]) ([0-9]|1[0-8])$'

class Move():
    __slots__ = ['position', 'color', 'previous_color', 'opposite_color',
                 'captures']
    def __init__(self, color: int, position, #: Union[tuple[int], str],
                 previous_color: int = EMPTY):
        if type(position) == str:
            regex_result = re.search(REGEX_MOVE_STRING, position)
            if regex_result is None:
                raise ValueError("Invalid position. Coordinates must be between 0 and 18, separated by a space.")
            position = tuple([int(regex_result.group(1)), int(regex_result.group(2))])
        self.color = color
        self.position = position
        self.previous_color = previous_color
        self.opposite_color = self.__get_opposite_color()
        self.captures = set()

    def __get_opposite_color(self):
        if self.color == EMPTY:
            return EMPTY
        return BLACK if self.color == WHITE else WHITE

