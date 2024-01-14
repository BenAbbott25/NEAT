import pygame, sys
import numpy as np

class Game:
    def __init__(self, frame_x, frame_y, players):
        self.frame_size_x = frame_x
        self.frame_size_y = frame_y
        self.title = "Shooter"
        self.is_game_over = False
        self.num_players = len(players)
        self.players = []
        self.id = 0
        for player in players:
            self.players.append(Player(0, np.random.randint(0,frame_x), np.random.randint(0,frame_y), (255, 255, 255), 0.0, 10, 2)) 
            self.id += 1
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
        for player in self.players:
            player.draw(self.game_window)
        for bullet in self.bullets:
            bullet.draw(self.game_window) 
        pygame.display.update()

    def run(self):
        while not self.is_game_over:
            # self.fps_controller.tick(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over()
            for player in self.players:
                player.moveTurnAndShoot()
                player.update()
            for bullet in self.bullets:
                bullet.update()
            self.update()
            self.draw()

    def update(self):
        pass

    def calculate_fitness(self):
        fitnesses = {}
        for player in self.players:
            player.fitness = player.health + 10 * player.kill_count
            fitnesses.append(player.id, player.fitness)
        

    def game_over(self):
        pygame.quit()
        sys.exit()



class Player:
    def __init__(self, id, x, y, color, direction, size, speed, health=100):
        self.id = id
        self.x = x
        self.y = y
        self.color = color
        self.direction = direction
        self.size = size
        self.speed = speed
        self.health = health
        self.reload_time = 0
        self.reload_max = 50
        self.kill_count = 0

    def moveAndTurn(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed

        if keys[pygame.K_LEFT]:
            self.direction -= self.speed
        if keys[pygame.K_RIGHT]:
            self.direction += self.speed
        if self.direction > 360:
            self.direction = 0
        if self.direction < 0:
            self.direction = 360

        if keys[pygame.K_SPACE] and self.reload_time == 0:
            game.bullets.append(Bullet(self.x, self.y, self.direction, self))
            self.reload_time = self.reload_max
        elif self.reload_time > 0:
            self.reload_time -= 1

    def draw(self, game_window):
        pygame.draw.circle(game_window, self.color, (self.x, self.y), self.size, 1)
        dx = 10 * np.cos(np.radians(self.direction))
        dy = 10 * np.sin(np.radians(self.direction))
        pygame.draw.line(game_window, self.color, (self.x, self.y), (self.x + dx, self.y + dy), 1)

    def update(self):        
        self.moveAndTurn()
        self.shoot()
        self.checkCollision()
        self.checkOutOfBounds()
        self.checkHit()
        self.checkDeath()

    def checkCollision(self):
        pass

    def checkOutOfBounds(self):
        if self.x < 0:
            self.x = 0
        if self.x > game.frame_size_x:
            self.x = game.frame_size_x
        if self.y < 0:
            self.y = 0
        if self.y > game.frame_size_y:
            self.y = game.frame_size_y

    def checkHit(self):
        pass

    def checkDeath(self):
        if self.health <= 0:
            game.players.remove(self)

class Bullet:
    def __init__(self, x, y, direction, source, speed=10, size=5):
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
        self.draw(game.game_window)

    def checkOutOfBounds(self):
        if self.x < 0 or self.x > game.frame_size_x or self.y < 0 or self.y > game.frame_size_y:
            game.bullets.remove(self)

    def checkHit(self):
        for player in [p for p in game.players if p != self.source]:
            if self.x > player.x - player.size and self.x < player.x + player.size:
                if self.y > player.y - player.size and self.y < player.y + player.size:
                    player.health -= 10
                    if player.health <= 0:
                        self.source.kill_count += 1
                    game.bullets.remove(self)
        

    def checkDeath(self):
        pass

game = Game(720, 480, [1,2,3,4])
game.run() 