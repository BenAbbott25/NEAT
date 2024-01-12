import neat
import pygame
import os
import pickle
import tqdm
from snake import Game
from sortedReporter import SortedStdOutReporter

frame_size_x = 720
frame_size_y = 480
max_cycles_without_food = 250

starting_generation = 300
ending_generation = 2000
save_every = 100

def eval_genomes(genomes, config):
    show_game = False
    # routes = [0,[]]
    max_fitness = max((genome.fitness for _, genome in genomes if genome.fitness is not None), default=0)

    for genome_id, genome in tqdm.tqdm(genomes):
        if genome.fitness is not None and genome.fitness >= max_fitness * 0.75:
            show_game = True
        # route = []
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = Game(72, 48, 10, 250, "genomeID: {0}".format(genome_id),show_game)  # Initialize a new game for each genome
        while game.is_game_over == False and game.cycles_since_last_food < max_cycles_without_food:
            sensors = game.snake_vision()
            inputs = net.activate(sensors)
            game.run(inputs)
            genome.fitness = game.calculate_fitness()


def run_neat(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)
    p.add_reporter(SortedStdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    for i in range(starting_generation, ending_generation, save_every):
        # Load the saved population state if it exists
        if os.path.isfile(f"saves/population_gen_{i}.pkl"):
            with open(f"saves/population_gen_{i}.pkl", "rb") as f:
                p = pickle.load(f)
        print(f"Running generation {i}...")
        winner = p.run(eval_genomes, save_every)
        # Save the winner and the population state.
        print(f"Saving winner and population of generation {i}...")
        with open(f"saves/winner_gen_{i}.pkl", "wb") as f:
            pickle.dump(winner, f)
        with open(f"saves/population_gen_{i}.pkl", "wb") as f:
            pickle.dump(p, f)

    print("Winner's genome saved to winner.pkl")

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.ini')
    run_neat(config_path)
