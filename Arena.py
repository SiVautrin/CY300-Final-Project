"""
Provides the Arena class responsible for drawing the game's screens and feedback
without changing the game state.
"""

import math

import pygame


class Arena:
    """Draw the game's screens and feedback without changing game state."""

    WIDTH = 800
    HEIGHT = 600

    BACKGROUND = (32, 38, 48)
    PANEL = (48, 57, 69)
    TEXT = (245, 239, 220)
    MUTED_TEXT = (190, 195, 199)
    PARCHMENT = (232, 214, 174)
    HP_BACK = (104, 55, 59)
    HP_FILL = (69, 166, 104)

    ELEMENT_COLORS = {
        "FIRE": (231, 103, 55),
        "WIND": (115, 204, 207),
        "EARTH": (144, 117, 75),
    }

    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.Font(None, 48)
        self.heading_font = pygame.font.Font(None, 34)
        self.body_font = pygame.font.Font(None, 27)
        self.small_font = pygame.font.Font(None, 22)

    def draw_arena(self, players, round_number=None):
        """Draw the shared background, player labels, and HP bars."""
        self.screen.fill(self.BACKGROUND)
        pygame.draw.rect(self.screen, self.PANEL, (18, 16, 764, 72), border_radius=12)
        pygame.draw.rect(self.screen, self.PANEL, (18, 512, 764, 72), border_radius=12)

        self._draw_player_status(players[0], (36, 24), 1)
        self._draw_player_status(players[1], (36, 520), 2)

        if round_number is not None:
            self._draw_text(
                f"ROUND {round_number}",
                (self.WIDTH // 2, 52),
                self.small_font,
                self.MUTED_TEXT,
                center=True,
            )

        # A subtle divider frames the central play area.
        pygame.draw.line(self.screen, (75, 85, 96), (42, 105), (758, 105), 2)
        pygame.draw.line(self.screen, (75, 85, 96), (42, 496), (758, 496), 2)

    def draw_countdown(self, seconds_remaining, round_number=None):
        """Show the ready countdown between rounds."""
        if round_number is not None:
            self._draw_text(
                f"ROUND {round_number}",
                (self.WIDTH // 2, 190),
                self.body_font,
                self.MUTED_TEXT,
                center=True,
            )
        self._draw_text(
            "GET READY",
            (self.WIDTH // 2, 255),
            self.title_font,
            self.TEXT,
            center=True,
        )
        count = max(0, math.ceil(seconds_remaining))
        self._draw_text(
            str(count),
            (self.WIDTH // 2, 335),
            pygame.font.Font(None, 96),
            (239, 191, 92),
            center=True,
        )

    def draw_drawing(self, players, active_player, canvas, round_number):
        """Show only the active player's drawing surface before the arena."""
        self.draw_arena(players, round_number)
        self._draw_text(
            f"{active_player.name}: select ink and draw",
            (self.WIDTH // 2, 123),
            self.heading_font,
            self.TEXT,
            center=True,
        )
        canvas.draw(self.screen, self.body_font)

    def draw_handoff(self, next_player):
        """Prompt the players to switch before showing the second drawing screen."""
        self._draw_text(
            f"Pass to {next_player.name}",
            (self.WIDTH // 2, 250),
            self.title_font,
            self.TEXT,
            center=True,
        )
        self._draw_text(
            "Press SPACE when ready",
            (self.WIDTH // 2, 310),
            self.body_font,
            self.MUTED_TEXT,
            center=True,
        )

    def _draw_spell_arena(self, players, spells, round_number):
        pygame.draw.rect(self.screen, self.PANEL, (30, 120, 740, 370), border_radius=12)
        self._draw_text(
            f"ARENA  |  ROUND {round_number}",
            (self.WIDTH // 2, 151),
            self.heading_font,
            self.TEXT,
            center=True,
        )
        pygame.draw.line(self.screen, (75, 85, 96), (400, 180), (400, 395), 2)

        for index, (player, spell) in enumerate(zip(players, spells)):
            x = 230 if index == 0 else 570
            self._draw_text(
                player.name,
                (x, 205),
                self.body_font,
                self.TEXT,
                center=True,
            )
            if spell is not None:
                self._draw_spell_effect(spell, (x, 290))

    def draw_results(self, players, spells, hp_changes, round_number):
        """Reveal the arena and both spells after both players have cast."""
        self._draw_spell_arena(players, spells, round_number)

        for index, (player, hp_change) in enumerate(zip(players, hp_changes)):
            x = 230 if index == 0 else 570
            self._draw_text(
                f"{hp_change:+.1f} HP  |  {player.hp:.1f}/{player.max_hp:.1f}",
                (x, 415),
                self.small_font,
                self.TEXT,
                center=True,
            )

        self._draw_text(
            "Next round begins shortly",
            (self.WIDTH // 2, 455),
            self.small_font,
            self.MUTED_TEXT,
            center=True,
        )

    def draw_game_over(self, winner, players, spells=None, hp_changes=None, round_number=None):
        """Declare the winner/draw and show rematch and quit controls."""
        if spells is not None:
            self._draw_spell_arena(players, spells, round_number)
        if hp_changes is not None:
            for index, (player, hp_change) in enumerate(zip(players, hp_changes)):
                x = 230 if index == 0 else 570
                self._draw_text(
                    f"{hp_change:+.1f} HP  |  {player.hp:.1f}/{player.max_hp:.1f}",
                    (x, 415),
                    self.small_font,
                    self.TEXT,
                    center=True,
                )

        if winner == "DRAW":
            message = "THE MATCH IS A DRAW"
            color = (239, 191, 92)
        else:
            message = f"{winner.name.upper()} WINS!"
            color = self.TEXT

        self._draw_text(
            message,
            (self.WIDTH // 2, 452),
            self.heading_font,
            color,
            center=True,
        )
        self._draw_text(
            "Press R to rematch  |  Q or ESC to quit",
            (self.WIDTH // 2, 480),
            self.small_font,
            self.MUTED_TEXT,
            center=True,
        )

    def _draw_player_status(self, player, position, player_number):
        x, y = position
        self._draw_text(
            f"PLAYER {player_number}  |  {player.name}",
            (x, y),
            self.body_font,
            self.TEXT,
        )

        bar_rect = pygame.Rect(x, y + 32, 280, 18)
        pygame.draw.rect(self.screen, self.HP_BACK, bar_rect, border_radius=8)
        hp_fraction = max(0.0, min(1.0, player.hp / player.max_hp))
        fill_rect = bar_rect.copy()
        fill_rect.width = round(bar_rect.width * hp_fraction)
        if fill_rect.width:
            pygame.draw.rect(
                self.screen,
                self.HP_FILL,
                fill_rect,
                border_radius=8,
            )
        pygame.draw.rect(
            self.screen,
            (220, 220, 210),
            bar_rect,
            width=1,
            border_radius=8,
        )
        self._draw_text(
            f"{player.hp:.1f}/{player.max_hp:.1f} HP",
            (x + 300, y + 31),
            self.small_font,
            self.TEXT,
        )

    def _draw_spell_effect(self, spell, center):
        x, y = center
        if spell.is_fizzle():
            pygame.draw.circle(self.screen, (100, 105, 113), center, 48, 3)
            pygame.draw.line(self.screen, (225, 105, 99), (x - 25, y - 25), (x + 25, y + 25), 6)
            pygame.draw.line(self.screen, (225, 105, 99), (x + 25, y - 25), (x - 25, y + 25), 6)
            self._draw_text("FIZZLE", (x, y + 65), self.small_font, (225, 135, 125), center=True)
            return

        color = self.ELEMENT_COLORS.get(spell.element, self.TEXT)
        pygame.draw.circle(self.screen, color, center, 48, 3)

        if spell.element == "FIRE":
            points = [
                (x, y - 32),
                (x + 24, y - 4),
                (x + 16, y + 25),
                (x, y + 35),
                (x - 20, y + 20),
                (x - 24, y - 4),
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, (255, 205, 115), [(x, y + 18), (x + 10, y - 2), (x - 8, y + 3)])
        elif spell.element == "WIND":
            for offset in (-14, 0, 14):
                pygame.draw.arc(
                    self.screen,
                    color,
                    (x - 30, y - 18 + offset, 60, 30),
                    math.radians(15),
                    math.radians(165),
                    4,
                )
        else:
            rock = [(x - 26, y + 18), (x - 20, y - 15), (x, y - 30), (x + 25, y - 12), (x + 28, y + 18), (x + 8, y + 29)]
            pygame.draw.polygon(self.screen, color, rock)
            pygame.draw.polygon(self.screen, (205, 185, 140), rock, 2)

        label = spell.spell_type.capitalize()
        self._draw_text(label, (x, y + 67), self.small_font, self.TEXT, center=True)

    def _draw_text(self, message, position, font, color, center=False):
        text_surface = font.render(message, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = position
        else:
            text_rect.topleft = position
        self.screen.blit(text_surface, text_rect)
