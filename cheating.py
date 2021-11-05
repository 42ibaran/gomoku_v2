import time
from algo.maximilian import Maximilian
from algo.move import Move
from algo.game import Game
from algo.board import load_hashtables, save_hashtables

if __name__ == "__main__":
    game = Game()
    maximilian = Maximilian()
    for color in range(1, 3):
        for i in range(19):
            for j in range(19):
                print(i, j, color)
                cheating_move = Move(color, (i, j))
                captures_count = game.record_new_move(cheating_move)
                a = time.time()
                maximilian.get_next_move(game.board, cheating_move, game.captures)
                b = time.time()
                print("Time: %f" % (b - a))
                game.board.undo_move()
                game.captures[cheating_move.color] -= captures_count
                save_hashtables()
    print("Done.")
