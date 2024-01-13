from replay_winner import play_game_with_winner
import os

blocks_x = 20
blocks_y = 20

for i in range(0, 2000, 1):
    if os.path.isfile(f"saves/x{blocks_x}y{blocks_y}/winner_size_{blocks_x}_{blocks_y}_gen_{i}.pkl"):
        play_game_with_winner(f"saves/x{blocks_x}y{blocks_y}/winner_size_{blocks_x}_{blocks_y}_gen_{i}.pkl", i, True, True)