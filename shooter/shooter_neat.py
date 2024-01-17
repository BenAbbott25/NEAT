import neat
import os
import pickle
import tqdm
from shooter import Game
import random
import numpy as np

frame_size_x = 720
frame_size_y = 480
player__batch_size = 10

def eval_genomes(genomes, config):
    genomes_list = list(genomes)
    random.shuffle(genomes_list)

    for i in tqdm.tqdm(range(0, len(genomes_list), player__batch_size)):
        # print(f"running game {int(np.floor(i/10))}/{int(np.ceil(len(genomes_list)/10))}")
        group = genomes_list[i:i+player__batch_size]
        game = Game(frame_size_x, frame_size_y, [genome_id for genome_id, _ in group])
        for genome_id, genome in group:
            genome.fitness = 0
            nets = {genome_id: neat.nn.FeedForwardNetwork.create(genome, config) for genome_id, genome in group}
        playerInputs = {}
        while not game.is_game_over:
            for genome_id, genome in group:
                sensors = game.get_vision(genome_id)
                inputs = nets[genome_id].activate(sensors)
                playerInputs[genome_id] = inputs
            game.run(playerInputs)
            game.update()
        fitnesses = game.calculate_fitness()
        for genome_id, genome in group:
            if genome_id in fitnesses:
                genome.fitness = fitnesses[genome_id]



def run_neat(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    run_save(p, 0, 100)
    run_save(p, 0, 1000)

def run_save(p, start_gen, end_gen):
    winner = p.run(eval_genomes, end_gen - start_gen)

    with open(f'winner_{end_gen}.pkl', 'wb') as output:
        pickle.dump(winner, output, 1)
    with open(f'population_{end_gen}.pkl', 'wb') as output:
        pickle.dump(p, output, 1)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.ini')
    run_neat(config_path)


