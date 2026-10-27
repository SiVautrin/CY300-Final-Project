'''CombatResolver: owns all spell-interaction logic and the editable rules table.
State: element_chart (which element beats which), multipliers table (attack, block, and heal values for win, neutral, and lose), base values
Behaviors: compare_elements(e1, e2), resolve(spell1, spell2) -> HP changes for each player
'''
from Spell import Spell


class CombatResolver:

    ELEMENT_CHART = {
        "FIRE": "EARTH",
        "WIND": "FIRE",
        "EARTH": "WIND"
    }

    # BLOCK values are the fraction of incoming damage let through, not effect strength.
    MULTIPLIERS = {
        "ATTACK": {"WIN": 3.0, "NEUTRAL": 3.0, "LOSE": 1.5},
        "BLOCK": {"WIN": 0.0, "NEUTRAL": 0.5, "LOSE": 0.5},
        "HEAL": {"WIN": 6.0, "NEUTRAL": 0.0, "LOSE": 0.0}
    }

    # The plan does not specify base attack damage; 10 HP is the current tuning choice.
    BASE_ATTACK_DAMAGE = 10.0

    def compare_elements(self, e1: str, e2: str) -> str:
        """Return the matchup from e1's perspective: WIN, NEUTRAL, or LOSE."""
        if e1 == e2:
            return "NEUTRAL"
        if self.ELEMENT_CHART.get(e1) == e2:
            return "WIN"
        return "LOSE"

    def get_multipliers(self, spell1: Spell, spell2: Spell) -> tuple[float, float]:
        """Return each spell's table value from its own elemental perspective."""
        result1 = self.compare_elements(spell1.element, spell2.element)
        result2 = self.compare_elements(spell2.element, spell1.element)
        return (
            self.MULTIPLIERS[spell1.spell_type][result1],
            self.MULTIPLIERS[spell2.spell_type][result2]
        )

    def _resolve_unopposed(self, spell: Spell, player_index: int) -> tuple[float, float]:
        """Resolve a single spell neutrally when the opposing spell fizzles."""
        if spell.spell_type == "ATTACK":
            damage = self.BASE_ATTACK_DAMAGE * self.MULTIPLIERS["ATTACK"]["NEUTRAL"] * spell.accuracy
            return (0.0, -damage) if player_index == 0 else (-damage, 0.0)
        if spell.spell_type == "HEAL":
            healing = self.MULTIPLIERS["HEAL"]["NEUTRAL"] * spell.accuracy
            return (healing, 0.0) if player_index == 0 else (0.0, healing)
        return 0.0, 0.0

    def resolve(self, spell1: Spell, spell2: Spell) -> tuple[float, float]:
        """Return (player 1 HP change, player 2 HP change)."""
        fizzled1 = spell1.is_fizzle()
        fizzled2 = spell2.is_fizzle()

        if fizzled1 and fizzled2:
            return 0.0, 0.0
        if fizzled1:
            return self._resolve_unopposed(spell2, 1)
        if fizzled2:
            return self._resolve_unopposed(spell1, 0)

        outcome1, outcome2 = self.get_multipliers(spell1, spell2)
        hp_change1 = 0.0
        hp_change2 = 0.0

        if spell1.spell_type == "ATTACK" and spell2.spell_type == "ATTACK":
            hp_change1 = -self.BASE_ATTACK_DAMAGE * outcome2 * spell2.accuracy
            hp_change2 = -self.BASE_ATTACK_DAMAGE * outcome1 * spell1.accuracy

        elif spell1.spell_type == "ATTACK" and spell2.spell_type == "BLOCK":
            damage = self.BASE_ATTACK_DAMAGE * outcome1 * spell1.accuracy
            # Lower block accuracy moves damage let through toward 1; full accuracy reaches the plan's table value.
            damage_let_through = outcome2 + (1.0 - spell2.accuracy) * (1.0 - outcome2)
            hp_change2 = -damage * damage_let_through

        elif spell1.spell_type == "BLOCK" and spell2.spell_type == "ATTACK":
            damage = self.BASE_ATTACK_DAMAGE * outcome2 * spell2.accuracy
            # Lower block accuracy moves damage let through toward 1; full accuracy reaches the plan's table value.
            damage_let_through = outcome1 + (1.0 - spell1.accuracy) * (1.0 - outcome1)
            hp_change1 = -damage * damage_let_through

        if spell1.spell_type == "HEAL":
            hp_change1 += outcome1 * spell1.accuracy
        if spell2.spell_type == "HEAL":
            hp_change2 += outcome2 * spell2.accuracy

        return hp_change1, hp_change2


# Previous implementation retained for reference:
# from Spell import Spell
#
# class CombatResolver:
#
#     # Defines which element beats which element
#     ELEMENT_CHART = {
#         "FIRE": "EARTH",# FIRE beats EARTH
#         "WIND": "FIRE", # WIND beats FIRE
#         "EARTH": "WIND" # EARTH beats WIND
#     }
#
#     # Multipliers for different spell types based on the outcome of the element comparison
#     MULTIPLIERS = {
#         "ATTACK": {"WIN": 1.0, "NEUTRAL": 1.0, "LOSE": 0.5},
#         "BLOCK": {"WIN": 2, "NEUTRAL": 1.5, "LOSE": 1.0},
#         "HEAL": {"WIN": 2.0, "NEUTRAL": 0.0, "LOSE": 0.0}
#     }
#
#     # Base values for different spell types
#     BASE_VALUES = {
#         "ATTACK": -10.0,
#         "BLOCK": 5.0,
#         "HEAL": 8.0
#     }
#
#     # Compares two elements and returns the result from the perspective of the first element: "WIN", "LOSE", or "NEUTRAL"
#     def compare_elements(self, e1: str, e2: str) -> str:
#         if e1 == e2:
#             return "NEUTRAL"
#         elif self.ELEMENT_CHART.get(e1) == e2:
#             return "WIN"
#         else:
#             return "LOSE"
#
#     # Resolves the outcome of two spells and returns the resulting multipliers for each player.
#     def get_multipliers(self, spell1: Spell, spell2: Spell) -> tuple:
#         element_result = self.compare_elements(spell1.element, spell2.element)
#         type1 = spell1.spell_type
#         type2 = spell2.spell_type
#         result1 = self.MULTIPLIERS[type1][element_result]
#         result2 = self.MULTIPLIERS[type2]["WIN" if element_result == "LOSE" else "LOSE" if element_result == "WIN" else "NEUTRAL"]
#         return result1, result2
#
#     # Resolves the outcome of two spells, based on types, and returns the health updates for two players
#     def resolve(self, spell1: Spell, spell2: Spell) -> tuple:
#         if spell1.is_fizzle() and spell2.is_fizzle():
#             return 0.0, 0.0
#         elif spell1.is_fizzle():
#             return -self.get_multipliers(spell2, spell1)[1], 0.0
#         elif spell2.is_fizzle():
#             return 0.0, -self.get_multipliers(spell1, spell2)[0]
#
#         multipliers1, multipliers2 = self.get_multipliers(spell1, spell2)
#         result1 = multipliers1 * self.BASE_VALUES[spell1.spell_type]
#         result2 = multipliers2 * self.BASE_VALUES[spell2.spell_type]
#         if spell1.spell_type == "BLOCK" and spell2.spell_type == "ATTACK":
#             result1 = result1 + result2
#         elif spell2.spell_type == "BLOCK" and spell1.spell_type == "ATTACK":
#             result2 = result2 + result1
#         return result1, result2
