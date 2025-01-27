import pygame
import numpy as np

class Game:
    def __init__(self, left_team_params, right_team_params):
        self.running = True
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Capture The Flag")
        self.clock = pygame.time.Clock()
        self.left_team = Team(self, **left_team_params)
        self.right_team = Team(self, **right_team_params)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        for player in self.left_team.players:
            player.update()
        for player in self.right_team.players:
            player.update()

        self.check_flag_capture()

        self.left_team.flag.update()
        self.right_team.flag.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for player in self.left_team.players:
            pygame.draw.circle(self.screen, self.left_team.color, player.position, 10)
        for player in self.right_team.players:
            pygame.draw.circle(self.screen, self.right_team.color, player.position, 10)

        self.left_team.flag.draw(self.screen)
        self.right_team.flag.draw(self.screen)
        pygame.display.update()

    def check_flag_capture(self):
        for player in self.left_team.players:
            if player.has_flag:
                if ((player.position[0] - self.left_team.flag.position[0]) ** 2 + (player.position[1] - self.left_team.flag.position[1]) ** 2) < 100:
                    self.right_team.score += 1
                    player.has_flag = False
                    self.left_team.flag.position = (self.game.screen.get_width() / 4, self.game.screen.get_height() / 2)
                else:
                    if ((player.position[0] - self.right_team.flag.position[0]) ** 2 + (player.position[1] - self.right_team.flag.position[1]) ** 2) < 100:
                        player.has_flag = True
                        self.right_team.flag.position = (player.position[0], player.position[1])

        for player in self.right_team.players:
            if player.has_flag:
                if ((player.position[0] - self.right_team.flag.position[0]) ** 2 + (player.position[1] - self.right_team.flag.position[1]) ** 2) < 100:
                    self.left_team.score += 1
                    player.has_flag = False
                    self.right_team.flag.position = (self.game.screen.get_width() / 4 * 3, self.game.screen.get_height() / 2)
                else:
                    if ((player.position[0] - self.left_team.flag.position[0]) ** 2 + (player.position[1] - self.left_team.flag.position[1]) ** 2) < 100:
                        player.has_flag = True
                        self.left_team.flag.position = (player.position[0], player.position[1])

class Team:
    def __init__(self, game, color, team_size, side):
        self.game = game
        self.side = side
        self.color = color
        self.players = [Player(self, (self.game.screen.get_width() / 4 * (1 if self.side == "left" else 3), self.game.screen.get_height() * (i + 0.5)  / team_size)) for i in range(team_size)]
        self.flag = Flag(self, self.color, (self.game.screen.get_width() / 6 * (1 if self.side == "left" else 5), self.game.screen.get_height() / 2))
        self.score = 0

class Flag:
    def __init__(self, team, color, position):
        self.team = team
        self.color = color
        self.position = position

    def update(self):
        for player in self.team.players:
            if ((player.position[0] - self.position[0]) ** 2 + (player.position[1] - self.position[1]) ** 2) < 100:
                self.position = (self.game.screen.get_width() / 4 * (1 if self.team.side == "left" else 3), self.game.screen.get_height() / 2)
        
        for player in self.team.game.left_team.players if self.team.side == "right" else self.team.game.right_team.players:
            if player.has_flag:
                self.position = (self.game.screen.get_width() / 4 * (1 if self.team.side == "left" else 3), self.game.screen.get_height() / 2)

    def draw(self, screen):
        pygame.draw.line(screen, self.color, (self.position[0], self.position[1]), (self.position[0], self.position[1] - 20), 3)
        pygame.draw.line(screen, self.color, (self.position[0] - 10 if self.team.side == "left" else self.position[0] + 10, self.position[1] - 15), (self.position[0], self.position[1] - 20), 3)
        pygame.draw.line(screen, self.color, (self.position[0] - 10 if self.team.side == "left" else self.position[0] + 10, self.position[1] - 15), (self.position[0], self.position[1] - 15), 3)
        pygame.draw.circle(screen, self.color, self.position, 3)

class Player:
    def __init__(self, team, position):
        self.team = team
        self.position = position
        self.has_flag = False

    def update(self):
        self.position = (self.position[0] + np.random.normal(0.25 if self.team.side == "left" else -0.25, 0.25), self.position[1] + np.random.normal(0, 1))

def main():
    left_team_params = {"color": (255, 0, 0), "team_size": 5, "side": "left"}
    right_team_params = {"color": (0, 0, 255), "team_size": 5, "side": "right"}
    game = Game(left_team_params, right_team_params)
    
    while game.running:
        game.update()
        game.draw()
        game.clock.tick(60)

if __name__ == "__main__":
    main()