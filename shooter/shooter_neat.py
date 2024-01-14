import neat
import os
import pickle
import tqdm
from shooter import Game

frame_size_x = 720
frame_size_y = 480

def eval_genomes(genomes, config):
    genomes_list = list(tqdm.tqdm(genomes))
    for i in range(0, len(genomes_list), 10):
        group = genomes_list[i:i+10]
        game = Game(frame_size_x, frame_size_y, group)
        while not game.is_game_over:
            game.run()
        fitnesses = game.calculate_fitness()
        for genome_id, genome in group:
            genome.fitness = fitnesses[genome_id]
