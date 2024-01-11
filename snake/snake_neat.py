import neat
import pygame
import os
import pickle
from snake import Game
# Your Game class here

frame_size_x = 720
frame_size_y = 480

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        # print('Genome ID: {0}'.format(genome_id))
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = Game(72, 48, 10, "genomeID: {0}".format(genome_id))  # Initialize a new game for each genome

        while game.is_game_over == False and game.cycles_since_last_food < 500:
            sensors = game.snake_vision()
            inputs = net.activate(sensors)
            # print("inputs: ",inputs)

            game.run(inputs)
            genome.fitness = game.calculate_fitness()
        # print("Fitness: ", genome.fitness)

def run_neat(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # winner = p.run(eval_genomes, 50) # Run for 50 generations
    winner = p.run(eval_genomes) # Run until fitness threshold is met

    # Save the winner.
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)

    print("Winner's genome saved to winner.pkl")

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.ini')
    run_neat(config_path)
