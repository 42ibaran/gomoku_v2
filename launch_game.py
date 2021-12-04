import argparse
from algo.maximilian import get_next_move, start_background_search, end_background_search
from algo.board import save_hashtables
from algo.constants import WHITE, BLACK, COLOR_DICTIONARY
from algo.errors import ForbiddenMoveError
from algo.game import Game
from algo.move import Move
import cProfile

def exit_game():
    save_hashtables()
    print("\nGood bye!")
    exit(0)

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

def get_and_record_human_move(game: Game, last_move=None):
    move_color = last_move.opposite_color if last_move else BLACK
    bg_process, event, queue = start_background_search(game.board) # if suggestions or vs_max else None, None, None
    while True:
        try:
            move_position = input("Where would you like to play? <pos_y pos_x> : ")
            human_move = Move(move_color, move_position)
            board = end_background_search(bg_process, event, queue)
            if board is not None:
                game.board = board
            game.record_new_move(human_move)
            break
        except (ForbiddenMoveError, ValueError) as e:
            print(e)
        except KeyboardInterrupt:
            end_background_search(bg_process, event, queue)
            exit_game()
    return human_move

def print_turn(human_turn, last_move):
    print("\n=================== [{}][{}]s TURN ===================\n".format(
            COLOR_DICTIONARY[last_move.opposite_color if last_move else BLACK],
            "HUMAN" if human_turn else "MAXIM"))

def print_maximilian_move(position, time, depth):
    print("Maximilian's move: {}\nTime: {:.3f}\nDepth: {}".format(position, time, depth))

def print_maximilian_suggestion(position, time, depth):
    print("Suggested move: {}\nTime: {:.3f}\nDepth: {}".format(position, time, depth))

def game_over_bitch():
    print("It's over bitch.")

def play_in_terminal(human_vs_maximilian, suggestion, human_as_white, intelligent):
    print(intelligent)
    last_move = None
    game = Game()
    human_turn = False if human_as_white else True
    turn = 1
    while True:
        print_turn(human_turn, last_move)
        if human_vs_maximilian and not human_turn:
            last_move, time_maximilian, depth = get_next_move(game.board)
            print_maximilian_move(last_move.position, time_maximilian, depth)
            game.record_new_move(last_move)
        else:
            if suggestion:
                suggestion_maximilian, time_maximilian, depth = get_next_move(game.board)
                print_maximilian_suggestion(suggestion_maximilian.position, time_maximilian, depth)
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
            play_in_terminal(human_vs_maximilian, suggestion, human_as_white, intelligent)
        except KeyboardInterrupt:
            exit_game()
    else:
        print("LAUNCH GAME ON WEB HEHE BISOUS :)")
