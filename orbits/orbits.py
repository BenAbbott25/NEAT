import pygame
import numpy as np
import time

class Game:
    def __init__(self, frames_x, frames_y):
        self.frames_x = frames_x
        self.frames_y = frames_y

        self.is_game_over = False

        self.start_point = [np.random.randint(0,frames_x), np.random.randint(0,frames_y)]
        self.end_point = [np.random.randint(0,frames_x), np.random.randint(0,frames_y)]

        self.player = Player(self, self.start_point[0], self.start_point[1], Vector(0,0), 5, 10, 10)
        self.planets = [Planet(np.random.randint(0,frames_x), np.random.randint(0,frames_y), 1000) for _ in range(0)]

        self.screen = pygame.display.set_mode((frames_x, frames_y))
        pygame.init()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.player.draw(self.screen)
        for planet in self.planets:
            planet.draw(self.screen)

        pygame.draw.circle(self.screen, (255, 0, 0), (self.end_point[0], self.end_point[1]), 5)
        pygame.display.flip()

    def update(self):
        self.check_gravity()
        self.check_collision()
        self.player.handle_input()
        self.player.move()

    def run(self):
        while not self.is_game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over()
            self.update()
            self.draw()

    def check_collision(self):
        for planet in self.planets:
            if np.sqrt((self.player.x - planet.x)**2 + (self.player.y - planet.y)**2) < self.player.mass + planet.mass/100:
                print(f"COLLISION with planet at {planet.x}, {planet.y}" )
                self.game_over()
        if np.sqrt((self.player.x - self.end_point[0])**2 + (self.player.y - self.end_point[1])**2) < self.player.mass:
            print("VICTORY! Reached the endpoint.")
            self.game_over()

    def check_gravity(self):
        total_gravity_dx = 0
        total_gravity_dy = 0
        for planet in self.planets:
            dx = planet.x - self.player.x
            dy = planet.y - self.player.y
            distance = np.sqrt(dx**2 + dy**2)
            gravity = planet.mass / distance**2
            gravity_dx = gravity * dx / distance
            gravity_dy = gravity * dy / distance
            total_gravity_dx += gravity_dx / 10
            total_gravity_dy += gravity_dy / 10
        self.player.accelerate(total_gravity_dx, total_gravity_dy)

    def get_sensor_data(self, player):
        player_x = player.x
        player_y = player.y
        player_vector_dx = player.vector.dx
        player_vector_dy = player.vector.dy
        player_mass = player.mass
        player_max_speed = player.max_speed
        end_point_x = self.end_point[0]
        end_point_y = self.end_point[1]


    def calculate_fitness(self):
        distance = np.sqrt((self.player.x - self.end_point[0])**2 + (self.player.y - self.end_point[1])**2)
        print(f"Distance to end point: {distance}")
        print(f"Fitness: {1 / distance}")
        print(-1 * np.log(distance/1000))
        return 1 / distance
    
    def game_over(self):
        self.calculate_fitness()
        self.is_game_over = True




class Player:
    def __init__(self, game, init_x, init_y, init_vector, mass, max_speed, max_thrust):
        self.x = init_x
        self.y = init_y
        self.movementVector = init_vector
        self.inputVector = radVector(0,0)
        self.mass = mass
        self.game = game
        self.max_speed = max_speed
        self.max_thrust = max_thrust
        self.fitness = 0
        # self.fuel = 10000

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.mass)
        self.draw_vector(screen)
    
    def draw_vector(self, screen):
        # convert to radians and magnitude
        vector_magnitude = np.sqrt(self.movementVector.dx ** 2 + self.movementVector.dy ** 2)
        vector_angle = np.arctan2(self.movementVector.dy, self.movementVector.dx)
        start_x = self.x + 15 * np.cos(vector_angle)
        start_y = self.y + 15 * np.sin(vector_angle)
        end_x = self.x + (vector_magnitude + 1.5) * np.cos(vector_angle) * 10
        end_y = self.y + (vector_magnitude + 1.5) * np.sin(vector_angle) * 10
        pygame.draw.line(screen, (255, 255, 255), (start_x, start_y), (end_x, end_y))

        self.inputVector.update()
        input_vector_magnitude = np.sqrt(self.inputVector.dx ** 2 + self.inputVector.dy ** 2)
        input_vector_angle = np.arctan2(self.inputVector.dy, self.inputVector.dx)
        start_x = self.x + 15 * np.cos(input_vector_angle)
        start_y = self.y + 15 * np.sin(input_vector_angle)
        end_x = start_x + (input_vector_magnitude + 15) * np.cos(input_vector_angle)
        end_y = start_y + (input_vector_magnitude + 15) * np.sin(input_vector_angle)
        pygame.draw.line(screen, (255, 255, 0), (start_x, start_y), (end_x, end_y))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.inputVector.magnitude < self.max_thrust:
            self.inputVector.magnitude += 1
        if keys[pygame.K_DOWN] and self.inputVector.magnitude > 0:
            self.inputVector.magnitude -= 1
        if keys[pygame.K_LEFT]:
            self.inputVector.angle -= 0.1
        if keys[pygame.K_RIGHT]:
            self.inputVector.angle += 0.1

        self.movementVector.dx += self.inputVector.dx/1000
        self.movementVector.dy += self.inputVector.dy/1000


    def accelerate(self, ddx, ddy):
        self.movementVector.dx += ddx
        self.movementVector.dy += ddy
        if self.movementVector.dx ** 2 + self.movementVector.dy ** 2 > self.max_speed ** 2:
            self.movementVector.dx *= self.max_speed / np.sqrt(self.movementVector.dx ** 2 + self.movementVector.dy ** 2)
            self.movementVector.dy *= self.max_speed / np.sqrt(self.movementVector.dx ** 2 + self.movementVector.dy ** 2)

    def move(self):
        self.x += self.movementVector.dx
        self.y += self.movementVector.dy

        if self.x < 0:
            self.x = 0
        if self.x > self.game.frames_x:
            self.x = self.game.frames_x
        if self.y < 0:
            self.y = 0
        if self.y > self.game.frames_y:
            self.y = self.game.frames_y

class Planet:
    def __init__(self, init_x, init_y, mass):
        self.x = init_x
        self.y = init_y
        self.mass = mass

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.mass/100)


class Vector:
    def __init__(self, init_dx, init_dy):
        self.dx = init_dx
        self.dy = init_dy

class radVector:
    def __init__(self, init_angle, init_magnitude):
        self.angle = init_angle
        self.magnitude = init_magnitude

        self.dx = self.magnitude * np.cos(self.angle)
        self.dy = self.magnitude * np.sin(self.angle)

    def update(self):
        self.dx = self.magnitude * np.cos(self.angle)
        self.dy = self.magnitude * np.sin(self.angle)

game = Game(720, 480)
game.run()