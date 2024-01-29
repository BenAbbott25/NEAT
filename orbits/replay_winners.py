import pickle
import neat
import os
from orbits_multi import Game
from orbits_neat import generate_coordinates, generate_coordinates_gauss
import numpy as np

# frame_size_x = 720
# frame_size_y = 480
# starting_fuel = 1250
# num_planets = 4

file_dir = "saves/6_planets_500_pop"

# load params from file
params_file = f"{file_dir}/params.pkl"
with open(params_file, "rb") as f:
    params = pickle.load(f)

frame_size_x = params["frame_size_x"]
frame_size_y = params["frame_size_y"]
starting_fuel = params["starting_fuel"]
num_planets = params["num_planets"]

def play_game_with_winners(winner_files, num_planets, show_score=False):
    # Load the saved winners and create networks
    genomes = []
    nets = []
    generation = []
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         f'{file_dir}/neat-config.ini')  # Assuming the config file is in the same directory
    for winner_file in winner_files:
        generation.append(int(winner_file.split("_")[-1].split(".")[0]))
        with open(winner_file, "rb") as f:
            genome = pickle.load(f)
            genomes.append(genome)
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)

    for _ in range(3):
        # start_point, end_point, planets = generate_coordinates(frame_size_x, frame_size_y)
        start_point, end_point, planets = generate_coordinates_gauss(frame_size_x, frame_size_y)

        batch_size = 3
        for i in range(0, len(genomes), batch_size):
            batch_genomes = genomes[i:i+batch_size]
            batch_nets = nets[i:i+batch_size]
            generation_batch = generation[i:i+batch_size]

            # Create the game instance
            game = Game(frame_size_x, frame_size_y, num_planets, starting_fuel, [genome.key for genome in batch_genomes], start_point, end_point, planets, 0, generation_batch)


            # Play the game
            while not game.is_game_over:
                playerInputs = {}
                for genome, net in zip(batch_genomes, batch_nets):
                    sensors = game.get_sensor_data(genome.key)
                    inputs = net.activate(sensors)
                    playerInputs[genome.key] = inputs
                game.run(playerInputs)

if __name__ == "__main__":
    winner_files = [f"{file_dir}/winner_gen_{i}.pkl" for i in range(0, 2000, 1) if os.path.isfile(f"{file_dir}/winner_gen_{i}.pkl")]
    play_game_with_winners(winner_files, num_planets)