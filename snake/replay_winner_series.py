from replay_winner import play_game_with_winner
import os

for i in range(100, 2000, 100):
    if os.path.isfile(f"saves/winner_size_20_20_gen_{i}.pkl"):
        play_game_with_winner(f"saves/winner_size_20_20_gen_{i}.pkl", i)