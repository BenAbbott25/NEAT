import pygame
import neat
import numpy as np
import pickle
from snake import Game
n = 300

def play_game_with_winner(winner_file):
    # Load the saved winner
    with open(winner_file, "rb") as f:
        genome = pickle.load(f)

    # Create the game instance
    game = Game(72, 48, 10, 250, f"Expected Score: {int(np.floor(genome.fitness/10))}",True)
    # game = Game(20, 20, 25, 250, f"Expected Score: {int(np.floor(genome.fitness/10))}",True)

    # Create the network
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'neat-config.ini')  # Assuming the config file is in the same directory
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    print(genome.fitness)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Play the game
    while not game.is_game_over and game.cycles_since_last_food < 250:
        sensors = game.snake_vision()
        inputs = net.activate(sensors)
        game.run(inputs)

if __name__ == "__main__":
    play_game_with_winner(f"saves/winner_gen_{n}.pkl")