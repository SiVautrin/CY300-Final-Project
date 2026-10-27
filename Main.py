import pygame

from Game import Game


WIDTH, HEIGHT = 800, 600


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rock, Paper, Magic")

    try:
        Game(screen).run()
    finally:
        # Main owns Pygame shutdown so it also happens if the game exits with an error.
        pygame.quit()


if __name__ == "__main__":
    main()
