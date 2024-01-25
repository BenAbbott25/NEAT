import neat
import os
import pickle
import tqdm
from orbits_multi import Game
import numpy as np

frame_size_x = 720
frame_size_y = 480
# frame_size_x = 1280
# frame_size_y = 720
starting_fuel = 1250

population_size = 500
num_games = 5
num_planets = 3
starting_generation = 200
ending_generation = 2000
save_every = 100

batch_size = 100

save_file_dir = f"saves/{num_planets}_planets_{population_size}_pop"
if not os.path.exists(save_file_dir):
    os.makedirs(save_file_dir)

if starting_generation == 0:
    previous_gen = 0
else:
    save_file = f"saves/{num_planets}_planets_{population_size}_pop/winner_gen_{starting_generation}.pkl"
    previous_gen = int(save_file.split("_")[-1].split(".")[0])
    print(f"Starting from generation {previous_gen}...")
    print(f"Loading file {save_file}...")


def eval_genomes(genomes, config):
    genomes_list = list(genomes)
    for genome_id, genome in tqdm.tqdm(genomes_list, desc="Creating Networks"):
        genome.fitness = 0
        nets = {genome_id: neat.nn.FeedForwardNetwork.create(genome, config) for genome_id, genome in genomes_list}
    for n_game in tqdm.tqdm(range(num_games), desc="Games"):  # Repeat each game 3 times
        start_point, end_point, planets = generate_coordinates(frame_size_x, frame_size_y)
        for i in tqdm.tqdm(range(0, len(genomes_list), batch_size), desc=f"{n_game+1}/{num_games} Generation"):
            group = genomes_list[i:i+batch_size]
            genome_ids = [genome_id for genome_id, _ in group]
            game = Game(frame_size_x, frame_size_y, num_planets, starting_fuel, genome_ids, start_point, end_point, planets)
            game.draw_bg()
            playerInputs = {}
            while not game.is_game_over:
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
    update_config(num_planets)
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    for i in range(starting_generation, ending_generation, save_every):
        # Load the saved population state if it exists
        if os.path.isfile(f"saves/{num_planets}_planets_{population_size}_pop/population_gen_{i}.pkl"):
            print(f"Loading file /population_gen_{i}.pkl...")
            with open(f"saves/{num_planets}_planets_{population_size}_pop/population_gen_{i}.pkl", "rb") as f:
                p = pickle.load(f)
        winner = p.run(eval_genomes, save_every)
        # Save the winner and the population state.
        print(f"Saving winner and population of generation {i+save_every}...")
        save_dir = f"saves/{num_planets}_planets_{population_size}_pop"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        with open(f"saves/{num_planets}_planets_{population_size}_pop/winner_gen_{i+save_every}.pkl", "wb") as f:
            pickle.dump(winner, f)
        with open(f"saves/{num_planets}_planets_{population_size}_pop/population_gen_{i+save_every}.pkl", "wb") as f:
            pickle.dump(p, f)

    print("Winner's genome saved to winner.pkl")

def update_config(num_planets):
    print("Updating config file...")
    with open('neat-config.ini', 'r') as f:
        config_lines = f.readlines()

    with open(f'{save_file_dir}/neat-config.ini', 'w') as f:
        print(f"Updating config file with {num_planets} planets...")
        for line in config_lines:
            if line.startswith('num_inputs'):
                f.write(f'num_inputs = {11 + num_planets*3}\n')
            elif line.startswith('pop_size'):
                f.write(f'pop_size = {population_size}\n')
            else:
                f.write(line)    



def generate_coordinates(frames_x, frames_y):
    # split into 4 quadrants and place start and end points in different quadrants
    end_quadrant_x = np.random.randint(0,2)
    end_quadrant_y = np.random.randint(0,2)
    start_quadrant_x = np.random.randint(0,2)
    start_quadrant_y = np.random.randint(0,2)

    if end_quadrant_x == start_quadrant_x and end_quadrant_y == start_quadrant_y:
        end_quadrant_x = 1 - end_quadrant_x
        end_quadrant_y = 1 - end_quadrant_y

    quadrant_start_point = [np.random.randint(int(np.floor(frames_x*0.1/4)),int(np.ceil(frames_x*0.9/4))), np.random.randint(int(np.floor(frames_y*0.1/4)),int(np.ceil(frames_y*0.9/4)))]
    quadrant_end_point = [np.random.randint(int(np.floor(frames_x*0.1/4)),int(np.ceil(frames_x*0.9/4))), np.random.randint(int(np.floor(frames_y*0.1/4)),int(np.ceil(frames_y*0.9/4)))]

    start_point = [quadrant_start_point[0] + start_quadrant_x * frames_x/2, quadrant_start_point[1] + start_quadrant_y * frames_y/2]
    end_point = [quadrant_end_point[0] + end_quadrant_x * frames_x/2, quadrant_end_point[1] + end_quadrant_y * frames_y/2]

    planets = []
    for i in range(num_planets):
        planet_x = np.random.randint(int(np.floor(frames_x*0.1)),int(np.ceil(frames_x*0.9)))
        planet_y = np.random.randint(int(np.floor(frames_y*0.1)),int(np.ceil(frames_y*0.9)))
        while np.sqrt((planet_x - start_point[0])**2 + (planet_y - start_point[1])**2) < 100 or np.sqrt((planet_x - end_point[0])**2 + (planet_y - end_point[1])**2) < 100:
            planet_x = np.random.randint(int(np.floor(frames_x*0.1)),int(np.ceil(frames_x*0.9)))
            planet_y = np.random.randint(int(np.floor(frames_y*0.1)),int(np.ceil(frames_y*0.9)))
        mass = np.random.randint(800, 1800)
        planets.append([planet_x, planet_y, mass])

    return start_point, end_point, planets
    

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, f'{save_file_dir}/neat-config.ini')
    if previous_gen < 100:
        run_neat(config_path, previous_gen, 100, 10)
        run_neat(config_path, 100, 1000, 100)
    else:
        run_neat(config_path, previous_gen, 2000, 100)
