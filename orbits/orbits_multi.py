import pygame
import numpy as np
import time

class Game:
    def __init__(self, frames_x, frames_y, num_planets, fuel, players):
        self.frames_x = frames_x
        self.frames_y = frames_y

        self.is_game_over = False
        self.end_all = False

        self.fitnesses = {}

        # split into 4 quadrants and place start and end points in different quadrants
        end_quadrant_x = np.random.randint(0,2)
        end_quadrant_y = np.random.randint(0,2)
        start_quadrant_x = np.random.randint(0,2)
        start_quadrant_y = np.random.randint(0,2)

        if end_quadrant_x == start_quadrant_x and end_quadrant_y == start_quadrant_y:
            end_quadrant_x = 1 - end_quadrant_x
            end_quadrant_y = 1 - end_quadrant_y

        self.quadrant_start_point = [np.random.randint(int(np.floor(frames_x*0.1/4)),int(np.ceil(frames_x*0.9/4))), np.random.randint(int(np.floor(frames_y*0.1/4)),int(np.ceil(frames_y*0.9/4)))]
        self.quadrant_end_point = [np.random.randint(int(np.floor(frames_x*0.1/4)),int(np.ceil(frames_x*0.9/4))), np.random.randint(int(np.floor(frames_y*0.1/4)),int(np.ceil(frames_y*0.9/4)))]

        self.start_point = [self.quadrant_start_point[0] + start_quadrant_x * frames_x/2, self.quadrant_start_point[1] + start_quadrant_y * frames_y/2]
        self.end_point = [self.quadrant_end_point[0] + end_quadrant_x * frames_x/2, self.quadrant_end_point[1] + end_quadrant_y * frames_y/2]

        # self.start_point = [frames_x/4, frames_y/2]
        # self.end_point = [frames_x*3/4, frames_y/2]

        self.players = []
        self.playerSensors = {}
        for player_id in players:
            self.players.append(Player(self, player_id, self.start_point[0], self.start_point[1], 5, 10, 10, fuel))
            self.playerSensors[player_id] = np.zeros(12 + 2*num_planets)
        self.planets = []
        for i in range(num_planets):
            planet_x = np.random.randint(int(np.floor(frames_x*0.1)),int(np.ceil(frames_x*0.9)))
            planet_y = np.random.randint(int(np.floor(frames_y*0.1)),int(np.ceil(frames_y*0.9)))
            while np.sqrt((planet_x - self.start_point[0])**2 + (planet_y - self.start_point[1])**2) < 100 or np.sqrt((planet_x - self.end_point[0])**2 + (planet_y - self.end_point[1])**2) < 100:
                planet_x = np.random.randint(int(np.floor(frames_x*0.1)),int(np.ceil(frames_x*0.9)))
                planet_y = np.random.randint(int(np.floor(frames_y*0.1)),int(np.ceil(frames_y*0.9)))
            self.planets.append(Planet(planet_x, planet_y, np.random.randint(800,1800)))
        # self.planets = [Planet(frames_x/2, frames_y*(i+0.5)/num_planets, 1000) for i in range(num_planets)]

        self.init_fuel = fuel

        self.screen = pygame.display.set_mode((frames_x, frames_y))
        pygame.init()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for player in self.players:
            player.draw(self.screen)
        for planet in self.planets:
            planet.draw(self.screen)

        pygame.draw.circle(self.screen, (0, 255, 0), (self.start_point[0], self.start_point[1]), 5)
        pygame.draw.circle(self.screen, (255, 0, 0), (self.end_point[0], self.end_point[1]), 5)
        pygame.display.flip()

    def update(self):
        for player in self.players:
            player.check_gravity()
            player.check_collision()
            player.check_fuel()
            player.checkSensors()
            player.move()
            player.update_min_distance()
            player.fuel -= player.inputVector.magnitude / player.max_thrust
            player.fuel -= 1

    def run(self, playerInputs):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end_all = True
                self.game_over()
        for player in self.players:
            inputs = playerInputs[player.player_id]
            player.handle_input(inputs)
        self.update()
        self.draw()
        self.check_game_over()

    def get_sensor_data(self, player_id):
        return self.playerSensors[player_id]
    
    def get_fitnesses(self):
        return self.fitnesses
    
    def check_game_over(self):
        if len(self.players) == 0:
            self.game_over()

    def game_over(self):
        self.is_game_over = True

class Player:
    def __init__(self, game, id, init_x, init_y, mass, max_speed, max_thrust, fuel=10000):
        self.player_id = id
        self.x = init_x
        self.y = init_y
        self.game = game
        # dx = self.game.end_point[0] - self.x
        # dy = self.game.end_point[1] - self.y
        dx = self.game.frames_x/2 - self.x
        dy = self.game.frames_y/2 - self.y
        init_vector_angle = np.arctan2(dy, dx) + np.random.uniform(-0.1, 0.1)
        self.movementVector = Vector(0,0)
        self.inputVector = radVector(init_vector_angle,0)
        self.mass = mass
        self.max_speed = max_speed
        self.max_thrust = max_thrust
        self.fitness = 0
        self.fuel = fuel
        self.min_distance = np.sqrt((self.game.start_point[0] - self.game.end_point[0])**2 + (self.game.start_point[1] - self.game.end_point[1])**2)

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

        self.inputVector.angle += max(min(angle_input, 0.2), -0.2)
        self.inputVector.magnitude += max(min(thrust_input, 1), -1)
        if self.inputVector.magnitude > self.max_thrust:
            self.inputVector.magnitude = self.max_thrust
        if self.inputVector.magnitude < 0:
            self.inputVector.magnitude = 0
        
        self.fuel -= abs(self.inputVector.angle)
        
        self.inputVector.update()
        self.movementVector.dx += self.inputVector.dx/1000
        self.movementVector.dy += self.inputVector.dy/1000


    def accelerate(self, ddx, ddy):
        self.movementVector.dx += ddx / self.mass
        self.movementVector.dy += ddy / self.mass
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


    def check_collision(self):
        for planet in self.game.planets:
            if np.sqrt((self.x - planet.x)**2 + (self.y - planet.y)**2) < self.mass + planet.mass/100:
                self.fitness -= 10 * self.fuel/self.game.init_fuel
                self.remove()
        if np.sqrt((self.x - self.game.end_point[0])**2 + (self.y - self.game.end_point[1])**2) < self.mass + 5:
            self.fitness += 10 * self.fuel/self.game.init_fuel
            self.remove()

    def check_gravity(self):
        total_gravity_dx = 0
        total_gravity_dy = 0
        for planet in self.game.planets:
            dx = planet.x - self.x
            dy = planet.y - self.y
            distance = np.sqrt(dx**2 + dy**2)
            gravity = planet.mass / distance**2
            gravity_dx = gravity * dx / distance
            gravity_dy = gravity * dy / distance
            total_gravity_dx += gravity_dx / 10
            total_gravity_dy += gravity_dy / 10
        self.accelerate(total_gravity_dx, total_gravity_dy)

    def check_fuel(self):
        if self.fuel <= 0:
            self.remove()

    def remove(self):
        self.update_fitness()
        self.game.fitnesses[self.player_id] = self.fitness
        if self in self.game.players:
            self.game.players.remove(self)

    def checkSensors(self):
        x = self.x
        y = self.y
        movement_vector_x = self.movementVector.dx
        movement_vector_y = self.movementVector.dy
        input_vector_x = self.inputVector.dx
        input_vector_y = self.inputVector.dy
        mass = self.mass
        max_thrust = self.max_thrust
        max_speed = self.max_speed
        fuel = self.fuel/self.game.init_fuel
        end_point_x = self.game.end_point[0]
        end_point_y = self.game.end_point[1]
        
        sensor_data = [x, y, movement_vector_x, movement_vector_y, input_vector_x, input_vector_y, mass, max_thrust, max_speed, fuel, end_point_x, end_point_y]

        for planet in self.game.planets:
            dx = planet.x - self.x
            dy = planet.y - self.y
            distance = np.sqrt(dx**2 + dy**2)
            gravity = planet.mass / distance**2
            gravity_dx = gravity * dx / distance
            gravity_dy = gravity * dy / distance
            sensor_data.extend([gravity_dx, gravity_dy])

        self.game.playerSensors[self.player_id] = sensor_data

    def update_min_distance(self):
            current_distance = np.sqrt((self.x - self.game.end_point[0])**2 + (self.y - self.game.end_point[1])**2)
            if current_distance < self.min_distance:
                self.min_distance = current_distance

    def update_fitness(self):
        initial_distance = np.sqrt((self.game.start_point[0] - self.game.end_point[0])**2 + (self.game.start_point[1] - self.game.end_point[1])**2) * 0.9
        current_distance = np.sqrt((self.x - self.game.end_point[0])**2 + (self.y - self.game.end_point[1])**2)
        self.fitness += initial_distance / current_distance + self.fuel/self.game.init_fuel + (initial_distance / self.min_distance)/2
        # print(f"player {self.player_id} fitness: {self.fitness}")


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

