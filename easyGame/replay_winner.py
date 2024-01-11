import neat
import pygame
import os
import time
import pickle
from easy_game import Game

frame_size_x = 720
frame_size_y = 480

def play_game(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    game = Game(frame_size_x, frame_size_y, (50, 50), (700, 460))

    while game.frames > 0:
        inputs = net.activate((game.rect1_x, game.rect1_y, game.rect2_x, game.rect2_y))
        print("inputs: ",inputs)

        game.run(inputs, 1)
        game.draw()
        print("Fitness: ", game.fitness())

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.ini')

    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Load the winner.
    with open("winner.pkl", "rb") as f:
        genome = pickle.load(f)

    play_game(genome, config)