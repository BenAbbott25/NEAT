from replay_winner import play_game_with_winner
import os

frame_size_x = 720
frame_size_y = 480
num_planets = 10

for i in range(0, 100, 1):
    print(i)
    saveFile = f"saves/{num_planets}_planets_{1000}_pop/winner_gen_{i}.pkl"
    if os.path.isfile(saveFile):
        print(f"Loading file /winner_gen_{i}.pkl...")
        play_game_with_winner(saveFile, num_planets, i, True)