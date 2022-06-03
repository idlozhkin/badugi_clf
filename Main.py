from Game import Game
from Player import Player

num_games = int(input("Enter number of games: "))

game = Game()

player1 = Player("p1")
player2 = Player("p2")

input_ = input("Choose your position (1 for p1, 2 for p2): ")
if input_ == "1":
    first_turn = True
else:
    first_turn = False

game.start_game(player1, player2, first_turn, num_games)
