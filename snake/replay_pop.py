import neat
import pickle
from snake import Game

def play_game_pop(winner_file):
    # Load the saved winner
    with open(winner_file, "rb") as f:
        genome = pickle.load(f)

    # Create the game instance
    game = Game(72, 48, 10, 250, "winner game")

    # Create the network
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'neat-config.ini')  # Assuming the config file is in the same directory
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # Play the game
    while not game.is_game_over and game.cycles_since_last_food < 250:
        sensors = game.snake_vision()
        inputs = net.activate(sensors)
        game.run(inputs)

if __name__ == "__main__":
    play_game_pop("winner_gen_{n}.pkl")