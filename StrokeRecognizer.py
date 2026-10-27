'''StrokeRecognizer implements the $1 Unistroke Recognizer. Stateless apart from its templates.
State templates (9 point lists mapped to element and type), num_resample_points, fizzle_threshold (0.5)
Behaviors load_templates(path), resample(points), normalize(points), recognize(points) → Spell
'''

import json
import math
from pathlib import Path

from Spell import Spell


Point = tuple[float, float]


class StrokeRecognizer:
    NUM_POINTS = 64
    SQUARE_SIZE = 250.0
    FIZZLE_THRESHOLD = 0.50
    SPELL_FIZZLE_THRESHOLDS = {
        "WIND": 0.48,
    }
    ANGLE_RANGE = math.radians(45.0)
    ANGLE_PRECISION = math.radians(2.0)
    INK_SPELLS = {
        "RED": ("FIRE", "ATTACK"),
        "GRAY": ("WIND", "BLOCK"),
        "BROWN": ("EARTH", "HEAL"),
    }

    def __init__(self, template_path=None):
        if template_path is None:
            template_path = (
                Path(__file__).resolve().parent
                / "templates"
                / "spell_templates.json"
            )

        self.templates = []
        self.load_templates(template_path)

    @staticmethod
    def _distance(a: Point, b: Point) -> float:
        return math.hypot(b[0] - a[0], b[1] - a[1])

    @classmethod
    def _path_length(cls, points: list[Point]) -> float:
        return sum(
            cls._distance(points[i - 1], points[i])
            for i in range(1, len(points))
        )

    @staticmethod
    def _centroid(points: list[Point]) -> Point:
        return (
            sum(point[0] for point in points) / len(points),
            sum(point[1] for point in points) / len(points),
        )

    @classmethod
    def _resample(cls, points: list[Point]) -> list[Point]:
        if len(points) < 2:
            raise ValueError("A stroke needs at least two points.")

        total_length = cls._path_length(points)
        if total_length == 0:
            raise ValueError("A stroke must move; all points are identical.")

        interval = total_length / (cls.NUM_POINTS - 1)
        result = [points[0]]
        segment_index = 1
        distance_at_segment_start = 0.0

        for point_number in range(1, cls.NUM_POINTS - 1):
            target_distance = point_number * interval

            while segment_index < len(points):
                start = points[segment_index - 1]
                end = points[segment_index]
                segment_length = cls._distance(start, end)

                if segment_length == 0:
                    segment_index += 1
                    continue

                distance_at_segment_end = (
                    distance_at_segment_start + segment_length
                )

                if distance_at_segment_end >= target_distance:
                    fraction = (
                        target_distance - distance_at_segment_start
                    ) / segment_length
                    interpolated = (
                        start[0] + fraction * (end[0] - start[0]),
                        start[1] + fraction * (end[1] - start[1]),
                    )
                    result.append(interpolated)
                    break

                distance_at_segment_start = distance_at_segment_end
                segment_index += 1
            else:
                result.append(points[-1])

        result.append(points[-1])
        return result

    @classmethod
    def _rotate_by(cls, points: list[Point], angle: float) -> list[Point]:
        center_x, center_y = cls._centroid(points)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        rotated = []

        for x, y in points:
            dx = x - center_x
            dy = y - center_y
            rotated.append((
                dx * cos_angle - dy * sin_angle + center_x,
                dx * sin_angle + dy * cos_angle + center_y,
            ))

        return rotated

    @classmethod
    def _scale_to_square(cls, points: list[Point]) -> list[Point]:
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)

        scale_x = cls.SQUARE_SIZE / width if width > 0 else 1.0
        scale_y = cls.SQUARE_SIZE / height if height > 0 else 1.0

        return [
            (x * scale_x, y * scale_y)
            for x, y in points
        ]

    @classmethod
    def _translate_to_origin(cls, points: list[Point]) -> list[Point]:
        center_x, center_y = cls._centroid(points)
        return [
            (x - center_x, y - center_y)
            for x, y in points
        ]

    @classmethod
    def _normalize(cls, points: list[Point]) -> list[Point]:
        resampled = cls._resample(points)

        center_x, center_y = cls._centroid(resampled)
        first_x, first_y = resampled[0]
        indicative_angle = math.atan2(
            first_y - center_y,
            first_x - center_x,
        )

        rotated = cls._rotate_by(resampled, -indicative_angle)
        scaled = cls._scale_to_square(rotated)
        return cls._translate_to_origin(scaled)

    @classmethod
    def _path_distance(
        cls,
        points_a: list[Point],
        points_b: list[Point],
    ) -> float:
        return sum(
            cls._distance(a, b)
            for a, b in zip(points_a, points_b)
        ) / len(points_a)

    @classmethod
    def _is_spiral(cls, points: list[Point]) -> bool:
        resampled = cls._resample(points)
        center_x, center_y = cls._centroid(resampled)
        radii = [
            math.hypot(x - center_x, y - center_y)
            for x, y in resampled
        ]
        angles = [
            math.atan2(y - center_y, x - center_x)
            for x, y in resampled
        ]

        winding = sum(
            (current - previous + math.pi) % (2 * math.pi) - math.pi
            for previous, current in zip(angles, angles[1:])
        )
        mean_radius = sum(radii) / len(radii)
        radial_range = (
            (max(radii) - min(radii)) / mean_radius
            if mean_radius
            else 0.0
        )

        return (
            abs(winding) >= 0.60 * 2 * math.pi
            and radial_range >= 0.50
        )

    @classmethod
    def _distance_at_angle(
        cls,
        points: list[Point],
        template: list[Point],
        angle: float,
    ) -> float:
        rotated = cls._rotate_by(points, angle)
        return cls._path_distance(rotated, template)

    @classmethod
    def _distance_at_best_angle(
        cls,
        points: list[Point],
        template: list[Point],
    ) -> float:
        left = -cls.ANGLE_RANGE
        right = cls.ANGLE_RANGE
        ratio = (math.sqrt(5.0) - 1.0) / 2.0

        x1 = right - ratio * (right - left)
        x2 = left + ratio * (right - left)
        f1 = cls._distance_at_angle(points, template, x1)
        f2 = cls._distance_at_angle(points, template, x2)

        while abs(right - left) > cls.ANGLE_PRECISION:
            if f1 < f2:
                right = x2
                x2 = x1
                f2 = f1
                x1 = right - ratio * (right - left)
                f1 = cls._distance_at_angle(points, template, x1)
            else:
                left = x1
                x1 = x2
                f1 = f2
                x2 = left + ratio * (right - left)
                f2 = cls._distance_at_angle(points, template, x2)

        return min(f1, f2)

    def load_templates(self, path):
        file_path = Path(path)
        data = json.loads(file_path.read_text(encoding="utf-8"))

        if not isinstance(data, list) or not data:
            raise ValueError("The template file must contain a non-empty list.")

        loaded = []
        for item in data:
            element = item["element"].upper()
            spell_type = item["spell_type"].upper()
            points = [
                (float(point[0]), float(point[1]))
                for point in item["points"]
            ]

            if len(points) < 2:
                raise ValueError(
                    f"Template {element} {spell_type} needs at least two points."
                )

            loaded.append((
                element,
                spell_type,
                self._normalize(points),
            ))

        self.templates = loaded

    def recognize(self, points, ink=None) -> Spell:
        if ink is None:
            candidate_templates = self.templates
        else:
            ink_color = ink.upper()
            if ink_color not in self.INK_SPELLS:
                raise ValueError(f"Unknown ink color: {ink}")
            element, spell_type = self.INK_SPELLS[ink_color]
            candidate_templates = [
                template
                for template in self.templates
                if template[:2] == (element, spell_type)
            ]

        if len(points) < 2 or self._path_length(points) == 0:
            return Spell("UNKNOWN", "UNKNOWN", 0.0, True)

        if not candidate_templates:
            raise RuntimeError("No matching spell templates have been loaded.")

        normalized = self._normalize([
            (float(x), float(y))
            for x, y in points
        ])

        best_distance = float("inf")
        best_element = None
        best_spell_type = None

        for element, spell_type, template in candidate_templates:
            distance = self._distance_at_best_angle(normalized, template)
            if distance < best_distance:
                best_distance = distance
                best_element = element
                best_spell_type = spell_type

        half_diagonal = (
            0.5 * math.hypot(self.SQUARE_SIZE, self.SQUARE_SIZE)
        )
        score = max(0.0, min(1.0, 1.0 - best_distance / half_diagonal))
        threshold = self.SPELL_FIZZLE_THRESHOLDS.get(
            best_element,
            self.FIZZLE_THRESHOLD,
        )
        fizzled = score < threshold
        if best_element == "WIND" and not self._is_spiral([
            (float(x), float(y))
            for x, y in points
        ]):
            fizzled = True

        return Spell(best_element, best_spell_type, score, fizzled)