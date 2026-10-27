'''Player: holds one player's state and applies HP changes.
State: name, hp, max_hp, player_icon, hp_icon, accuracy_history
Behaviors: take_damage(amount), heal(amount), record_accuracy(score), is_defeated(), total_accuracy()
'''

class Player:

    def __init__(self, name: str, max_hp: int, hp: int, player_icon: str = None, hp_icon: str = None) -> None:
        self.name = name
        self.max_hp = max_hp
        self.hp = hp
        self.player_icon = player_icon # Icon representing the player | NOT MVP
        self.hp_icon = hp_icon # Icon representing the player's | HP NOT MVP
        self.accuracy_history = []

    # Reduces the player's HP by the specified amount, not going below 0
    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    # Increases the player's HP by the specified amount, not exceeding max_hp
    def heal(self, amount: int) -> None:
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    # Records the accuracy score of the player's action
    def record_accuracy(self, score: float) -> None:
        self.accuracy_history.append(score)

    # Returns True if the player is defeated (HP <= 0), False otherwise
    def is_defeated(self) -> bool:
        return self.hp <= 0

    # Returns the total accuracy score accumulated by the player
    def total_accuracy(self) -> float:
        return sum(self.accuracy_history)
