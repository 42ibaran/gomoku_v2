import argparse
from algo.maximilian import get_next_move
from algo.board import load_hashtables, save_hashtables
from algo.constants import WHITE, BLACK, EMPTY, COLOR_DICTIONARY
from algo.errors import ForbiddenMoveError
from algo.game import Game
from algo.move import Move
import cProfile

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--terminal", action='store_true', help="Play on the terminal.")
    parser.add_argument("-m", "--maximilian", action='store_true', help="Play against Maximilian.")
    parser.add_argument("-s", "--suggestion", action='store_true', help="Receive Maximilian' suggestions.")
    parser.add_argument("-w", "--white", action='store_true', help="Play as white (2nd turn).")
    parser.add_argument("-i", "--intelligent", action='store_true', help="Use The I.Max aka. The Intelligent Maximilian\n[default option The MP.Max. aka. The Max Power Maximilian]")
    arguments = parser.parse_args()
    white = arguments.white if arguments.maximilian else False
    return arguments.terminal, arguments.maximilian, arguments.suggestion, white, arguments.intelligent

def get_and_record_human_move(game, last_move=None):
    move_color = last_move.opposite_color if last_move else BLACK
    while True:
        try:
            move_position = input("Where would you like to play? <pos_y pos_x> : ")
            human_move = Move(move_color, move_position)
            game.record_new_move(human_move)
            break
        except (ForbiddenMoveError, ValueError) as e:
            print(e)
    return human_move

def print_turn(human_turn, last_move):
    print("\n=================== [{}][{}]s TURN ===================\n".format(
            COLOR_DICTIONARY[last_move.opposite_color if last_move else BLACK],
            "HUMAN" if human_turn else "MAXIM"))

def print_maximilian_move(position, time):
    print("Maximilian's move: {}\nTime: {}".format(position, time))

def print_maximilian_suggestion(position, time):
    print("Suggested move: {}\nTime: {}".format(position, time))

def game_over_bitch():
    print("It's over bitch.")

def play_in_terminal(human_vs_maximilian, suggestion, human_as_white, intelligent):
    print(intelligent)
    last_move = None
    game = Game()
    human_turn = False if human_as_white else True
    turn = 0
    while True:
        print_turn(human_turn, last_move)
        if human_vs_maximilian and not human_turn:
            last_move, time_maximilian = get_next_move(game.board)
            print_maximilian_move(last_move.position, time_maximilian)
            game.record_new_move(last_move)
        else:
            if suggestion:
                suggestion_maximilian, time_maximilian = get_next_move(game.board)
                print_maximilian_suggestion(suggestion_maximilian.position, time_maximilian)
            last_move = get_and_record_human_move(game, last_move)
        game.dump()
        print("TURN: {}".format(turn))
        if game.is_over:
            return game_over_bitch()
        human_turn = not human_turn if human_vs_maximilian else True
        turn += 1 if last_move.color == WHITE else 0

if __name__ == "__main__":
    terminal, human_vs_maximilian, suggestion, human_as_white, intelligent = get_arguments()
    if (terminal):
        try:
            load_hashtables()
            play_in_terminal(human_vs_maximilian, suggestion, human_as_white, intelligent)
        except KeyboardInterrupt:
            pass
        save_hashtables()
    else:
        print("LAUNCH GAME ON WEB HEHE BISOUS :)")
    print("\nGood bye!")
