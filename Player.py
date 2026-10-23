class Player:

    box = pygame.rect(15,15)
    HP = 20

    def take_damage(amount):
        HP -= amount

    def heal(amount):
        HP += amount
