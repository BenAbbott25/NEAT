import numpy as np
import pygame

class Driver:
    def __init__(self, genomeId, game, x, y, angle, checkpoint, colour, max_speed=10, max_steering=1):
        self.game = game
        self.id = genomeId
        self.x = x
        self.y = y
        self.angle = angle
        self.checkpoint = checkpoint
        self.slice = checkpoint
        self.speed = 0
        self.steering = 0
        self.max_speed = max_speed
        self.max_steering = max_steering
        self.color = colour
        self.time_since_last_checkpoint = 0
        self.max_time_since_last_checkpoint = 100
        self.fitness = 0

        self.update_corners()

    def update_corners(self):
        self.front_left = (self.x + np.cos(self.angle + np.pi/6)*10, self.y + np.sin(self.angle + np.pi/6)*10)
        self.front_right = (self.x + np.cos(self.angle - np.pi/6)*10, self.y + np.sin(self.angle - np.pi/6)*10)
        self.back_left = (self.x + np.cos(self.angle + np.pi + np.pi/6)*10, self.y + np.sin(self.angle + np.pi + np.pi/6)*10)
        self.back_right = (self.x + np.cos(self.angle + np.pi - np.pi/6)*10, self.y + np.sin(self.angle + np.pi - np.pi/6)*10)

    def update(self):
        self.update_corners()
        self.move()
        self.check_next_checkpoint()
        self.check_collision()
        if self.time_since_last_checkpoint > self.max_time_since_last_checkpoint:
            self.crash()
        self.time_since_last_checkpoint += 1

    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, [self.front_left, self.front_right, self.back_left, self.back_right])
        self.draw_checkpoint_timer_bar(screen)

    def draw_checkpoint_timer_bar(self, screen):
        time_percentage = self.time_since_last_checkpoint / self.max_time_since_last_checkpoint
        bar_width = self.game.frames_x
        bar_height = 20
        timer_bar_position = (0, 0)
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(timer_bar_position[0], timer_bar_position[1], bar_width * (1 - time_percentage), bar_height/2))

    def move(self):
        dx = np.cos(self.angle) * self.speed
        dy = np.sin(self.angle) * self.speed

        if self.speed > self.max_speed * 0.8:
            self.angle += self.steering / 10
            dx += np.cos(self.angle - self.steering) * self.speed / 5
            dy += np.sin(self.angle - self.steering) * self.speed / 5

        self.x += dx
        self.y += dy
        self.speed *= 0.995
        self.steering *= 0.95
        self.update_corners()

    def accelerate(self, acceleration):
        self.speed += acceleration
        self.speed = max(-self.speed/10, min(self.speed, self.max_speed))

    def turn(self, dtheta):
        self.steering += dtheta
        self.steering = max(-self.max_steering, min(self.steering, self.max_steering))

    def crash(self):
        self.game.fitnesses[self.id] = self.fitness - self.time_since_last_checkpoint/100
        if self in self.game.drivers:
            self.game.drivers.remove(self)

    def check_next_checkpoint(self):
        checkpointIndex = self.checkpoint
        next_checkpoint = self.game.course.checkpoints[checkpointIndex]
        checkpoint_line = [next_checkpoint.left_position, next_checkpoint.right_position]

        car_lines = [
            [self.front_left, self.back_left], # left
            [self.front_right, self.back_right], # right
            [self.front_left, self.front_right], # front
            [self.back_left, self.back_right] # back
        ]

        for car_line in car_lines:
            if self.intersect(car_line, checkpoint_line):
                self.checkpoint += 10
                self.fitness += 1
                self.checkpoint %= len(self.game.course.checkpoints)
                self.time_since_last_checkpoint = 0
                return
    
    def handle_input(self, inputs):
        acceleration = inputs[0]
        steering = inputs[1]
        self.accelerate(acceleration)
        self.turn(steering)

    def get_sensors(self):
        # speed, angle, acceleration, steering, distance and angle to next 3 checkpoints center, left and right
        
        sensors = [
            self.checkpoint,
            self.speed,
            self.angle,
            self.steering,
        ]
        
        sensepoints = [
            self.game.course.checkpoints[self.checkpoint].position, # next checkpoint
            self.game.course.checkpoints[self.checkpoint].left_position, # next checkpoint left
            self.game.course.checkpoints[self.checkpoint].right_position, # next checkpoint right
            self.game.course.checkpoints[(self.checkpoint + 10) % len(self.game.course.checkpoints)].position, # next next checkpoint
            self.game.course.checkpoints[(self.checkpoint - 10) % len(self.game.course.checkpoints)].position, # previous checkpoint
            self.game.course.checkpoints[(self.checkpoint - 10) % len(self.game.course.checkpoints)].left_position, # previous checkpoint left
            self.game.course.checkpoints[(self.checkpoint - 10) % len(self.game.course.checkpoints)].right_position # previous checkpoint right
        ]

        for point in sensepoints:
            dx = point[0] - self.x
            dy = point[1] - self.y
            distance = np.sqrt(dx**2 + dy**2)
            angle = np.arctan2(dy, dx)
            sensors.append(distance)
            sensors.append(angle)

        return np.array(sensors)

    def check_collision(self):
        if self.x < 0 or self.x > self.game.frames_x or self.y < 0 or self.y > self.game.frames_y:
            self.crash()
            return

        if self.checkpoint != 0:
            points = [[checkpoint.left_position, checkpoint.right_position] for checkpoint in self.game.course.checkpoints if checkpoint.index < self.checkpoint + 50 and checkpoint.index > self.checkpoint - 50]
        else:
            points = [[checkpoint.left_position, checkpoint.right_position] for checkpoint in self.game.course.checkpoints if checkpoint.index < 50 or checkpoint.index > len(self.game.course.checkpoints) - 50]

        self.update_corners()
        car_lines = [
            [self.front_left, self.back_left], # left
            [self.front_right, self.back_right], # right
            [self.front_left, self.front_right], # front
            [self.back_left, self.back_right] # back
        ]

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i+1]

            wall_lines = [
                [p1[0], p2[0]], # left wall
                [p1[1], p2[1]] # right wall
            ]

            for car_line in car_lines:
                for wall_line in wall_lines:
                    if self.intersect(car_line, wall_line):
                        self.crash()
                        return

    def intersect(self, line1, line2):
        x1, y1 = line1[0]
        x2, y2 = line1[1]
        x3, y3 = line2[0]
        x4, y4 = line2[1]

        def ccw(x1, y1, x2, y2, x3, y3):
            return (y3 - y1) * (x2 - x1) > (y2 - y1) * (x3 - x1)
        
        return ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4)