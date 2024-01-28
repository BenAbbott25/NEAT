import colorsys
import pygame
import numpy as np
import time

class Game:
    def __init__(self, frames_x, frames_y, num_planets, fuel, players, start_point, end_point, planets, catchment_range, gen_list):
        self.frames_x = frames_x
        self.frames_y = frames_y

        self.is_game_over = False
        self.end_all = False

        self.fitnesses = {}
        self.catchment_range = catchment_range

        self.start_point = start_point
        self.end_point = end_point

        self.planets = []
        for planet in planets:
            self.planets.append(Planet(planet[0], planet[1], planet[2]))
        
        self.players = []
        self.playerSensors = {}
        for player_id in players:
            self.players.append(Player(self, player_id, self.start_point[0], self.start_point[1], 5, 15, 15, fuel))
            self.playerSensors[player_id] = np.zeros(11 + 3*num_planets)

        self.init_fuel = fuel

        if len(gen_list) > 1:
            self.gen_list = gen_list = ', '.join([str(gen) for gen in gen_list])
            pygame.display.set_caption(f"Generations {self.gen_list}")
        else:
            self.gen_list = gen_list = gen_list[0]
            pygame.display.set_caption(f"Generation {self.gen_list}")

        self.screen = pygame.display.set_mode((frames_x, frames_y))
        pygame.init()

    # draw gravity feild, colour for direction and brightness for magnitude
    def draw_bg(self):
        bg = pygame.Surface((self.frames_x, self.frames_y))
        for x in range(5, self.frames_x):
            for y in range(self.frames_y):
                total_gravity_dx = 0
                total_gravity_dy = 0
                for planet in self.planets:
                    dx = planet.x - x
                    dy = planet.y - y
                    if dx == 0 and dy == 0:
                        continue
                    distance = np.sqrt(dx**2 + dy**2)
                    gravity = planet.mass / distance**2
                    gravity_dx = gravity * dx / distance
                    gravity_dy = gravity * dy / distance
                    total_gravity_dx += gravity_dx / 10
                    total_gravity_dy += gravity_dy / 10
                total_gravity_angle = np.arctan2(total_gravity_dy, total_gravity_dx)
                total_gravity_magnitude = np.sqrt(total_gravity_dx**2 + total_gravity_dy**2)

                colour = (int(255 * (total_gravity_angle + np.pi) / (2*np.pi)), int(255 * (total_gravity_angle + np.pi) / (2*np.pi)), int(255 * (total_gravity_angle + np.pi) / (2*np.pi)))
                brightness = min(int(255 * total_gravity_magnitude * 3), 255)

                colourHSV = (((total_gravity_angle) / (2*np.pi))*360, 1, 1)
                # print(f'colourHSL: {colourHSV}')
                colourRGB = colorsys.hsv_to_rgb(*colourHSV)
                # print(f'colourRGB: {colourRGB}')
                
                bg.set_at((x, y), colourRGB)
        self.screen.blit(bg, (0, 0))
            

    def draw(self):
        self.screen.fill((0, 0, 0))
        # self.draw_bg()
        for player in self.players:
            player.draw(self.screen)
        for planet in self.planets:
            planet.draw(self.screen)

        pygame.draw.circle(self.screen, (0, 255, 0), (self.start_point[0], self.start_point[1]), 5)
        pygame.draw.circle(self.screen, (255, 0, 0), (self.end_point[0], self.end_point[1]), 5)
        pygame.draw.circle(self.screen, (255, 0, 0), (self.end_point[0], self.end_point[1]), max(self.catchment_range,0)+5, 1)
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

        for planet in self.planets:
            planet.check_gravity()
            planet.move()

    def run(self, playerInputs):
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

    def setTitle(self, title):
        print(title)
        pygame.display.set_caption(title)

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
        init_vector_angle = np.arctan2(dy, dx)
        self.movementVector = Vector(0,0)
        self.inputVector = radVector(init_vector_angle,0)
        self.mass = mass
        self.fastest_speed = 0
        self.max_speed = max_speed
        self.max_thrust = max_thrust
        self.fitness = 0
        self.fuel = fuel
        self.total_gravity_angle = 0
        self.total_gravity_magnitude = 0
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

        # gravity vector in blue
        start_x = self.x + 15 * np.cos(self.total_gravity_angle)
        start_y = self.y + 15 * np.sin(self.total_gravity_angle)
        end_x = self.x + min((100*self.total_gravity_magnitude) + 15, 50) * np.cos(self.total_gravity_angle)
        end_y = self.y + min((100*self.total_gravity_magnitude) + 15, 50) * np.sin(self.total_gravity_angle)
        pygame.draw.line(screen, (0, 0, 255), (start_x, start_y), (end_x, end_y))


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
        
        self.inputVector.update()
        self.movementVector.dx += self.inputVector.dx/1000
        self.movementVector.dy += self.inputVector.dy/1000

        self.fastest_speed = max(self.fastest_speed, np.sqrt(self.movementVector.dx**2 + self.movementVector.dy**2))


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
        if np.sqrt((self.x - self.game.end_point[0])**2 + (self.y - self.game.end_point[1])**2) < self.mass + 5 + self.game.catchment_range:
            self.fitness += 10 * self.fuel/self.game.init_fuel
            self.remove()
        if self.x == 0 or self.x == self.game.frames_x or self.y == 0 or self.y == self.game.frames_y:
            self.fuel -= 10

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

        scaled_x = x / self.game.frames_x - 0.5
        scaled_y = y / self.game.frames_y - 0.5

        movement_vector_x = self.movementVector.dx
        movement_vector_y = self.movementVector.dy
        movement_vector_angle = np.arctan2(movement_vector_y, movement_vector_x)
        movement_vector_magnitude = np.sqrt(movement_vector_x**2 + movement_vector_y**2)

        # input_vector_x = self.inputVector.dx
        # input_vector_y = self.inputVector.dy
        input_vector_angle = self.inputVector.angle
        input_vector_magnitude = self.inputVector.magnitude

        # mass = self.mass
        # max_thrust = self.max_thrust
        # max_speed = self.max_speed
        fuel = self.fuel/self.game.init_fuel

        end_point_x = self.game.end_point[0]
        end_point_y = self.game.end_point[1]
        end_point_angle = np.arctan2(end_point_y - y, end_point_x - x)
        end_point_distance = np.sqrt((end_point_x - x)**2 + (end_point_y - y)**2)
        
        sensor_data = [
            scaled_x,
            scaled_y,
            movement_vector_angle,
            movement_vector_magnitude,
            input_vector_angle,
            input_vector_magnitude,
            fuel,
            end_point_angle,
            end_point_distance
        ]

        self.total_gravity_dx = 0
        self.total_gravity_dy = 0
        for planet in self.game.planets:
            dx = planet.x - self.x
            dy = planet.y - self.y
            distance = np.sqrt(dx**2 + dy**2)
            gravity = planet.mass / distance**2
            gravity_dx = gravity * dx / distance
            gravity_dy = gravity * dy / distance
            gravity_angle = np.arctan2(gravity_dy, gravity_dx)
            gravity_magnitude = np.sqrt(gravity_dx**2 + gravity_dy**2)
            self.total_gravity_dx += gravity_dx
            self.total_gravity_dy += gravity_dy
            sensor_data.append(gravity_angle)
            sensor_data.append(gravity_magnitude)
            sensor_data.append(planet.mass/1800)
        self.total_gravity_angle = np.arctan2(self.total_gravity_dy, self.total_gravity_dx)
        self.total_gravity_magnitude = np.sqrt(self.total_gravity_dx**2 + self.total_gravity_dy**2)
        sensor_data.append(self.total_gravity_angle)
        sensor_data.append(self.total_gravity_magnitude)

        self.game.playerSensors[self.player_id] = sensor_data

    def update_min_distance(self):
            current_distance = np.sqrt((self.x - self.game.end_point[0])**2 + (self.y - self.game.end_point[1])**2)
            if current_distance < self.min_distance:
                self.min_distance = current_distance

    def update_fitness(self):
        initial_distance = np.sqrt((self.game.start_point[0] - self.game.end_point[0])**2 + (self.game.start_point[1] - self.game.end_point[1])**2) * 0.9
        current_distance = np.sqrt((self.x - self.game.end_point[0])**2 + (self.y - self.game.end_point[1])**2)
        self.fitness += 5*(initial_distance / current_distance) + self.fuel/self.game.init_fuel + (initial_distance / self.min_distance) + (self.fastest_speed / self.max_speed)
        # print(f"player {self.player_id} fitness: {self.fitness}")


class Planet:
    def __init__(self, init_x, init_y, mass):
        self.x = init_x
        self.y = init_y
        self.mass = mass

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.mass/100)

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


