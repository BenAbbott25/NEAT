import neat
import os
import pickle
import tqdm
from orbits_multi import Game

# frame_size_x = 720
# frame_size_y = 480
frame_size_x = 1280
frame_size_y = 720
starting_fuel = 1000

num_planets = 4
starting_generation = 0
ending_generation = 2000
save_every = 100

batch_size = 100

if starting_generation == 0:
    previous_gen = 0
else:
    save_file = f"saves/{num_planets}_planets/winner_gen_{starting_generation}.pkl"
    previous_gen = int(save_file.split("_")[-1].split(".")[0])


def eval_genomes(genomes, config):
    genomes_list = list(genomes)
    batch_size = len(genomes_list)
    for i in tqdm.tqdm(range(0, len(genomes_list), batch_size)):
        group = genomes_list[i:i+batch_size]
        genome_ids = [genome_id for genome_id, _ in group]
        for _ in range(3):  # Repeat each game 3 times
            game = Game(frame_size_x, frame_size_y, num_planets, starting_fuel, genome_ids)
            for genome_id, genome in group:
                genome.fitness = 0
                nets = {genome_id: neat.nn.FeedForwardNetwork.create(genome, config) for genome_id, genome in group}
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
        for genome_id, genome in group:
            genome.fitness /= 3  # Average the fitness over the 3 games

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
        if os.path.isfile(f"saves/{num_planets}_planets/population_gen_{i}.pkl"):
            print(f"Loading file /population_gen_{i}.pkl...")
            with open(f"saves/{num_planets}_planets/population_gen_{i}.pkl", "rb") as f:
                p = pickle.load(f)
        winner = p.run(eval_genomes, save_every)
        # Save the winner and the population state.
        print(f"Saving winner and population of generation {i+save_every}...")
        with open(f"saves/{num_planets}_planets/winner_gen_{i+save_every}.pkl", "wb") as f:
            pickle.dump(winner, f)
        with open(f"saves/{num_planets}_planets/population_gen_{i+save_every}.pkl", "wb") as f:
            pickle.dump(p, f)

    print("Winner's genome saved to winner.pkl")

def update_config(num_planets):
    print("Updating config file...")
    with open('neat-config.ini', 'r') as f:
        config_lines = f.readlines()

    with open('neat-config.ini', 'w') as f:
        print(f"Updating config file with {num_planets} planets...")
        for line in config_lines:
            if line.startswith('num_inputs'):
                f.write(f'num_inputs = {num_planets * 2 + 12}\n')
            else:
                f.write(line)    

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.ini')
    if previous_gen < 10:
        run_neat(config_path, 0, 10, 1)
    if previous_gen < 100 :
        run_neat(config_path, 10, 100, 10)
        run_neat(config_path, 100, 1000, 100)
    else:
        run_neat(config_path, previous_gen, 2000, 100)
