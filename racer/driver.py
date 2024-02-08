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

