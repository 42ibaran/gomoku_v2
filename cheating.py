import time
from algo.maximilian import get_next_move
from algo.move import Move
from algo.game import Game
from algo.board import load_hashtables, save_hashtables

if __name__ == "__main__":
    for color in range(1, 3):
        for i in range(5, 14):
            for j in range(5, 14):
                game = Game()
                print(i, j, color)
                cheating_move = Move(color, (i, j))
                game.record_new_move(cheating_move)
                a = time.time()
                get_next_move(game.board, 5)
                b = time.time()
                print("Time: %f" % (b - a))
    print("Saving hashtables...")
    save_hashtables()
    print("Done.")
