from replay_winner import play_game_with_winner
import os

frame_size_x = 720
frame_size_y = 480
num_planets = 0

for i in range(0, 100, 1):
    print(i)
    if os.path.isfile(f"saves/{num_planets}_planets/winner_gen_{i}.pkl"):
        print(f"Loading file /population_gen_{i}.pkl...")
        play_game_with_winner(f"saves/{num_planets}_planets/winner_gen_{i}.pkl", num_planets, i, True)