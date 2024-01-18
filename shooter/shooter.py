import pygame, sys
import numpy as np
import time

class Game:
    def __init__(self, frame_x, frame_y, players):
        self.frame_size_x = frame_x
        self.frame_size_y = frame_y
        self.title = "Shooter"
        self.is_game_over = False
        self.num_players = len(players)
        self.players = []
        self.timer = 250
        self.max_timer = 250
        self.playerSensors = {}
        for player in players:
            self.players.append(Player(self, player, np.random.randint(0,frame_x), np.random.randint(0,frame_y), (255, 255, 255), 0.0, 10, 3)) 
            self.playerSensors[player] = np.zeros(12)
        self.bullets = []

         # Checks for errors encountered
        check_errors = pygame.init()
        # pygame.init() example output -> (6, 0)
        # second number in tuple gives number of errors
        if check_errors[1] > 0:
            print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
            sys.exit(-1)
        # else:
            # print('[+] Game successfully initialised')


        # Initialise game window
        pygame.display.set_caption(self.title)
        self.game_window = pygame.display.set_mode((self.frame_size_x, self.frame_size_y))


        # Colors (R, G, B)
        self.black = pygame.Color(0, 0, 0)
        self.white = pygame.Color(255, 255, 255)
        self.red = pygame.Color(255, 0, 0)
        self.green = pygame.Color(0, 255, 0)
        self.blue = pygame.Color(0, 0, 255)


        # FPS (frames per second) controller
        self.fps_controller = pygame.time.Clock()

    def draw(self):
        self.game_window.fill(self.black)

        # Draw timer bar at the top of the screen
        remaining_time_ratio = max(0, self.timer / self.max_timer)
        pygame.draw.rect(self.game_window, self.green, pygame.Rect(0, 0, self.frame_size_x * remaining_time_ratio, 20))

        for player in self.players:
            player.draw(self.game_window)
        for bullet in self.bullets:
            bullet.draw(self.game_window) 

        pygame.display.update()

    def run(self, playerInputs):
        while not self.is_game_over:
            if len(self.players) == 1 or self.timer <= 0:
                self.game_over()
            # self.fps_controller.tick(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over()
            for player in self.players:
                inputs = playerInputs[player.id]
                player.moveTurnAndShoot(inputs)
                player.update()
            for bullet in self.bullets:
                bullet.update()
            self.update()
            self.draw()
            self.timer -= 1

    def get_vision(self, id):
        return self.playerSensors[id]

    def update(self):
        pass

    def calculate_fitness(self):
        fitnesses = {}
        for player in self.players:
            edge_penalty = 1000 if player.x == 0 or player.y == 0 or player.x == self.frame_size_x or player.y == self.frame_size_y else 0
            no_movement_penalty = 1000 if player.steps == 0 else 0
            player.fitness = player.health/10 + 10 * player.kill_count + player.steps/100 - edge_penalty - no_movement_penalty
            fitnesses[player.id] = player.fitness
        return fitnesses
        

    def game_over(self):
        self.is_game_over = True
        # pygame.quit()
        # sys.exit()



class Player:
    def __init__(self, game, id, x, y, color, direction, size, speed, health=100):
        self.game = game
        self.id = id
        self.x = x
        self.y = y
        self.color = color
        self.direction = direction
        self.size = size
        self.speed = speed
        self.health = health
        self.reload_time = 0
        self.reload_max = 25
        self.kill_count = 0
        self.fitness = 0
        self.sensors = [0 for _ in range(13)]
        self.steps = 0
        self.shotsFired = 0

    def moveTurnAndShoot(self, inputs):
        # up, down, left, right, shoot
        if inputs[0] > 0.75:
            self.y -= self.speed
        if inputs[1] > 0.75:
            self.y += self.speed
        if inputs[2] > 0.75:
            self.x -= self.speed
        if inputs[3] > 0.75:
            self.x += self.speed

        if inputs[0] > 0.75 or inputs[1] > 0.75 or inputs[2] > 0.75 or inputs[3] > 0.75:
            if self.x != self.game.frame_size_x and self.x != 0 and self.y != self.game.frame_size_y and self.y != 0:
                self.steps += 1

        # rotating
        if inputs[4] > 0.75:
            self.direction -= self.speed * 2
        if inputs[5] > 0.75:
            self.direction += self.speed * 2
        if self.direction > 360:
            self.direction = 0
        if self.direction < 0:
            self.direction = 360

        if inputs[6] > 0.75 and self.reload_time == 0:
            self.game.bullets.append(Bullet(self.game, self.x, self.y, self.direction, self))
            self.reload_time = self.reload_max
            self.shotsFired += 1
        elif self.reload_time > 0:
            self.reload_time -= 1

    def draw(self, game_window):
        pygame.draw.circle(game_window, self.color, (self.x, self.y), self.size, 1)
        dx = 10 * np.cos(np.radians(self.direction))
        dy = 10 * np.sin(np.radians(self.direction))
        if self.sensors[5] > 0.0:
            color = (255, 0, 0, 50)
        else:
            color = (255, 255, 255, 50)
        pygame.draw.line(game_window, self.color, (self.x, self.y), (self.x + dx, self.y + dy), 1)
        semi_transparent_circle = pygame.Surface((200,200), pygame.SRCALPHA)  # per-pixel alpha
        pygame.draw.circle(semi_transparent_circle, color, (100, 100), 100)  # alpha level
        game_window.blit(semi_transparent_circle, (self.x-100, self.y-100))

    def update(self):        
        # self.moveTurnAndShoot()
        self.checkSensors()
        self.checkCollision()
        self.checkOutOfBounds()
        self.checkHit()
        self.checkDeath()

    def checkSensors(self):
        # x, y, direction, health, reload_time, players_within_100_px, 
        # the remaining sensors give the result of a raycast in 30 degree increments from -90 to 90 degrees
        self.sensors[0] = self.x
        self.sensors[1] = self.y
        self.sensors[2] = self.direction
        self.sensors[3] = self.health
        self.sensors[4] = self.reload_time
        players_within_100_px = 0.0
        for player in self.game.players:
            if player != self:
                # print(player.x, player.y)
                # print(self.x, self.y)
                distance = np.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
                if distance < 100.0:
                    players_within_100_px += 1.0
        self.sensors[5] = players_within_100_px
        # raycast
        for i in range(-90, 91, 30):
            dx = np.cos(np.radians(self.direction + i))
            dy = np.sin(np.radians(self.direction + i))
            for distance in range(1, 501, 50):
                x = self.x + distance * dx
                y = self.y + distance * dy
                for player in [p for p in self.game.players if p != self]:
                    if x > player.x - player.size - 50 and x < player.x + player.size + 50:
                        if y > player.y - player.size - 50 and y < player.y + player.size + 50:
                            self.sensors[i//30 + 9] = distance/100
                            break
        
        self.game.playerSensors[self.id] = self.sensors
        

    def checkCollision(self):
        pass

    def checkOutOfBounds(self):
        if self.x < 0:
            self.x = 0
        if self.x > self.game.frame_size_x:
            self.x = self.game.frame_size_x
        if self.y < 0:
            self.y = 0
        if self.y > self.game.frame_size_y:
            self.y = self.game.frame_size_y

    def checkHit(self):
        pass

    def checkDeath(self):
        if self.health <= 0:
            self.game.players.remove(self)
            self.game.timer = self.game.max_timer

class Bullet:
    def __init__(self, game, x, y, direction, source, speed=10, size=5):
        self.game = game
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.size = size
        self.source = source

    def move(self):
        dx = self.speed * np.cos(np.radians(self.direction))
        dy = self.speed * np.sin(np.radians(self.direction))
        self.x += dx
        self.y += dy

    def draw(self, game_window):
        # pygame.draw.circle(game_window, (255, 255, 255), (self.x, self.y), self.size)
        dx = 10 * np.cos(np.radians(self.direction))
        dy = 10 * np.sin(np.radians(self.direction))
        pygame.draw.line(game_window, (255, 255, 255), (self.x, self.y), (self.x + dx, self.y + dy), 1)

    def update(self):
        self.move()
        self.checkOutOfBounds()
        self.checkHit()
        self.draw(self.game.game_window)

    def checkOutOfBounds(self):
        if self.x < 0 or self.x > self.game.frame_size_x or self.y < 0 or self.y > self.game.frame_size_y:
            self.game.bullets.remove(self)

    def checkHit(self):
        for player in [p for p in self.game.players if p != self.source]:
            if self.x > player.x - player.size and self.x < player.x + player.size:
                if self.y > player.y - player.size and self.y < player.y + player.size:
                    player.health -= 100
                    if player.health <= 0:
                        self.source.kill_count += 1
                    if self in self.game.bullets:
                        self.game.bullets.remove(self)
        

    def checkDeath(self):
        pass

# game = Game(720, 480, [1,2,3,4])
# game.run(np.zeros((4, 7)))