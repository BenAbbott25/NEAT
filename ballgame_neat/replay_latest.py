import gymnasium as gym
import numpy as np
import pygame
import torch
import torch.nn as nn
import torch.nn.functional as F
from ballgame_env import BallGameEnv
import matplotlib.pyplot as plt
import matplotlib
from team_strategies import team5_strategy, team6_strategy

# set up matplotlib
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display

# Initialize environment
screen_width = 800
screen_height = 600
team_size = 5
env = BallGameEnv(screen_width, screen_height, team_size)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define actor network
class Actor(nn.Module):
    def __init__(self, state_dim, action_dim, max_action):
        super(Actor, self).__init__()
        self.layer1 = nn.Linear(state_dim, 400)
        self.layer2 = nn.Linear(400, 300)
        self.layer3 = nn.Linear(300, action_dim)
        self.max_action = max_action

    def forward(self, x):
        x = torch.nn.functional.leaky_relu(self.layer1(x))
        x = torch.nn.functional.leaky_relu(self.layer2(x))
        return self.max_action * torch.tanh(self.layer3(x))

# Initialize actor for all teams
state_dim = env.observation_space.shape[0]
action_dim = env.action_space.shape[0]
max_action = float(env.action_space.high[0])

class TeamData:
    def __init__(self, color, size, speed, throw_strength):
        self.color = color
        self.size = size
        self.speed = speed
        self.throw_strength = throw_strength
        self.actor = Actor(state_dim, action_dim, max_action).to(device)
        self.episode_rewards = []

    def load_model(self):
        self.actor.load_state_dict(torch.load(f'saves/active_run_models/{self.color}/actor_latest.pth'))

class TeamDataCoded:
    def __init__(self, color, strategy, size, speed, throw_strength):
        self.color = color
        self.strategy = strategy
        self.size = size
        self.speed = speed
        self.throw_strength = throw_strength
        self.episode_rewards = []

    def load_model(self):
        pass

    def actor(self, state):
        action = self.strategy.act(state)
        return torch.tensor(action)

team1 = TeamData(color="green", size=5, speed=1, throw_strength=10)
team2 = TeamData(color="red", size=5, speed=1, throw_strength=10)
team3 = TeamData(color="blue", size=5, speed=1, throw_strength=10)
team4 = TeamData(color="orange", size=5, speed=1, throw_strength=10)
team5 = TeamDataCoded(color="grey", strategy=team5_strategy(), size=5, speed=0.5, throw_strength=7.5)
team6 = TeamDataCoded(color="purple", strategy=team6_strategy(), size=5, speed=0.75, throw_strength=5.0)
teams = [team1, team2, team3, team4, team5, team6]

# Load the latest models
import re
import os

def get_latest_episode(directory):
    files = os.listdir(directory)
    episode_numbers = [int(re.search(r'episode_(\d+)', file).group(1)) for file in files if 'episode_' in file]
    return max(episode_numbers) if episode_numbers else 0

played_episodes = min(get_latest_episode(f'saves/active_run_models/{team.color}') for team in teams if isinstance(team, TeamData))
for team in teams:
    team.load_model()

def play_game(num_games=10):
    for game in range(num_games):
        pygame.init()
        left_team = np.random.choice(teams)
        right_team = np.random.choice(teams)
        while left_team == right_team:
            right_team = np.random.choice(teams)
        state = env.reset(left_team, right_team)
        done = False
        while not done:
            state_tensor_left_team = torch.FloatTensor(state[0].reshape(1, -1)).to(device)
            state_tensor_right_team = torch.FloatTensor(state[1].reshape(1, -1)).to(device)
            action_left_team = left_team.actor(state_tensor_left_team).cpu().data.numpy()
            if action_left_team.shape[0] == 1:
                action_left_team = action_left_team.squeeze(0)
            action_right_team = right_team.actor(state_tensor_right_team).cpu().data.numpy()
            if action_right_team.shape[0] == 1:
                action_right_team = action_right_team.squeeze(0)

            # Construct action dictionaries
            action_dict_left_team = {i: action_left_team[i * 4:(i + 1) * 4] for i in range(team_size)}
            action_dict_right_team = {i: action_right_team[i * 4:(i + 1) * 4] for i in range(team_size)}

            next_state_left_team, next_state_right_team, reward_left_team, reward_right_team, done, _ = env.step(action_dict_left_team, action_dict_right_team)
            state = next_state_left_team, next_state_right_team

            if is_ipython:
                display.clear_output(wait=True)
                display.display(plt.gcf())

        print(f"Game {game + 1}/{num_games} finished.")

# Play the game
play_game()