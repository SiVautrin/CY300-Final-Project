'''Spell: a plain data object describing one cast spell.
State: element (FIRE / WIND / EARTH), spell_type (ATTACK / BLOCK / HEAL), accuracy, fizzled
Behaviors: is_fizzle(), name() (e.g., returns "Fire Attack")
'''

class Spell:

    def __init__(self, element: str, spell_type: str, accuracy: float, fizzled: bool):
        self.element = element # FIRE / WIND / EARTH
        self.spell_type = spell_type # ATTACK / BLOCK / HEAL
        self.accuracy = accuracy
        self.fizzled = fizzled

    # Returns True if the spell fizzled, False otherwise
    def is_fizzle(self) -> bool:
        return self.fizzled

    # Returns the display name of the spell (e.g., "Fire Attack")
    def name(self) -> str:
        return f"{self.element.capitalize()} {self.spell_type.capitalize()}"