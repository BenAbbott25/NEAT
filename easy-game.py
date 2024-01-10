import pygame, sys

frame_size_x = 720
frame_size_y = 480

class Game:
    def __init__(self, frame_size_x, frame_size_y, rect1, rect2):
        self.frame_size_x = frame_size_x
        self.frame_size_y = frame_size_y
        self.start_x, self.start_y = rect1
        self.rect1_x, self.rect1_y = rect1
        self.rect2_x, self.rect2_y = rect2
        self.frames = frame_size_x

        # Initialize pygame window
        pygame.init()
        self.game_window = pygame.display.set_mode((frame_size_x, frame_size_y))

        # Initialize the two rectangles
        self.rect1 = pygame.Rect(self.rect1_x, self.rect1_y, 10, 10)
        self.rect2 = pygame.Rect(self.rect2_x, self.rect2_y, 10, 10)

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.rect1.move_ip(0, -10)
                    self.rect1_y -= 10
                elif event.key == pygame.K_DOWN:
                    self.rect1.move_ip(0, 10)
                    self.rect1_y += 10
                elif event.key == pygame.K_LEFT:
                    self.rect1.move_ip(-10, 0)
                    self.rect1_x -= 10
                elif event.key == pygame.K_RIGHT:
                    self.rect1.move_ip(10, 0)
                    self.rect1_x += 10

    def fitness(self):
        rect_distance = ((self.rect1_x - self.rect2_x)**2 + (self.rect1_y - self.rect2_y)**2)**0.5
        dist_from_start = ((self.rect1_x - self.start_x)**2 + (self.rect1_y - self.start_y)**2)**0.5

        print("Distance from start: ", dist_from_start)
        print("Distance between rectangles: ", rect_distance)

        return dist_from_start - rect_distance


    def run(self):
        while self.frames > 0:
            self.handle_keys()
            print("Fitness: ", self.fitness())

            # Fill the screen with black
            self.game_window.fill((0, 0, 0))

            # Draw the rectangles
            pygame.draw.rect(self.game_window, (255, 0, 0), self.rect1)
            pygame.draw.rect(self.game_window, (0, 255, 0), self.rect2)

            # draw a bar showing remaining frames
            pygame.draw.rect(self.game_window, (255, 255, 255), pygame.Rect(0, 0, self.frames, 10))

            # Victory condition
            if self.rect1.colliderect(self.rect2):
                print("Victory!")
                pygame.quit()
                sys.exit()

            pygame.display.update()
            self.frames -= 1

game = Game(frame_size_x, frame_size_y, (50, 50), (200, 200))
game.run()
