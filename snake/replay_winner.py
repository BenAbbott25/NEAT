import pygame
import neat
import numpy as np
import pickle
from snake import Game

save_file = "saves/x20y20/winner_size_20_20_gen_1000.pkl"
# save_file = "saves/x10y10/winner_gen_500.pkl"
if save_file != "":
    generation = int(save_file.split("_")[-1].split(".")[0])

def play_game_with_winner(winner_file, blocks_x, blocks_y, generation=0, show_game=True, show_score=False):
    # blocks_x, blocks_y = map(int, winner_file.split("_")[2:4])
    # Load the saved winner
    with open(winner_file, "rb") as f:
        genome = pickle.load(f)

    # Create the game instance
    title = f"Best Score: {int(np.floor(genome.fitness/10))}"
    if generation > 0:
        title = f"Gen: {generation}, " + title
    print(show_score)
    game = Game(blocks_x, blocks_y, 25, 250, title, show_game, show_score)
    # game = Game(20, 20, 25, 250, f"Expected Score: {int(np.floor(genome.fitness/10))}",True)

    # Create the network
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'neat-config.ini')  # Assuming the config file is in the same directory
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    print(genome.fitness)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Play the game
    while not game.is_game_over and game.cycles_since_last_food < 250:
        sensors = game.snake_vision()
        inputs = net.activate(sensors)
        game.run(inputs)

if __name__ == "__main__":
    # play_game_with_winner(f"saves/winner_gen_{n}.pkl")
    play_game_with_winner(save_file, 20, 20, generation, True, True)