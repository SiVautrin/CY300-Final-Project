import pygame
from Player import Player
from Spell import Spell #list of spells

# --- Config ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# --- Player Creation ---











def main():
    # 1. Init
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("My Game")
    clock = pygame.time.Clock()

    running = True
    # 2. Game loop
    while running:
        dt = clock.tick(FPS) / 1000  # seconds since last frame

        # 3. Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # 4. Update game state
        # (move things using dt here)

        # 5. Draw
        screen.fill((30, 30, 40))
        # (draw things here)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()