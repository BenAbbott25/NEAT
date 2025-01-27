import pygame
import numpy as np

screen_width = 800
screen_height = 600

class Game:
    def __init__(self, screen_width, screen_height, left_team, right_team, num_players):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Basketball Game')
        self.running = True
        self.num_players = num_players
        self.ball = Ball(self, self.screen_width / 2, self.screen_height / 2)
        self.team_left = Team((np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)), 
                              num_players, 
                              self.screen_width / 4, 
                              self.screen_height)
        self.team_right = Team((np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)), 
                              num_players, 
                              3 * self.screen_width / 4, 
                              self.screen_height)

    def update(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, self.team_left.color, (0, 0, 10, screen_height))
        pygame.draw.rect(self.screen, self.team_right.color, (screen_width-10, 0, 10, screen_height))
        for player in self.team_left.players + self.team_right.players:
            player.draw(self.screen)
            player.update_holding_ball_since()
        self.ball.updatePosition()
        self.ball.check_collisions()
        self.ball.draw(self.screen)
        for team in [self.team_left, self.team_right]:
            team.drawScore(self.screen)
            team.separatePlayers(self.team_right if team == self.team_left else self.team_left)
        pygame.display.flip()
        if self.team_left.score >= 10 or self.team_right.score >= 10:
            print(f"Team {self.team_left.color if self.team_left.score > self.team_right.score else self.team_right.color} wins!")
            self.running = False
    
    def reset(self):
        self.ball.stationary_ball = 0
        self.ball.x = self.ball.starting_x
        self.ball.y = self.ball.starting_y
        self.ball.velocityVector.magnitude = 0
        self.ball.velocityVector.updateCartesian()
        self.team_left.resetPlayers()
        self.team_right.resetPlayers()

class Ball:
    def __init__(self, game, x, y):
        self.game = game
        self.starting_x = x
        self.starting_y = y
        self.x = x
        self.y = y
        self.velocityVector = Vector("cartesian", 0, 0)
        self.heldBy = None
        self.last_team_colour = None
        self.prev_x = [self.x]
        self.prev_y = [self.y]
        self.stationary_ball = 0

    def draw(self, screen):
        for i in range(len(self.prev_x)-1, 0, -1):
            if self.last_team_colour == "green":
                trail_colour = (0, 255 * (i/100), 0)
            elif self.last_team_colour == "red":
                trail_colour = (255 * (i/100), 0, 0)
            elif self.last_team_colour == "blue":
                trail_colour = (0, 0, 255 * (i/100))
            elif self.last_team_colour == "orange":
                trail_colour = (255 * (i/100), 128 * (i/100), 0)
            elif self.last_team_colour == "purple":
                trail_colour = (128 * (i/100), 0, 128 * (i/100))
            elif self.last_team_colour == "lightgrey":
                trail_colour = (128 * (i/100), 128 * (i/100), 128 * (i/100))
            else:
                trail_colour = (255 * (i/100), 255 * (i/100), 255 * (i/100))
            pygame.draw.circle(screen, trail_colour, (self.prev_x[i], self.prev_y[i]), i/10)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 10)
        
        pygame.draw.rect(screen, (255, 255, 255), (0, 0, (2500-self.stationary_ball)/2500*screen_width, 10))

    def updatePosition(self):
        self.x += self.velocityVector.x/10
        self.y += self.velocityVector.y/10

        if self.y >= screen_height or self.y <= 0:
            self.velocityVector.y *= -1

        self.velocityVector.updatePolar()
        self.velocityVector.magnitude *= 0.9995
        self.velocityVector.updateCartesian()

        self.prev_x.append(self.x)
        self.prev_y.append(self.y)
        if len(self.prev_x) > 100:
            self.prev_x.pop(0)
            self.prev_y.pop(0)

        if self.velocityVector.magnitude < 0.1:
            self.stationary_ball += 1
        else:
            self.stationary_ball = 0

    def check_collisions(self):
        if self.stationary_ball != 0 and self.heldBy is None:
            catch_range = 45
        else:
            catch_range = 15
        for player in self.game.team_left.players + self.game.team_right.players:
            if self.heldBy == player:
                continue
            if self.x >= player.x - catch_range and self.x <= player.x + catch_range and self.y >= player.y - catch_range and self.y <= player.y + catch_range:
                player.holding_ball = True
                player.ball = self
                self.x = player.x
                self.y = player.y
                self.velocityVector.magnitude = 0
                self.velocityVector.updateCartesian()
                if player in self.game.team_left.players:
                    self.game.team_left.possessionCount += 1
                    self.last_team_colour = self.game.team_left.color
                else:
                    self.game.team_right.possessionCount += 1
                    self.last_team_colour = self.game.team_right.color
                self.heldBy = player
        
        if self.x < 0:
            self.game.team_right.score += 1
            self.x = self.starting_x
            self.y = self.starting_y
            self.velocityVector.magnitude = 0
            self.velocityVector.updateCartesian()
            self.game.reset()

        if self.x > screen_width:
            self.game.team_left.score += 1
            self.x = self.starting_x
            self.y = self.starting_y
            self.velocityVector.magnitude = 0
            self.velocityVector.updateCartesian()
            self.game.reset()

class Team:
    def __init__(self, color, size, x, max_y):
        self.color = color
        self.size = size
        self.starting_x = x
        self.max_y = max_y
        self.players = [Player(i, self.starting_x, self.max_y / (2*self.size) + (self.max_y * (i/self.size)), self.color) for i in range(self.size)]
        self.score = 0
        self.possessionCount = 0

    def drawScore(self, screen):
        font = pygame.font.Font(None, 74)
        score_text = font.render(str(self.score), True, self.color)
        screen.blit(score_text, (self.starting_x-12, 10))

    def resetPlayers(self):
        self.possessionCount = 0
        for player in self.players:
            player.x = self.starting_x
            player.y = self.max_y / (2*self.size) + (self.max_y * (player.id/self.size))
            player.holding_ball = False
            player.ball = None
    
    def separatePlayers(self, other_team):
        for player in self.players:
            for other_player in self.players + other_team.players:
                if player != other_player:
                    distance = np.sqrt((player.x - other_player.x) ** 2 + (player.y - other_player.y) ** 2)
                    if distance < 30:
                        overlap = 30 - distance
                        move_x = (player.x - other_player.x) / distance * overlap / 2
                        move_y = (player.y - other_player.y) / distance * overlap / 2
                        player.x += move_x if player.x + move_x >= 15 and player.x + move_x <= screen_width - 15 else 0
                        player.y += move_y if player.y + move_y >= 15 and player.y + move_y <= screen_height - 15 else 0
                        other_player.x -= move_x if other_player.x - move_x >= 15 and other_player.x - move_x <= screen_width - 15 else 0
                        other_player.y -= move_y if other_player.y - move_y >= 15 and other_player.y - move_y <= screen_height - 15 else 0

class Player:
    def __init__(self, id, x, y, color):
        self.id = id
        self.x = x
        self.y = y
        self.color = color
        self.holding_ball = False
        self.holding_ball_since = 0
        self.ball = None
        self.speed = 10
        self.throw_strength = 10

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)

    def handle_input(self, action:list[float]):
        if (abs(action[0])>1 or abs(action[1])>1 or abs(action[2])>1 or abs(action[3])>1):
            print(action)
            raise ValueError("Invalid action")
        if not self.holding_ball:
            if self.x + action[0] >= 15 and self.x + action[0] <= screen_width - 15:
                self.x += action[0] * self.speed

            if self.y + action[1] >= 15 and self.y + action[1] <= screen_height - 15:
                self.y += action[1] * self.speed

        if action[2]**2 + action[3]**2 > 0.25 and self.holding_ball and self.ball.heldBy == self:
            direction = np.arctan2(action[2], action[3])
            magnitude = np.sqrt(action[2]**2 + action[3]**2)
            self.throw_ball(direction, magnitude)

    def throw_ball(self, direction, magnitude):
        self.holding_ball = False
        self.holding_ball_since = 0
        self.ball.velocityVector.magnitude = magnitude * self.throw_strength
        self.ball.velocityVector.direction = direction
        self.ball.velocityVector.updateCartesian()
        self.ball.x += 30 * np.cos(direction)
        self.ball.y += 30 * np.sin(direction)
        self.ball.heldBy = None
        self.ball = None
        
    
    def update_holding_ball_since(self):
        if self.holding_ball:
            self.holding_ball_since += 1

class Vector:
    def __init__(self, type, a, b):
        if type == "polar":
            self.magnitude = a
            self.direction = b
            self.updateCartesian()
        elif type == "cartesian":
            self.x = a
            self.y = b
            self.updatePolar()
        else:
            raise ValueError("Invalid vector type")
        
    def updatePolar(self):
        self.magnitude = np.sqrt(self.x ** 2 + self.y ** 2)
        self.direction = np.arctan2(self.y, self.x)

    def updateCartesian(self):
        self.x = self.magnitude * np.cos(self.direction)
        self.y = self.magnitude * np.sin(self.direction)

if __name__ == "__main__":
    game = Game(screen_width, screen_height)
    game.run()
