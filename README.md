# 🔥 Welcome to Gomoku 🔥
by [Ivan Baran](https://github.com/42ibaran) & [Cristina Fernández Bornay](https://github.com/CristinaFdezBornay).
___
### Table of contents:
1. ℹ️ Description
    1. 🖥️ 4️2
    2. 🧮 What is Gomoku
    3. 🤹🏽 Playing modes
2. 🤖 Play on terminal
    1. 🔨 Installation
    2. 🏄🏽‍♀️ Usage
3. 🔥 Play on web
    1. 🔨 Installation
    2. 🏄🏽‍♀️ Usage
4. License
___
## 1. ℹ️ **Description**

This is an application presented as a solution for the 42 Gomoku project.

It involves creating a Gomoku game integrating an AI player capable of beating a human
player the fastest way possible. To do this, we have implemented a min-max algorithm and
the most adapted heuristics.

### 1.1. 🖥️ **What is 4️2**

42 is a future-proof computer science training to educate the next generation of
software engineers. The 42 program takes a project-based approach to progress and
is designed to develop technical and people skills that match the expectations of
the labor market.

[Find out more in the website!](https://42.fr/en/homepage/)

### 1.2. 🧮 **What is Gomoku**

[Gomoku](https://en.wikipedia.org/wiki/Gomoku) is a strategy board game traditionally
played on a [Go](https://en.wikipedia.org/wiki/Go_%28game%29) board with stones of
two different colors: black [ ● ] and white [ ○ ].

Two players take turns placing stones of their color on an intersection of the board,
and the game ends when one player manages to align five stones. Gomoku will be played
on a 19x19 Goban, without limit to the number of stones. In the context of this project,
we play with the following additional rules:

1. Captures

You can remove a pair of your opponent’s stones from the board by flanking them with your own stones.
**If you manage to capture 10 stones, meaning 5 captures, you win!!**

Ex: in this board => [ ○ ● ● _ ]; if whites played [ ○ ● ● ○ ] => the result will be [ ○ _ _ ○ ].

Also, you can move into a position that leads to a capture pattern but it will not have any effect.

Ex: in this board => [ ○ ● _ ○ ]; if blacks played [ ○ ● ● ○ ] => the result will be [ ○ ● ● ○ ].

2. Double free-three

A free-three is an alignment of three stones that, if not immediately blocked, allows for
an indefensible alignment of four stones (that’s to say an alignment of four stones with
two unobstructed extremities); meaning a winning game.

Ex: these two possibilities are free-threes: [ _ ● ● ● _ ] and [ _ ● ● _ ● ].

A double-three is a move that introduces two simultaneous free-three alignments.
Well, **it is completely forbidden to introduce a double free-three**.

3. Gave Over?

As explained above, a player that manages to align five stones wins! The exception comes
when introducing the captures: if the opponent can break this alignment by capturing a pair,
the game continues. Also, even if a player has 5 in a row, but the opponent can capture a 5th
pair in the next move, the opponent wins if playing that move.

### 1.3. **Playing modes**

1. Human 🦹🏽‍♀️ vs. 🦹🏽 Human

By default, you will play against your nice pals. To make it more interesting, you can choose
to receive suggestions or not, as you wish.

2. Human 🥷🏽 vs. 🧠 Maximilian

You should choose this option if your pals are not very good at playing Gomoku and you are
already bored of them. Maximilian is an incredible AI designed to beat you in less than
half a second by taking into account the best move based on the current and future boards and
the way you play!

3. White 🤍 vs. 🖤 Black

When playing against Maximilian, by default you will play Blacks [ ● ], so you will start playing.
Therefore, you are the one attacking, and Maximilian will have to defend itself, it will win anyway...

In case you don't know how to cope with confrontation and your preferred strategy is to defend
instead of attacking, we have implemented an option to allow you to play Whites [ ○ ]. Be careful,
Maximilian is also better than you at attacking!!

4. Receive suggestions?

As mentioned before, you and your pals can choose to receive suggestions from Maximilian.
The way we have implemented this option is by asking Maximilian to play for you.
This is a great option but it has two flaws! First, if you both choose to play Max's
suggestions, it can lead to a pretty long game. Second, if you get creative in the middle of the
game, there might me a miscommunication between your strategy and Max's one. Free advice:
try to understand what it is trying to do!!

___
## 2. 🤖 **Playing time**

### 2.1. 🔨 **Installation**

**On your machine:**
- Choose Python 3.9 as your interpreter.
- Install the needed packages: `python3 -m pip install -r requirements.txt`.
- To select the desired playing mode run: `python3 launch_game.py -h`.
- Run the program `python3 launch_game.py -t`

**Use Docker:**
- Build the image: `docker build -t gomoku .`
- Run the container (all dependencies are installed): `docker run -it --rm gomoku`

### 2.2. 🤹🏽 **Usage**

Once you have properly launched the program, it will manage the turns itself.
When it is your turn, you will be asked to introduce your desired move.
The input should be in the format: `<pos_y pos_x>`.

In case you introduce an invalid position (already taken, out of the board,
double free-three) the program will display the error and ask again.

___
## 3. 🔥 **Play on web**

### 3.1. 🔨 **Installation**

- Choose Python 3.9 as your interpreter.
- Install the needed packages: `python3 -m pip install -r requirements.txt`.
- To select the desired playing mode run: `python3 launch_game.py -h`.
- Run the program `python3 launch_game.py`, it launch the server to play on web.
- Open another terminal and check that you have installed npm@6.14.15, node@14.18.0 and yarn@1.22.15.
- Then, go into app and run the following commands:
    - `npm i`
    - `yarn start`

### 3.2. 🤹🏽 **Usage**

Once launched it should automatically open the browser on [http://localhost:3000/](http://localhost:3000/).
The board will be displayed and you can click on it to place your stone.

Managing the options:
- If you wanted to play whites (`-w`), a black stone will already be placed on the board and it will be your time to move.
- If you indicated that you wanted to receive suggestions (`-s`), they'll be shown by placing a grey stone on the board. It will be removed if you prefer to move somewhere else.

Error management:
- If you put the stone on an invalid position, it will be automatically removed and a alert message will pop with the needed information.

Changing options or restarting the game:
- If at any point you want to play with a different configuration, you can stop the server and relaunch it with other parameters. Then, refresh the window and you can start playing again. Do not stop the app!!

___
## 4. **License**

© 2021 Copyright [Ivan Baran](https://github.com/42ibaran) & [Cristina Fernández Bornay](https://github.com/CristinaFdezBornay) under the [MIT License](https://github.com/42ibaran/gomoku_v2/blob/master/LICENSE)
