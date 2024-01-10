import neat
from snake import SnakeGame  # Import your game class
import time

# Load configuration.
config_path = 'config-test2.ini'
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        print('Genome ID: {0}'.format(genome_id))
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = SnakeGame()  # Initialize a new game for each genome

        while not game.is_game_over:
            inputs = game.snake_vision()
            print("game state: ",game.get_current_state())
            print("inputs: ",inputs)
            action = net.activate(inputs)
            game.perform_action(action)
            game.draw()
            genome.fitness = game.calculate_fitness()

# Create the population, which is the top-level object for a NEAT run.
p = neat.Population(config)

# Add a stdout reporter to show progress in the terminal.
p.add_reporter(neat.StdOutReporter(True))
stats = neat.StatisticsReporter()
p.add_reporter(stats)

# Run the NEAT algorithm
winner = p.run(eval_genomes)

# You can print the winning genome and visualize it.
print('\nBest genome:\n{!s}'.format(winner))