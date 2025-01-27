import neat
import os
import pickle
from ballgame_env import BallGameEnv
import numpy as np

# Initialize environment
screen_width = 800
screen_height = 600
team_size = 5

# NEAT parameters
population_size = 100
num_games = 5
starting_generation = 0
ending_generation = 5000
save_every = 100

save_file_dir = f"saves/{population_size}_pop"
if not os.path.exists(save_file_dir):
    os.makedirs(save_file_dir)

def run_games(genomes, config):
    # Create a single game instance
    player_ids = [genome_id for genome_id, _ in genomes]
    left_teams = [player_ids[i:i+team_size] for i in range(0, len(player_ids)//2, team_size)]
    right_teams = [player_ids[i:i+team_size] for i in range(len(player_ids)//2, len(player_ids), team_size)]

    tournament = createTournament(left_teams, right_teams)

    # Create neural networks for each genome
    nets = {genome_id: neat.nn.FeedForwardNetwork.create(genome, config) for genome_id, genome in genomes}
    fitnesses = {genome_id: 0 for genome_id, _ in genomes}
    
    for _ in range(num_games):
        states = env.reset(tournament)
        done = False
        while not done:
            print(states)
            actions = {state["genome_id"]: nets[state["genome_id"]].activate(state["state"]) for state in states}
            states, rewards, done, _ = env.step(actions)
            for genome_id, reward in rewards.items():
                fitnesses[genome_id] += reward
    
    # Average fitness over the number of games
    for genome_id, genome in genomes:
        genome.fitness = fitnesses[genome_id] / num_games

def eval_genomes(genomes, config, generation):
    # Directly call run_game with all genomes
    run_games(genomes, config)

def run_neat(config_file, starting_generation=0, ending_generation=2000, save_every=100):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    for i in range(starting_generation, ending_generation, save_every):
        if os.path.isfile(f"{save_file_dir}/population_gen_{i}.pkl"):
            with open(f"{save_file_dir}/population_gen_{i}.pkl", "rb") as f:
                p = pickle.load(f)
        winner = p.run(lambda genomes, config: eval_genomes(genomes, config, i), save_every)
        with open(f"{save_file_dir}/winner_gen_{i+save_every}.pkl", "wb") as f:
            pickle.dump(winner, f)
        with open(f"{save_file_dir}/population_gen_{i+save_every}.pkl", "wb") as f:
            pickle.dump(p, f)

    print("Winner's genome saved to winner.pkl")

def createTournament(left_teams, right_teams):
    left_order = np.random.permutation(len(left_teams))
    right_order = np.random.permutation(len(right_teams))
    tournament = []
    for i in range(len(left_order)):
        tournament.append((left_teams[left_order[i]], right_teams[right_order[i]]))
    print(tournament)
    return tournament

if __name__ == '__main__':
    env = BallGameEnv(screen_width, screen_height, team_size)
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.ini')
    run_neat(config_path, starting_generation, ending_generation, save_every)