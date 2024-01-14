from replay_winner import play_game_with_winner
import os

blocks_x = 10
blocks_y = 10

for i in range(0, 2000, 1):
    print(i)
    if os.path.isfile(f"saves/x{blocks_x}y{blocks_y}/winner_gen_{i}.pkl"):
        play_game_with_winner(f"saves/x{blocks_x}y{blocks_y}/winner_gen_{i}.pkl", blocks_x, blocks_y, i, True, True)