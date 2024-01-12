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
    # routes = [0,[]]
    for genome_id, genome in tqdm.tqdm(genomes):
        # route = []
        # print('Genome ID: {0}'.format(genome_id))
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = Game(72, 48, 10, 250, "genomeID: {0}".format(genome_id))  # Initialize a new game for each genome
        while game.is_game_over == False and game.cycles_since_last_food < max_cycles_without_food:
            sensors = game.snake_vision()
            inputs = net.activate(sensors)
            # max_index = inputs.index(max(inputs))
            # route.append(max_index)
            print("Genome's species: ", genome.species)
            print("Genome's fitness: ", genome.fitness)
            best_genome = max(genomes, key=lambda x: x[1].fitness)
            print("Species of fittest genome: ", best_genome[1].species)
            game.run(inputs)
            genome.fitness = game.calculate_fitness()
    #     routefitness = game.calculate_fitness()
    #     if routefitness > routes[0]:
    #         routes[0] = routefitness
    #         routes[1] = route
    # print("Best route: ", routes[1])

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
