import neat
import os
import pickle
import tqdm
from race import Game, Course
import numpy as np

frame_size_x = 1280
frame_size_y = 720
max_checkpoint_time = 1000

population_size = 500
num_games = 1
starting_generation = 0
ending_generation = 5000
save_every = 100

batch_size = 100

save_file_dir = f"saves"
if not os.path.exists(save_file_dir):
    os.makedirs(save_file_dir)

params = {
    "frame_size_x": frame_size_x,
    "frame_size_y": frame_size_y,
    "max_checkpoint_time": max_checkpoint_time,
    "population_size": population_size,
    "num_games": num_games,
    "starting_generation": starting_generation,
    "ending_generation": ending_generation,
    "save_every": save_every,
    "batch_size": batch_size,
}

params_file = os.path.join(save_file_dir, "params.pkl")
with open(params_file, "wb") as f:
    pickle.dump(params, f)


if starting_generation == 0:
    previous_gen = 0
else:
    save_file = f"saves/winner_gen_{starting_generation}.pkl"
    previous_gen = int(save_file.split("_")[-1].split(".")[0])
    # print(f"Starting from generation {previous_gen}...")
    # print(f"Loading file {save_file}...")

def eval_genomes(genomes, config, course):
    genomes_list = list(genomes)
    for genome_id, genome in tqdm.tqdm(genomes_list, desc="Creating Networks"):
        genome.fitness = 0
        nets = {genome_id: neat.nn.FeedForwardNetwork.create(genome, config) for genome_id, genome in genomes_list}
    genomes_list.sort(key=lambda x: x[1].fitness)
    for n_game in tqdm.tqdm(range(num_games), desc="Generation"):  # Repeat each game 3 times
        # start_point, end_point, planets = generate_coordinates(frame_size_x, frame_size_y)
        for i in tqdm.tqdm(range(0, len(genomes_list), batch_size), desc=f"{n_game+1}/{num_games} Games"):
            group = genomes_list[i:i+batch_size]
            genome_ids = [genome_id for genome_id, _ in group]
            game = Game(frame_size_x, frame_size_y, course, genome_ids)
            # game.draw_bg()  # Slow not good for training
            playerInputs = {}
            while len(game.drivers) > 0:
                for genome_id, genome in group:
                    sensors = game.get_sensor_data(genome_id)
                    inputs = nets[genome_id].activate(sensors)
                    playerInputs[genome_id] = inputs
                game.run(playerInputs)
            fitnesses = game.get_fitnesses()
            for genome_id, genome in group:
                if genome_id in fitnesses:
                    genome.fitness += fitnesses[genome_id]  # Accumulate fitness over the 3 games
    for genome_id, genome in genomes_list:
        genome.fitness /= num_games  # Average the fitness over the 3 games

def run_neat(config_file, starting_generation=0, ending_generation=2000, save_every=100):
    update_config()
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    for i in range(starting_generation, ending_generation, save_every):
        # Load the saved population state if it exists
        if os.path.isfile(f"saves/population_gen_{i}.pkl"):
            print(f"Loading file /population_gen_{i}.pkl...")
            with open(f"saves/population_gen_{i}.pkl", "rb") as f:
                p = pickle.load(f)
        course = Course(frame_size_x, frame_size_y)
        winner = p.run(lambda genomes, config: eval_genomes(genomes, config, course), save_every)
        # Save the winner and the population state.
        print(f"Saving winner and population of generation {i+save_every}...")
        save_dir = f"saves"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        with open(f"saves/winner_gen_{i+save_every}.pkl", "wb") as f:
            pickle.dump(winner, f)
        with open(f"saves/population_gen_{i+save_every}.pkl", "wb") as f:
            pickle.dump(p, f)

    print("Winner's genome saved to winner.pkl")

def update_config():
    print("Updating config file...")
    with open('neat-config.ini', 'r') as f:
        config_lines = f.readlines()

    with open(f'{save_file_dir}/neat-config.ini', 'w') as f:
        print(f"Updating config...")
        for line in config_lines:
            if line.startswith('pop_size'):
                f.write(f'pop_size = {population_size}\n')
            else:
                f.write(line)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, f'{save_file_dir}/neat-config.ini')
    if previous_gen < 100:
        run_neat(config_path, previous_gen, 100, 10)
        run_neat(config_path, 100, 1000, 100)
    else:
        run_neat(config_path, previous_gen, ending_generation, 100)
