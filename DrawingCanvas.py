"""
Provides the DrawingCanvas class responsible for capturing and displaying mouse strokes
on a parchment-like area within the game.
"""

import pygame


class DrawingCanvas:
    """Capture and display one mouse stroke on a parchment area."""

    INK_COLORS = {
        "RED": (185, 45, 45),
        "GRAY": (95, 95, 95),
        "BROWN": (110, 62, 35),
    }

    def __init__(
        self,
        canvas_rect,
        cast_button_rect,
        clear_button_rect=None,
        parchment=None,
    ):
        # Rectangles let us test whether mouse clicks are inside the canvas or buttons.
        self.canvas_rect = pygame.Rect(canvas_rect)
        self.cast_button_rect = pygame.Rect(cast_button_rect)
        self.clear_button_rect = (
            pygame.Rect(clear_button_rect)
            if clear_button_rect is not None
            else None
        )

        # Store mouse positions in order; these points will later go to the recognizer.
        self.points = []
        self.is_drawing = False

        # These flags remember where a button press began until the mouse is released.
        self._cast_pressed = False
        self._clear_pressed = False
        self._ink_pressed = None
        self.selected_ink = None
        ink_width = (self.canvas_rect.width - 20) // 3
        ink_y = self.canvas_rect.top - 36
        self.ink_buttons = {
            ink: pygame.Rect(
                self.canvas_rect.left + index * (ink_width + 10),
                ink_y,
                ink_width,
                28,
            )
            for index, ink in enumerate(self.INK_COLORS)
        }

        # The parchment is an optional already-loaded Pygame image (Surface).
        self.parchment = parchment
        if self.parchment is not None:
            self.parchment = pygame.transform.smoothscale(
                self.parchment,
                self.canvas_rect.size,
            )

    def _append_point(self, position):
        # Convert screen coordinates to integer pixels and skip adjacent duplicates.
        point = (int(position[0]), int(position[1]))
        if not self.points or point != self.points[-1]:
            self.points.append(point)

    def handle_mouse(self, event):
        """Process one Pygame event; return True when a stroke is submitted."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for ink, button_rect in self.ink_buttons.items():
                if button_rect.collidepoint(event.pos):
                    self._ink_pressed = ink
                    return False

            # Remember button presses; activation happens on release over that button.
            if self.cast_button_rect.collidepoint(event.pos):
                self._cast_pressed = True
                return False

            if (
                self.clear_button_rect is not None
                and self.clear_button_rect.collidepoint(event.pos)
            ):
                self._clear_pressed = True
                return False

            # Start a new stroke only inside the canvas and when no stroke is present.
            if (
                self.selected_ink is not None
                and self.canvas_rect.collidepoint(event.pos)
                and not self.points
            ):
                self._append_point(event.pos)
                self.is_drawing = True
            return False

        if event.type == pygame.MOUSEMOTION and self.is_drawing:
            if self.canvas_rect.collidepoint(event.pos):
                # Add each point as the held mouse moves across the canvas.
                self._append_point(event.pos)
            else:
                # End capture at the canvas edge so outside movement is not part of the spell.
                self.is_drawing = False
            return False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_drawing:
                # Save the release position too, then finish the stroke.
                if self.canvas_rect.collidepoint(event.pos):
                    self._append_point(event.pos)
                self.is_drawing = False

            if self._ink_pressed is not None:
                ink = self._ink_pressed
                self._ink_pressed = None
                if self.ink_buttons[ink].collidepoint(event.pos):
                    self.set_ink(ink)
                return False

            if self._clear_pressed:
                # Clear only when the click both starts and ends on the Clear button.
                should_clear = (
                    self.clear_button_rect is not None
                    and self.clear_button_rect.collidepoint(event.pos)
                )
                self._clear_pressed = False
                if should_clear:
                    self.clear()
                return False

            if self._cast_pressed:
                # A Cast click is accepted only for a finished stroke with movement.
                should_cast = self.cast_button_rect.collidepoint(event.pos)
                self._cast_pressed = False
                return (
                    should_cast
                    and len(self.points) >= 2
                    and not self.is_drawing
                    and self.selected_ink is not None
                )

        return False

    def get_stroke(self):
        # Return a copy so callers cannot accidentally change the canvas's own points.
        return self.points.copy()

    def clear(self):
        # Remove the current drawing and reset any unfinished mouse interaction.
        self.points.clear()
        self.is_drawing = False
        self._cast_pressed = False
        self._clear_pressed = False
        self._ink_pressed = None

    def set_ink(self, ink):
        if ink is not None and ink not in self.INK_COLORS:
            raise ValueError(f"Unknown ink color: {ink}")
        if ink != self.selected_ink:
            self.selected_ink = ink
            self.clear()

    def draw(self, surface, font=None):
        if font is None:
            font = pygame.font.Font(None, 28)

        for ink, button_rect in self.ink_buttons.items():
            pygame.draw.rect(
                surface,
                self.INK_COLORS[ink],
                button_rect,
                border_radius=5,
            )
            border_color = (
                (255, 232, 175)
                if ink == self.selected_ink
                else (72, 56, 42)
            )
            pygame.draw.rect(
                surface,
                border_color,
                button_rect,
                width=3 if ink == self.selected_ink else 1,
                border_radius=5,
            )
            label = f"{ink.capitalize()} Ink"
            self._draw_button_label(surface, button_rect, label, font)

        # Draw either the supplied parchment image or a plain parchment-colored panel.
        if self.parchment is not None:
            surface.blit(self.parchment, self.canvas_rect)
        else:
            pygame.draw.rect(surface, (232, 214, 174), self.canvas_rect)

        # Clip the ink to the parchment so strokes cannot draw over the rest of the UI.
        previous_clip = surface.get_clip()
        surface.set_clip(self.canvas_rect)

        # The selected ink controls both the visible stroke and spell family.
        ink_color = self.INK_COLORS.get(self.selected_ink, (35, 29, 22))
        if len(self.points) >= 2:
            # Connect recorded points in order to render the user's stroke.
            pygame.draw.lines(
                surface,
                ink_color,
                False,
                self.points,
                5,
            )
        elif self.points:
            # Show a dot for a click that has not moved yet.
            pygame.draw.circle(
                surface,
                ink_color,
                self.points[0],
                3,
            )

        # Restore the previous clipping region so later UI drawing is unaffected.
        surface.set_clip(previous_clip)

        # Outline the drawing area.
        pygame.draw.rect(
            surface,
            (92, 63, 38),
            self.canvas_rect,
            width=2,
        )

        # Show Cast as available only after a stroke has ended and has multiple points.
        cast_ready = len(self.points) >= 2 and not self.is_drawing
        cast_color = (80, 145, 90) if cast_ready else (120, 120, 120)
        pygame.draw.rect(surface, cast_color, self.cast_button_rect)
        self._draw_button_label(surface, self.cast_button_rect, "Cast", font)

        if self.clear_button_rect is not None:
            # Draw Clear only when a clear button rectangle was provided.
            pygame.draw.rect(
                surface,
                (130, 85, 65),
                self.clear_button_rect,
            )
            self._draw_button_label(
                surface,
                self.clear_button_rect,
                "Clear",
                font,
            )

    @staticmethod
    def _draw_button_label(surface, button_rect, label, font):
        # Use the caller's font, or a default Pygame font for a simple standalone canvas.
        if font is None:
            font = pygame.font.Font(None, 28)
        text = font.render(label, True, (255, 255, 255))
        surface.blit(text, text.get_rect(center=button_rect.center))
