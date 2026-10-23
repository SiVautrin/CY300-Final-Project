'''Class of spells and their basic properties'''
class Spell:

    spell_type: str | None = None
    attack: float = 1.0
    block: float = 1.0
    heal: float = 0


class Fire(Spell):

    spell_type: str = 'fire'
    strength: str = 'earth'
    weakness: str = 'wind'

    def fire_attack(self, opponent_spell: Spell) -> float:
        opponent_spell_type = opponent_spell.spell_type
        damage = self.attack

        if opponent_spell_type == self.strength:
            damage *= 2
        elif opponent_spell_type == self.weakness:
            damage *= 0.5

        return damage

    def fire_block(self, opponent_spell: Spell) -> float:
        opponent_spell_type = opponent_spell.spell_type
        block = self.block

        if opponent_spell_type == self.strength:
            block *= 0
        elif opponent_spell_type == self.weakness:
            block *= 0.5

        return block

    def fire_heal(self, opponent_spell: Spell) -> float:
        if opponent_spell.spell_type == self.strength:
            return 2.0
        return self.heal

class Wind(Spell):

    spell_type: str = 'wind'
    strength: str = 'fire'
    weakness: str = 'earth'

    def wind_attack(self, opponent_spell: Spell) -> float:
        opponent_spell_type = opponent_spell.spell_type
        damage = self.attack

        if opponent_spell_type == self.strength:
            damage *= 2
        elif opponent_spell_type == self.weakness:
            damage *= 0.5

        return damage

    def wind_block(self, opponent_spell: Spell) -> float:
        opponent_spell_type = opponent_spell.spell_type
        block = self.block

        if opponent_spell_type == self.strength:
            block *= 0
        elif opponent_spell_type == self.weakness:
            block *= 0.5

        return block

    def wind_heal(self, opponent_spell: Spell) -> float:
        if opponent_spell.spell_type == self.strength:
            return 2.0
        return self.heal

class Earth(Spell):

    spell_type: str = 'fire'
    strength: str = 'earth'
    weakness: str = 'wind'

    def earth_attack(self, opponent_spell: Spell) -> float:
        opponent_spell_type = opponent_spell.spell_type
        damage = self.attack

        if opponent_spell_type == self.strength:
            damage *= 2
        elif opponent_spell_type == self.weakness:
            damage *= 0.5

        return damage

    def earth_block(self, opponent_spell: Spell) -> float:
        opponent_spell_type = opponent_spell.spell_type
        block = self.block

        if opponent_spell_type == self.strength:
            block *= 0
        elif opponent_spell_type == self.weakness:
            block *= 0.5

        return block

    def earth_heal(self, opponent_spell: Spell) -> float:
        if opponent_spell.spell_type == self.strength:
            return 2.0
        return self.heal