import pygame
import numpy as np
import time

class Game:
    def __init__(self, frames_x, frames_y, num_planets=0, fuel=10000):
        self.frames_x = frames_x
        self.frames_y = frames_y

        self.is_game_over = False
        self.end_all = False

        self.start_point = [np.random.randint(int(np.floor(frames_x*0.1)),int(np.ceil(frames_x*0.9))), np.random.randint(int(np.floor(frames_y*0.1)),int(np.ceil(frames_y*0.9)))]
        self.end_point = [np.random.randint(int(np.floor(frames_x*0.1)),int(np.ceil(frames_x*0.9))), np.random.randint(int(np.floor(frames_y*0.1)),int(np.ceil(frames_y*0.9)))]
        while np.sqrt((self.start_point[0] - self.end_point[0])**2 + (self.start_point[1] - self.end_point[1])**2) < 500:
            self.end_point = [np.random.randint(int(np.floor(frames_x*0.1)),int(np.ceil(frames_x*0.9))), np.random.randint(int(np.floor(frames_y*0.1)),int(np.ceil(frames_y*0.9)))]

        self.player = Player(self, self.start_point[0], self.start_point[1], 5, 10, 10, fuel)
        self.planets = [Planet(np.random.randint(int(np.floor(frames_x*0.1)),int(np.ceil(frames_x*0.9))), np.random.randint(int(np.floor(frames_y*0.1)),int(np.ceil(frames_y*0.9))), 1000) for _ in range(num_planets)]

        self.init_fuel = fuel

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
        self.check_fuel()
        self.player.move()
        # if self.player.inputVector.magnitude > 0:
        #     print(f"M:{self.player.inputVector.magnitude}, A:{self.player.inputVector.angle}")
        self.player.fuel -= self.player.inputVector.magnitude / self.player.max_thrust
        self.player.fuel -= 1

    def run(self, inputs):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end_all = True
                self.game_over()
        self.player.handle_input(inputs)
        self.update()
        self.draw()

    def check_collision(self):
        for planet in self.planets:
            if np.sqrt((self.player.x - planet.x)**2 + (self.player.y - planet.y)**2) < self.player.mass + planet.mass/100:
                self.player.fitness -= 2
                self.game_over()
        if np.sqrt((self.player.x - self.end_point[0])**2 + (self.player.y - self.end_point[1])**2) < self.player.mass:
            # print("VICTORY! Reached the endpoint.")
            self.player.fitness += 2
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

    def check_fuel(self):
        if self.player.fuel <= 0:
            self.game_over()

    def get_sensor_data(self, player):
        player_x = player.x
        player_y = player.y
        movement_vector_x = player.movementVector.dx
        movement_vector_y = player.movementVector.dy
        input_vector_x = player.inputVector.dx
        input_vector_y = player.inputVector.dy
        player_mass = player.mass
        max_thrust = player.max_thrust
        max_speed = player.max_speed
        fuel = player.fuel/self.init_fuel
        end_point_x = self.end_point[0]
        end_point_y = self.end_point[1]
        
        return [player_x, player_y, movement_vector_x, movement_vector_y, input_vector_x, input_vector_y, player_mass, max_thrust, max_speed, fuel, end_point_x, end_point_y]

    def calculate_fitness(self):
        initial_distance = np.sqrt((self.start_point[0] - self.end_point[0])**2 + (self.start_point[1] - self.end_point[1])**2)
        distance = np.sqrt((self.player.x - self.end_point[0])**2 + (self.player.y - self.end_point[1])**2)
        df = initial_distance / distance + self.player.fuel/self.init_fuel
        self.player.fitness += df
        return self.player.fitness
    
    def game_over(self):
        self.is_game_over = True

class Player:
    def __init__(self, game, init_x, init_y, mass, max_speed, max_thrust, fuel=10000):
        self.x = init_x
        self.y = init_y
        self.movementVector = Vector(0,0)
        self.inputVector = radVector(0,0)
        self.mass = mass
        self.game = game
        self.max_speed = max_speed
        self.max_thrust = max_thrust
        self.fitness = 0
        self.fuel = fuel

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.mass)
        self.draw_vector(screen)
        self.draw_fuel(screen)
    
    def draw_vector(self, screen):
        # convert to radians and magnitude
        vector_magnitude = np.sqrt(self.movementVector.dx ** 2 + self.movementVector.dy ** 2)
        if vector_magnitude > 0:
            vector_angle = np.arctan2(self.movementVector.dy, self.movementVector.dx)
            start_x = self.x + 15 * np.cos(vector_angle)
            start_y = self.y + 15 * np.sin(vector_angle)
            end_x = self.x + (vector_magnitude + 1.5) * np.cos(vector_angle) * 10
            end_y = self.y + (vector_magnitude + 1.5) * np.sin(vector_angle) * 10
            pygame.draw.line(screen, (255, 255, 255), (start_x, start_y), (end_x, end_y))


        self.inputVector.update()
        # print(f"Angle: {self.inputVector.angle}, Magnitude: {self.inputVector.magnitude}")
        start_x = self.x + 15 * np.cos(self.inputVector.angle)
        start_y = self.y + 15 * np.sin(self.inputVector.angle)
        end_x = self.x + (self.inputVector.magnitude + 15) * np.cos(self.inputVector.angle)
        end_y = self.y + (self.inputVector.magnitude + 15) * np.sin(self.inputVector.angle)
        pygame.draw.line(screen, (255, 255, 0), (start_x, start_y), (end_x, end_y))


    def draw_fuel(self, screen):
        fuel_percentage = self.fuel / self.game.init_fuel
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(0, 0, self.game.frames_x, 5))
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(0, 0, self.game.frames_x * fuel_percentage, 5))

    def handle_input(self, inputs):
        angle_input = inputs[0]
        thrust_input = inputs[1]

        # print(f"Angle: {angle_input}, Thrust: {thrust_input}")
        # print(f"Angle change: {np.tanh(angle_input)/10}, Thrust change: {np.tanh(thrust_input)/10}")

        self.inputVector.angle += max(min(angle_input/10, 0.1), -0.1)
        self.inputVector.magnitude += max(min(thrust_input/10, 0.1), -0.1)
        if self.inputVector.magnitude > self.max_thrust:
            self.inputVector.magnitude = self.max_thrust
        if self.inputVector.magnitude < 0:
            self.inputVector.magnitude = 0
        
        self.inputVector.update()
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

# game = Game(720, 480, 0, 10000)
# game.run()