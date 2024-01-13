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

blocks_x = 20
blocks_y = 20
block_size = 20

# starting_generation = 100
# ending_generation = 2000
# save_every = 100

save_file = "saves/x20y20/winner_size_20_20_gen_700.pkl"
previous_gen = int(save_file.split("_")[-1].split(".")[0])
# previous_gen = 0


def eval_genomes(genomes, config):
    show_game = False
    # routes = [0,[]]
    max_fitness = max((genome.fitness for _, genome in genomes if genome.fitness is not None), default=0)

    for genome_id, genome in tqdm.tqdm(genomes):
        # if genome.fitness is not None and genome.fitness >= max_fitness * 0.75:
        #     show_game = True
        show_game = True
        # route = []
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = Game(blocks_x, blocks_y, block_size, 250, "genomeID: {0}".format(genome_id),show_game)  # Initialize a new game for each genome
        while game.is_game_over == False and game.cycles_since_last_food < max_cycles_without_food:
            sensors = game.snake_vision()
            inputs = net.activate(sensors)
            game.run(inputs)
        genome.fitness = game.calculate_fitness()


def run_neat(config_file, starting_generation=0, ending_generation=2000, save_every=100):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)
    p.add_reporter(SortedStdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    for i in range(starting_generation, ending_generation, save_every):
        # Load the saved population state if it exists
        if os.path.isfile(f"saves/x{blocks_x}y{blocks_y}/population_size_{blocks_x}_{blocks_y}_gen_{i}.pkl"):
            print(f"Loading file /population_size_{blocks_x}_{blocks_y}_gen_{i}.pkl...")
            with open(f"saves/x{blocks_x}y{blocks_y}/population_size_{blocks_x}_{blocks_y}_gen_{i}.pkl", "rb") as f:
                p = pickle.load(f)
        print(f"Running generation {i}...")
        winner = p.run(eval_genomes, save_every)
        # Save the winner and the population state.
        print(f"Saving winner and population of generation {i}...")
        with open(f"saves/x{blocks_x}y{blocks_y}/winner_size_{blocks_x}_{blocks_y}_gen_{i+save_every}.pkl", "wb") as f:
            pickle.dump(winner, f)
        with open(f"saves/x{blocks_x}y{blocks_y}/population_size_{blocks_x}_{blocks_y}_gen_{i+save_every}.pkl", "wb") as f:
            pickle.dump(p, f)

    print("Winner's genome saved to winner.pkl")

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.ini')
    if previous_gen < 10:
        run_neat(config_path, 0, 10, 1)
    if previous_gen < 100:
        run_neat(config_path, 10, 100, 10)
        run_neat(config_path, 100, 1000, 100)
    else:
        run_neat(config_path, previous_gen, 1000, 100)
