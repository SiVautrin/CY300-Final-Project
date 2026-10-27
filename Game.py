"""Coordinate turns, spell recognition, combat, and the game loop."""

import pygame

from Arena import Arena
from CombatResolver import CombatResolver
from DrawingCanvas import DrawingCanvas
from Player import Player
from StrokeRecognizer import StrokeRecognizer


class Game:
    COUNTDOWN = "COUNTDOWN"
    DRAWING = "DRAWING"
    HANDOFF = "HANDOFF"
    RESULTS = "RESULTS"
    GAME_OVER = "GAME_OVER"

    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FPS = 60
    ROUND_COUNTDOWN_SECONDS = 5
    RESULTS_SECONDS = 3
    STARTING_HP = 100

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.stroke_recognizer = StrokeRecognizer()
        self.combat_resolver = CombatResolver()
        self.arena = Arena(screen)
        self.canvas = DrawingCanvas(
            canvas_rect=(150, 180, 500, 250),
            cast_button_rect=(560, 445, 90, 45),
            clear_button_rect=(450, 445, 90, 45),
        )

        self.reset_match()

    def run(self):
        """Run the event, update, and drawing cycle until the user quits."""
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_event(event)

            self.update(dt)
            self.draw()
            pygame.display.flip()

    def handle_event(self, event):
        """Send input to the active stage of the game."""
        if self.current_state == self.DRAWING:
            if self.canvas.handle_mouse(event):
                self._submit_current_spell()

        elif self.current_state == self.HANDOFF:
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
            ):
                self.current_player_index = 1
                self.change_state(self.DRAWING)

        elif self.current_state == self.GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_match()
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    self.running = False

    def update(self, dt):
        """Advance countdowns and automatically continue after round results."""
        if self.current_state == self.COUNTDOWN:
            self.countdown_timer = max(0.0, self.countdown_timer - dt)
            if self.countdown_timer == 0:
                self.change_state(self.DRAWING)

        elif self.current_state == self.RESULTS:
            self.results_timer = max(0.0, self.results_timer - dt)
            if self.results_timer == 0:
                self._start_next_round()

    def _submit_current_spell(self):
        """Recognize and store one player's drawing, then advance the turn."""
        if self.canvas.selected_ink is None:
            raise RuntimeError("Choose an ink color before casting a spell.")
        stroke = self.canvas.get_stroke()
        spell = self.stroke_recognizer.recognize(
            stroke,
            self.canvas.selected_ink,
        )
        self.pending_spells[self.current_player_index] = spell
        self.players[self.current_player_index].record_accuracy(spell.accuracy)

        if self.current_player_index == 0:
            # Remove Player 1's drawing before passing the device to Player 2.
            self.canvas.clear()
            self.change_state(self.HANDOFF)
        else:
            self.resolve_round()

    def resolve_round(self):
        """Apply both spell effects together and decide whether the match ended."""
        spell1, spell2 = self.pending_spells
        if spell1 is None or spell2 is None:
            raise RuntimeError("Both players must submit a spell before resolution.")

        hp_change1, hp_change2 = self.combat_resolver.resolve(spell1, spell2)
        self.last_hp_changes = (hp_change1, hp_change2)

        for player, hp_change in zip(self.players, self.last_hp_changes):
            if hp_change < 0:
                player.take_damage(abs(hp_change))
            elif hp_change > 0:
                player.heal(hp_change)

        self.winner = self.check_winner()
        if self.winner is not None:
            self.change_state(self.GAME_OVER)
        else:
            self.change_state(self.RESULTS)

    def check_winner(self):
        """Return a winning Player, 'DRAW', or None while the match continues."""
        player1_defeated = self.players[0].is_defeated()
        player2_defeated = self.players[1].is_defeated()

        if not player1_defeated and not player2_defeated:
            return None
        if player1_defeated and not player2_defeated:
            return self.players[1]
        if player2_defeated and not player1_defeated:
            return self.players[0]

        accuracy1 = self.players[0].total_accuracy()
        accuracy2 = self.players[1].total_accuracy()
        if accuracy1 > accuracy2:
            return self.players[0]
        if accuracy2 > accuracy1:
            return self.players[1]
        return "DRAW"

    def change_state(self, new_state):
        """Set a stage and reset any timer or canvas associated with it."""
        self.current_state = new_state

        if new_state == self.COUNTDOWN:
            self.countdown_timer = self.ROUND_COUNTDOWN_SECONDS
        elif new_state == self.DRAWING:
            self.canvas.set_ink(None)
        elif new_state == self.RESULTS:
            self.results_timer = self.RESULTS_SECONDS

    def _start_next_round(self):
        """Clear round-specific data and begin a new countdown."""
        self.round_number += 1
        self.pending_spells = [None, None]
        self.current_player_index = 0
        self.last_hp_changes = (0.0, 0.0)
        self.change_state(self.COUNTDOWN)

    def reset_match(self):
        """Start a fresh match while retaining the loaded recognition templates."""
        self.players = [
            Player("Player 1", self.STARTING_HP, self.STARTING_HP),
            Player("Player 2", self.STARTING_HP, self.STARTING_HP),
        ]
        self.pending_spells = [None, None]
        self.current_player_index = 0
        self.round_number = 1
        self.countdown_timer = self.ROUND_COUNTDOWN_SECONDS
        self.results_timer = self.RESULTS_SECONDS
        self.winner = None
        self.last_hp_changes = (0.0, 0.0)
        self.canvas.clear()
        self.canvas.set_ink(None)
        self.current_state = self.COUNTDOWN

    def draw(self):
        """Delegate presentation to Arena based on the current game stage."""
        self.arena.draw_arena(self.players, self.round_number)

        if self.current_state == self.COUNTDOWN:
            self.arena.draw_countdown(self.countdown_timer, self.round_number)

        elif self.current_state == self.DRAWING:
            self.arena.draw_drawing(
                self.players,
                self.players[self.current_player_index],
                self.canvas,
                self.round_number,
            )

        elif self.current_state == self.HANDOFF:
            self.arena.draw_handoff(self.players[1])

        elif self.current_state == self.RESULTS:
            self.arena.draw_results(
                self.players,
                self.pending_spells,
                self.last_hp_changes,
                self.round_number,
            )

        elif self.current_state == self.GAME_OVER:
            self.arena.draw_game_over(
                self.winner,
                self.players,
                self.pending_spells,
                self.last_hp_changes,
                self.round_number,
            )
