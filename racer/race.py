import pygame
import numpy as np

frames_x = 1080
frames_y = 720

class Game:
    def __init__(self, frames_x, frames_y):
        self.frames_x = frames_x
        self.frames_y = frames_y

        self.course = Course(frames_x, frames_y)

    def draw(self, screen):
        self.course.draw(screen)

class Checkpoint:
    def __init__(self, index, position, angle):
        self.index = index
        self.position = position
        self.angle = angle
        self.width = 10
        self.left_position = (self.position[0] + np.cos(self.angle + np.pi/2)*self.width, self.position[1] + np.sin(self.angle + np.pi/2)*self.width)
        self.right_position = (self.position[0] + np.cos(self.angle - np.pi/2)*self.width, self.position[1] + np.sin(self.angle - np.pi/2)*self.width)

    def draw(self, screen):
        end_position = (self.position[0] + np.cos(self.angle)*50, self.position[1] + np.sin(self.angle)*50)
        pygame.draw.line(screen, (255, 0, 0), self.position, end_position)
        pygame.draw.line(screen, (0, 255, 0), self.left_position, self.right_position)
        

class Course:
    def __init__(self, frames_x, frames_y):
        self.frames_x = frames_x
        self.frames_y = frames_y

        t = 0
        self.points = []
        while t < 2.1 * np.pi:
            x = 300 * np.cos(t) + frames_x / 2
            y = 300 * np.sin(2*t) + frames_y / 2
            self.points.append([x, y])
            t += 0.1 * np.pi

        self.checkpoints = []
        for i in range(len(self.points) - 1):
            dx = self.points[i+1][0] - self.points[i][0]
            dy = self.points[i+1][1] - self.points[i][1]
            angle = np.arctan2(dy, dx)
            self.checkpoints.append(Checkpoint(i, self.points[i], angle))

        for checkpoint in self.checkpoints:
            print(f"Index: {checkpoint.index}, Position: {checkpoint.position}, Angle: {checkpoint.angle}")

        

    def draw(self, screen):
        for i in range(len(self.points) - 1):
            pygame.draw.line(screen, (255, 255, 255), self.points[i], self.points[i+1])

        for checkpoint in self.checkpoints:
            checkpoint.draw(screen)
        
        for i in range(len(self.checkpoints) - 1):
            pygame.draw.line(screen, (255, 255, 255), self.checkpoints[i].left_position, self.checkpoints[i+1].left_position)
            pygame.draw.line(screen, (255, 255, 255), self.checkpoints[i].right_position, self.checkpoints[i+1].right_position)
        pygame.draw.line(screen, (255, 255, 255), self.checkpoints[-1].left_position, self.checkpoints[0].left_position)
        pygame.draw.line(screen, (255, 255, 255), self.checkpoints[-1].right_position, self.checkpoints[0].right_position)

def main():
    pygame.init()
    screen = pygame.display.set_mode((frames_x, frames_y))
    pygame.display.set_caption("Orbits")

    game = Game(frames_x, frames_y)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 0, 0))
        game.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()