import neat
import os
import pickle
import tqdm
from orbits import Game

frame_size_x = 720
frame_size_y = 480
starting_fuel = 1000
num_planets = 0

starting_generation = 0
ending_generation = 2000
save_every = 100

if starting_generation == 0:
    previous_gen = 0
else:
    save_file = f"saves/{num_planets}_planets/winner_gen_{starting_generation}.pkl"
    previous_gen = int(save_file.split("_")[-1].split(".")[0])


def eval_genomes(genomes, config):
    for genome_id, genome in tqdm.tqdm(genomes):
        fitness = 0
        for i in range(3):
            fitness += runGame(genome_id, genome, config)
        fitness /= 3
        genome.fitness = fitness

def runGame(genome_id, genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    game = Game(frame_size_x, frame_size_y, num_planets, starting_fuel)
    while game.is_game_over == False:
        sensors = game.get_sensor_data(game.player)
        inputs = net.activate(sensors)
        game.run(inputs)
    return  game.calculate_fitness()


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
    with open('neat-config.ini', 'r') as f:
        config_lines = f.readlines()

    with open('neat-config.ini', 'w') as f:
        for line in config_lines:
            if line.startswith('num_inputs'):
                f.write(f'num_inputs = {num_planets + 12}\n')
            else:
                f.write(line)    

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.ini')
    if previous_gen < 10:
        run_neat(config_path, 0, 10, 1)
    if previous_gen < 100:
        run_neat(config_path, 10, 100, 10)
        run_neat(config_path, 100, 1000, 100)
    else:
        run_neat(config_path, previous_gen, 2000, 100)