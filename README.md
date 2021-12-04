# 🔥 Welcome to Gomoku 🔥
by Cristina Fernández Bornay & Ivan Baran.
___
### Table of contents:
1. [ℹ️ Description](https://github.com/42ibaran/gomoku_v2#1-%E2%84%B9%EF%B8%8F-description)
    1. [🖥️ 4️2](https://github.com/42ibaran/gomoku_v2#11-%EF%B8%8F-4%EF%B8%8F2)
    2. [🧮 What is Gomoku](https://github.com/42ibaran/gomoku_v2#12--what-is-gomoku)
    3. [🤹🏽 Playing modes](https://github.com/42ibaran/gomoku_v2#13-playing-modes)
2. [🤖 Play on terminal](https://github.com/42ibaran/gomoku_v2#2--play-on-terminal)
    1. [🔨 Installation](https://github.com/42ibaran/gomoku_v2#21--installation)
    2. [🏄🏽‍♀️ Usage](https://github.com/42ibaran/gomoku_v2#22--usage)
3. [🔥 Play on web](https://github.com/42ibaran/gomoku_v2#3--play-on-web)
    1. [🔨 Installation](https://github.com/42ibaran/gomoku_v2#31--installation)
    2. [🏄🏽‍♀️ Usage](https://github.com/42ibaran/gomoku_v2#32--usage)
4. [Testing](https://github.com/42ibaran/gomoku_v2#4-testing)
5. [License](https://github.com/42ibaran/gomoku_v2#5-license)
___
## 1. ℹ️ **Description**

This is an application presented as a solution for the 42 Gomoku project.

It involves creating a Gomoku game integrating an AI player capable of beating a human
player the fastest way possible. To do this, you will implement a min-max algorithm but
also do research, trial and error to find the most adapted heuristics.

### 1.1. 🖥️ **4️2**

42 is a future-proof computer science training to educate the next generation of
software engineers. The 42 program takes a project-based approach to progress and
is designed to develop technical and people skills that match the expectations of
the labor market.

[Find more in the website!](https://42.fr/en/homepage/)

### 1.2. 🧮 **What is Gomoku**

[Gomoku](https://en.wikipedia.org/wiki/Gomoku) is a strategy board game traditionally
played on a [Go](https://en.wikipedia.org/wiki/Go_%28game%29) board with stones of
two different colors: black [ ○ ] and white [ ● ].

Two players take turns placing stones of their color on an intersection of the board,
and the game ends when one player manages to align five stones. Gomoku will be played
on a 19x19 Goban, without limit to the number of stones. In the context of this project,
we play with the following additional rules:

1. Captures

You can remove a pair of your opponent’s stones from the board by flanking them with your own stones.
**If you manage to capture 10 stones, meaning 5 captures, you win!!**

Ex: in this board => [ ○ ● ● _ ]; if blacks played [ ○ ● ● ○ ] => the result will be [ ○ _ _ ○ ].

Also, you can move into a position that leads to a capture pattern but it will not have any effect.

Ex: in this board => [ ○ ● _ ○ ]; if whites played [ ○ ● ● ○ ] => the result will be [ ○ ● ● ○ ].

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
the game continues. Also, even if a player has 5 in a row, if the opponent can capture their
5th pair in the next move, they win if they play that move.

### 1.3. **Playing modes**

1. Human 🦹🏽‍♀️ vs. 🦹🏽 Human

By default, you will play against your nice pals. To make it more interesting, you can choose
to receive suggestions or not, as you wish.

2. Human 🥷🏽 vs. 🧠 Maximilian

You should choose this option if your pals are not very good at playing Gomoku and you are
already bored of them. Maximilian is an incredible AI designed to beat you in less than
half a second by taking into account the best move based on the current and future board and
the way you play!

3. White 🤍 vs. 🖤 Black

When playing against Maximilian, by default you will play Blacks [ ○ ], so you will start playing.
Therefore, you one attacking an Maximilian will have to defend itself, event it will win anyway.

In case you don't know how to cope with confrontation and your preferred strategy is to defend
instead of attacking, we have implemented an option to allow you wo play Whites [ ● ]. Be careful,
Maximilian is also good at attacking!!

4. Receive suggestions?

As mentioned before, you and your pals can choose to receive suggestions from Maximilian.
they way we have implemented this option is by asking Maximilian to play as it was you.
This is a great option but it has two flakes! First, if you both choose to play Max's
suggestion, it can lead to a pretty long game. Second, get creative in the middle of the
game, there might me a miscommunication between your strategy and Max's one. Free advice:
try to understand how it is trying to do!!

___
## 2. 🤖 **Play on terminal**

### 2.1. 🔨 **Installation**

**Play directly on your machine:**
- Choose Python 3.9 as your interpreter.
- Install the needed packages: `python3 -m pip install -r requirements.txt`.
- To select the desired playing mode run: `python3 launch_game.py -h`.
- Run the program. Ex: `python3 launch_game.py -tms`.

**Use a dev container:**
- lolol

**Use Docker:**
- Check that Docker is properly installed and running.
- Run `...`

### 2.2. 🤹🏽 **Usage**

Once you have properly launched the program, it will manage the turns itself.
You will be asked when it is your turn to introduce your desired move.
The input should be in the format: `<pos_y pos_x>`.

In case you introduce an invalid position (already taken, out of the board,
double free-three) the program will display an error and ask again and again.

___
## 3. 🔥 **Play on web**

### 3.1. 🔨 **Installation**

### 3.2. 🤹🏽 **Usage**

___
## 4. **Testing**

___
## 5. **License**

© 2021 Copyright Ivan Baran & Cristina Fernández Bornay under the MIT License