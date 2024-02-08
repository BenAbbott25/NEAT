import pygame
import numpy as np

frames_x = 1440
frames_y = 900

class Game:
    def __init__(self, frames_x, frames_y):
        self.frames_x = frames_x
        self.frames_y = frames_y

        self.course = Course(frames_x, frames_y)
        self.start = (self.course.points[0][0], self.course.points[0][1])
        self.driver = Driver(self.start[0], self.start[1], self.course.checkpoints[0].angle)
        

    def draw(self, screen):
        self.course.draw(screen)
        self.driver.draw(screen)

class Checkpoint:
    def __init__(self, index, position, angle, angle_derivative):
        self.index = index
        self.position = position
        self.angle = angle
        self.angle_derivative = angle_derivative
        self.width = min(max(angle_derivative, 15), 50)
        print(f"Index: {self.index},Width: {self.width}, Angle Derivative: {self.angle_derivative}")
        self.left_position = (self.position[0] + np.cos(self.angle + np.pi/2)*self.width, self.position[1] + np.sin(self.angle + np.pi/2)*self.width)
        self.right_position = (self.position[0] + np.cos(self.angle - np.pi/2)*self.width, self.position[1] + np.sin(self.angle - np.pi/2)*self.width)

    def draw(self, screen):
        color = (255, 0, 0) if self.index == 0 else (0, 255, 0)
        if self.index % 10 == 0:
            pygame.draw.line(screen, color, self.left_position, self.right_position)
            yellow = (255, 255, 0)
            end_mid = (self.position[0] + np.cos(self.angle)*15, self.position[1] + np.sin(self.angle)*15)
            end_left = (self.position[0] + np.cos(self.angle + np.pi/8)*10, self.position[1] + np.sin(self.angle + np.pi/8)*10)
            end_right = (self.position[0] + np.cos(self.angle - np.pi/8)*10, self.position[1] + np.sin(self.angle - np.pi/8)*10)
            pygame.draw.line(screen, yellow, self.position, end_mid)
            pygame.draw.line(screen, yellow, end_mid, end_left)
            pygame.draw.line(screen, yellow, end_mid, end_right)
        
class Course:
    def __init__(self, frames_x, frames_y):
        self.frames_x = frames_x
        self.frames_y = frames_y

        t = 0
        self.points = []
        while t <= 2 * np.pi:
            x = 500 * np.cos(t) + frames_x / 2
            y = 250 * np.sin(2*t) + frames_y / 2
            self.points.append([x, y])
            t += 0.005 * np.pi

        self.checkpoints = []
        for i in range(len(self.points) - 1):
            dx = self.points[i+1][0] - self.points[i][0]
            dy = self.points[i+1][1] - self.points[i][1]
            angle = np.arctan2(dy, dx)
            
            previous_dx = self.points[i][0] - self.points[i-1][0]
            previous_dy = self.points[i][1] - self.points[i-1][1]
            angle0 = np.arctan2(previous_dy, previous_dx)
            angle_derivative = np.sin(abs(angle0- angle)) * 1000
            
            self.checkpoints.append(Checkpoint(i, self.points[i], angle, angle_derivative))

        # smooth width changes
        for i in range(len(self.checkpoints)-1):
            if self.checkpoints[i].width < self.checkpoints[i-1].width and self.checkpoints[i].width < self.checkpoints[i+1].width:
                self.checkpoints[i].width = (self.checkpoints[i-1].width + self.checkpoints[i+1].width) / 2
                self.checkpoints[i].left_position = (self.checkpoints[i].position[0] + np.cos(self.checkpoints[i].angle + np.pi/2)*self.checkpoints[i].width, self.checkpoints[i].position[1] + np.sin(self.checkpoints[i].angle + np.pi/2)*self.checkpoints[i].width)
                self.checkpoints[i].right_position = (self.checkpoints[i].position[0] + np.cos(self.checkpoints[i].angle - np.pi/2)*self.checkpoints[i].width, self.checkpoints[i].position[1] + np.sin(self.checkpoints[i].angle - np.pi/2)*self.checkpoints[i].width)

        

    def draw(self, screen):
        for checkpoint in self.checkpoints:
            checkpoint.draw(screen)
        
        for i in range(len(self.checkpoints)):
            pygame.draw.line(screen, (255, 255, 255), self.checkpoints[i-1].left_position, self.checkpoints[i].left_position)
            pygame.draw.line(screen, (255, 255, 255), self.checkpoints[i-1].right_position, self.checkpoints[i].right_position)

class Driver:
    def __init__(self, x, y, angle, speed=0, steering=0, max_speed=200, max_steering=1):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.steering = steering
        self.max_speed = max_speed
        self.max_steering = max_steering
        self.update_corners()

    def update_corners(self):
        self.front_left = (self.x + np.cos(self.angle + np.pi/6)*10, self.y + np.sin(self.angle + np.pi/6)*10)
        self.front_right = (self.x + np.cos(self.angle - np.pi/6)*10, self.y + np.sin(self.angle - np.pi/6)*10)
        self.back_left = (self.x + np.cos(self.angle + np.pi + np.pi/6)*10, self.y + np.sin(self.angle + np.pi + np.pi/6)*10)
        self.back_right = (self.x + np.cos(self.angle + np.pi - np.pi/6)*10, self.y + np.sin(self.angle + np.pi - np.pi/6)*10)

    def draw(self, screen):
        pygame.draw.polygon(screen, (255, 255, 255), [self.front_left, self.front_right, self.back_left, self.back_right])

    def move(self):
        dx = np.cos(self.angle) * self.speed
        dy = np.sin(self.angle) * self.speed
        self.x += dx
        self.y += dy
        if self.speed > 0.1:
            self.angle += self.steering/100
        self.speed *= 0.995
        self.steering *= 0.95
        self.update_corners()

    def accelerate(self, acceleration):
        self.speed += acceleration
        self.speed = max(0, min(self.speed, self.max_speed))

    def turn(self, dtheta):
        self.steering += dtheta
        self.steering = max(-self.max_steering, min(self.steering, self.max_steering))



def main():
    pygame.init()
    screen = pygame.display.set_mode((frames_x, frames_y))
    pygame.display.set_caption("Orbits")

    game = Game(frames_x, frames_y)

    running = True
    while running:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            game.driver.turn(-1)
        if keys[pygame.K_RIGHT]:
            game.driver.turn(1)
        if keys[pygame.K_UP]:
            game.driver.accelerate(0.01)
        if keys[pygame.K_DOWN]:
            game.driver.accelerate(-0.1)

        game.driver.move()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((40, 40, 40))
        game.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()