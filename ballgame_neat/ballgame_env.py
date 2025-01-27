import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
from ballgame import Game, Team, Player

class BallGameEnv(gym.Env):
    def __init__(self, screen_width: int, screen_height: int, team_size: int):
        super(BallGameEnv, self).__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.team_size = team_size
        self.game = None
        self.screen = None
        self.clock = None
        self.left_team = None
        self.right_team = None

        # Define action and observation space
        action_space_low = np.array([-1, -1, -1, -1])
        action_space_high = np.array([1, 1, 1, 1])
        self.action_space = spaces.Box(
            low=action_space_low,
            high=action_space_high,
            dtype=np.float32
        )

        # left/right players * [x, y, holding ball], ball x, y, ball velocity x, y
        print(self.team_size)
        observation_space_shape = (1 + 3 * self.team_size * 2 + 4)
        observation_space_low = -np.ones(observation_space_shape)
        observation_space_high = np.ones(observation_space_shape)
        self.observation_space = spaces.Box(
            low=observation_space_low,
            high=observation_space_high,
            dtype=np.float32
        )

    def step(self, actions):
        # Execute one time step within the environment
        player_actions_team_left = {}
        player_actions_team_right = {}

        # Map actions to players based on genome_id
        for player in self.game.team_left.players:
            if player.id in actions:
                player_actions_team_left[player.id] = actions[player.id]
        
        for player in self.game.team_right.players:
            if player.id in actions:
                player_actions_team_right[player.id] = actions[player.id]

        # Apply actions to players
        for player in self.game.team_left.players:
            player.handle_input(player_actions_team_left.get(player.id, [0, 0, 0, 0]))
        
        for player in self.game.team_right.players:
            player.handle_input(player_actions_team_right.get(player.id, [0, 0, 0, 0]))

        self.game.update()
        observations = self._get_observations()
        rewards = self._get_rewards()
        done = not self.game.running or self.game.ball.stationary_ball > 2500
        infos = {}
        return observations, rewards, done, infos

    def reset(self, tournament):
        # Reset the state of the environment to an initial state
        self.game = Game(self.screen_width, self.screen_height, tournament[0], tournament[1], self.team_size)
        self.game.ball.heldBy = None
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            self.clock = pygame.time.Clock()
        return self._get_observations()

    def render(self, mode='human'):
        # Render the environment to the screen
        if mode == 'human' and self.screen is not None:
            self.game.run()
            pygame.display.flip()
            self.clock.tick(60)

    def close(self):
        # Perform any necessary cleanup
        self.game.running = False
        pygame.quit()

    def _get_observations(self):
        # Collect observations from the game state
        observations = []
        for player in self.game.team_left.players + self.game.team_right.players:
            normalized_x = (player.x / self.screen_width) * 2 - 1
            normalized_y = (player.y / self.screen_height) * 2 - 1
            observations.extend([normalized_x, normalized_y, player.holding_ball])
        normalized_ball_x = (self.game.ball.x / self.screen_width) * 2 - 1
        normalized_ball_y = (self.game.ball.y / self.screen_height) * 2 - 1
        observations.extend([normalized_ball_x, normalized_ball_y, self.game.ball.velocityVector.x/10, self.game.ball.velocityVector.y/10])
        return np.array(observations)

    def _get_rewards(self):
        # Calculate rewards based on the game state
        rewards = 0
        if self.game.ball.prev_x[-2] > 1 and self.game.ball.prev_x[-2] < self.screen_width - 1:
            rewards += (self.game.ball.x - self.game.ball.prev_x[-2]) / self.screen_width
        rewards -= 10 if self.game.ball.x <= 1 else 0
        rewards += 10 if self.game.ball.x >= self.screen_width - 1 else 0

        for player in self.game.team_left.players:
            if player.holding_ball:
                rewards += 1
            distance = np.sqrt((player.x - self.game.ball.x)**2 + (player.y - self.game.ball.y)**2)
            if distance < 100:
                rewards += distance / 100

        return rewards
