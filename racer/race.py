import pygame
import numpy as np
from driver import Driver

frames_x = 1280
frames_y = 720

class Game:
    def __init__(self, frames_x, frames_y, drivers):
        self.frames_x = frames_x
        self.frames_y = frames_y

        self.fitnesses = {}

        self.course = Course(frames_x, frames_y)
        self.start = (self.course.points[0][0], self.course.points[0][1])
        self.drivers = []
        self.driverSensors = {}
        # self.drivers = [Driver(self, genomeId, self.start[0], self.start[1], self.course.checkpoints[0].angle, self.course.checkpoints[0].index) for genomeId in drivers]
        for driver in drivers:
            self.drivers.append(Driver(driver, self, self.start[0], self.start[1], self.course.checkpoints[0].angle, self.course.checkpoints[0].index))
            self.driverSensors[driver] = np.zeros(12)

        self.screen = pygame.display.set_mode((frames_x, frames_y))

        self.is_game_over = False

    def draw(self, screen):
        self.course.draw(screen)
        for driver in self.drivers:
            driver.draw(screen)

    def update(self):
        for driver in self.drivers:
            driver.move()
            driver.check_next_checkpoint()
            driver.check_collision()
            if driver.time_since_last_checkpoint > 1000:
                self.drivers.remove(driver)
                self.fitnesses[driver.id] = driver.fitness
                print(f"Driver {driver.id} fitness: {driver.fitness}")
        if len(self.drivers) == 0:
            self.is_game_over = True
            return
        

    def run(self, playerInputs):
        self.update()
        for driver in self.drivers:
            driverInputs = playerInputs[driver.id]
            driver.handle_input(driverInputs)
            driver.update()
            self.driverSensors[driver.id] = driver.get_sensors()
        self.draw(self.screen)
    
    def get_fitnesses(self):
        return self.fitnesses

    def get_sensor_data(self, driver_id):
        return self.driverSensors[driver_id]

class Checkpoint:
    def __init__(self, index, position, angle, angle_derivative):
        self.index = index
        self.position = position
        self.angle = angle
        self.angle_derivative = angle_derivative
        self.width = min(max(angle_derivative, 15), 50)
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((frames_x, frames_y))
    pygame.display.set_caption("Orbits")

    game = Game(frames_x, frames_y)

    running = True
    while running:
        for driver in game.drivers:
            driver.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((40, 40, 40))
        game.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()