import neat
import pygame
import os
import pickle
from easy_game import Game
# Your Game class here

frame_size_x = 720
frame_size_y = 480

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        # print('Genome ID: {0}'.format(genome_id))
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = Game(frame_size_x, frame_size_y, (50, 50), (500, 300))

        while game.frames > 0:
            inputs = net.activate((game.rect1_x, game.rect1_y, game.rect2_x, game.rect2_y))
            # print("inputs: ",inputs)

            game.run(inputs)
            genome.fitness = game.fitness()

def run_neat(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 50) # Run for 50 generations

    # Save the winner.
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)

    print("Winner's genome saved to winner.pkl")

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.ini')
    run_neat(config_path)
