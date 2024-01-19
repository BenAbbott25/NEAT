import pygame
import neat
import numpy as np
import pickle
from orbits import Game

frame_size_x = 720
frame_size_y = 480
starting_fuel = 1000

save_file = "saves/0_planets/winner_gen_5.pkl"
if save_file != "":
    generation = int(save_file.split("_")[-1].split(".")[0])
    num_planets = int(save_file.split("/")[1].split("_")[0])

def play_game_with_winner(winner_file, num_planets, generation=0, show_score=False):
    # blocks_x, blocks_y = map(int, winner_file.split("_")[2:4])
    # Load the saved winner
    with open(winner_file, "rb") as f:
        genome = pickle.load(f)

    # Create the game instance
    title = f"Best Score: {int(np.floor(genome.fitness/10))}"
    if generation > 0:
        title = f"Gen: {generation}, " + title
    # print(show_score)
    game = Game(frame_size_x, frame_size_y, num_planets, starting_fuel)
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
    while not game.is_game_over:
        sensors = game.get_sensor_data(game.player)
        inputs = net.activate(sensors)
        game.run(inputs)

if __name__ == "__main__":
    # play_game_with_winner(f"saves/winner_gen_{n}.pkl")
    play_game_with_winner(save_file, num_planets, generation)